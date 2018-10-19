from datetime import datetime
from flask import Flask, jsonify, request
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, FacetedSearch, TermsFacet, DateHistogramFacet
from elasticsearch_dsl.connections import connections
from tqdm import tqdm
import csv
import click
import re

class Question(Document):
    title = Text(analyzer="snowball")
    body = Text(analyzer="snowball")
    category = Keyword()
    date = Date()

    class Index:
        name = "goeievraag"

    def save(self, **kwargs):
        return super(Question, self).save(**kwargs)

    @property
    def url(self):
        id_ = self.meta.id
        if not self.category:
            return f"https://www.startpagina.nl/v/vraag/{id_}"

        category = self.category.lower()
        category = re.sub("[^A-Za-z ]", "", category).replace("  ", "-")
        return f"https://www.startpagina.nl/v/{category}/vraag/{id_}"

    @property
    def summary(self, length=128):
        if len(self.body) > length:
            return self.body[:length - 3] + "..."

        return self.body



class QuestionSearch(FacetedSearch):
    doc_types = Question,
    fields = "category", "title", "body"

    facets = {
        "date_frequency": DateHistogramFacet(field="date", interval="month"),
        "category": TermsFacet(field="category")
    }

app = Flask(__name__)

connections.create_connection(hosts=["localhost"])
Question.init()

def round_sigfig(value, figures):
    return float(format(value, f".{figures}g"))

@app.route("/api/")
def index():
    query = request.args.get("q")
    categories = request.args.get("categories", None)

    facets = {}
    if categories is not None:
        category_list = categories.split(",")
        facets["category"] = category_list

    search = QuestionSearch(query, facets)

    response = search.execute()

    date_facets = [{"timestamp": date.timestamp(), "count": count}
                   for date, count, _ in response.facets.date_frequency]
    category_facets = [{"category": category, "count": round_sigfig(count, 3)}
                       for category, count, _ in response.facets.category]

    results = [{"id": hit.meta.id, "score": hit.meta.score, "title": hit.title,
                "body": hit.summary, "category": hit.category,
                "date": hit.date, "url": hit.url}
               for hit in response]

    return jsonify(
        facets={"months": date_facets, "categories": category_facets},
        results=results,
        hits=round_sigfig(response.hits.total, 4),
        took=response.took / 1000,
    )


@app.cli.command()
@click.argument("questions")
@click.argument("categories")
def import_data(questions, categories):
    categories_dict = {}
    num_lines = sum(1 for line in open(categories))
    with open(categories, newline="") as csv_file:
        reader = csv.reader(csv_file)
        for row in tqdm(reader, desc="Reading categories", total=num_lines):
            id_ = int(row[0])
            category = row[2]

            categories_dict[id_] = category

    num_lines = sum(1 for line in open(questions))
    with open(questions, newline="") as csv_file:
        reader = csv.reader(csv_file)

        it = tqdm(reader, desc="Reading questions", total=num_lines)
        for i, row in enumerate(it):
            try:
                id_ = int(row[0])
                category_id = int(row[3])

                question = Question(meta={"id": id_})

                question.date = row[1]
                question.category = categories_dict[category_id]
                question.title = row[4]
                question.body = "\n".join(row[5:])

                question.save()
            except (IndexError, ValueError):
                continue
