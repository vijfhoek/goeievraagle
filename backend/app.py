from flask import Flask, jsonify, request
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from tqdm import tqdm
from beeprint import pp
import csv
import click

from .question import Question
from .question_search import QuestionSearch

app = Flask(__name__)

connections.create_connection(hosts=["localhost"])
Question.init()


@app.route("/api/")
def index():
    def round_sigfig(value, figures):
        return float(format(value, f".{figures}g"))

    query = request.args.get("q")
    categories = request.args.get("categories", None)

    facets = {}
    if categories is not None:
        category_list = categories.split(",")
        facets["category"] = category_list

    search = Search.from_dict({
        "query": {
            "query_string": {
                "query": query,
            },
        },
        "aggregations": {
            "category": {
                "terms": {"field": "category"},
            },
            "suggestions": {
                "significant_terms": {
                    "field": "body",
                    "mutual_information": {
                        "include_negatives": True,
                    },
                    "size": 40,
                },
            }
        },
    })

    response = search.execute()

    #date_facets = [{"timestamp": date.timestamp(), "count": count}
                   #for date, count, _ in response.facets.date_frequency]
    category_facets = [
        {"category": bucket.key, "count": round_sigfig(bucket.doc_count, 3)}
        for bucket in response.aggregations.category.buckets
    ]

    suggestions = [{"key": bucket.key, "count": bucket.doc_count}
                   for bucket in response.aggregations.suggestions.buckets]

    date_facets = []

    results = []
    for hit in response:
        summary = Question.summary(hit)
        url = Question.url(hit)

        results.append({
            "id": hit.meta.id, "score": hit.meta.score, "title": hit.title,
            "body": summary, "category": hit.category, "date": hit.date,
            "url": url,
        })

    return jsonify(
        facets={
            "months": date_facets,
            "categories": category_facets,
        },
        suggestions=suggestions,
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
