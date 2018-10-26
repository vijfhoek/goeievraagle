from flask import Flask, jsonify, request
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from elasticsearch.exceptions import NotFoundError
from tqdm import tqdm
from beeprint import pp
import csv
import click
import requests

from .question import Question

app = Flask(__name__)

connections.create_connection(hosts=["localhost"])
Question.init()


@app.route("/api/")
def index():
    def round_sigfig(value, figures):
        return float(format(value, f".{figures}g"))

    query = request.args.get("q")
    categories = request.args.get("categories", None)
    page = int(request.args.get("page", 1)) - 1

    search_dict = {
        "from": page * 10,
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": query}},
                ]
            }
        },
        "aggregations": {
            "category": {
                "terms": {"field": "category"},
            },
            "chips": {
                "significant_terms": {
                    "field": "body",
                    "mutual_information": {
                        "include_negatives": True,
                    },
                    "size": 40,
                },
            }
        },
    }

    if categories is not None:
        category_list = categories.split(",")
        search_dict["post_filter"] = {
            "terms": {"category": category_list},
        }

    search = Search.from_dict(search_dict)
    response = search.execute()
    pp(response.to_dict())

    category_facets = [
        {"category": bucket.key, "count": round_sigfig(bucket.doc_count, 3)}
        for bucket in response.aggregations.category.buckets
    ]

    chips = [{"key": bucket.key, "count": bucket.doc_count}
             for bucket in response.aggregations.chips.buckets]

    date_facets = []

    results = []
    for hit in response:
        summary = Question.summary(hit)
        url = Question.url(hit)

        try:
            dead = hit.dead
        except AttributeError:
            dead = False

        results.append({
            "id": hit.meta.id, "score": hit.meta.score, "title": hit.title,
            "body": summary, "category": hit.category, "date": hit.date,
            "url": url, "dead": dead,
        })

    return jsonify(
        facets={
            "months": date_facets,
            "categories": category_facets,
        },
        chips=chips,
        results=results,
        hits=round_sigfig(response.hits.total, 4),
        took=response.took / 1000,
    )


@app.cli.command()
@click.argument("questions")
@click.argument("categories")
@click.argument("answers")
def import_data(questions, categories, answers):
    categories_dict = {}
    num_lines = sum(1 for line in open(categories))
    with open(categories, newline="") as csv_file:
        reader = csv.reader(csv_file)
        for row in tqdm(reader, desc="Reading categories", total=num_lines):
            id_ = int(row[0])
            category = row[2]

            categories_dict[id_] = category

    if questions != "skip":
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

    if answers != "skip":
        with open(answers, newline="") as csv_file:
            reader = csv.reader(csv_file)

            it = tqdm(reader, desc="Reading answers")
            for i, row in enumerate(it):
                try:
                    question_id = int(row[3])
                    question = Question.get(id=question_id)
                    if question.answers is None:
                        question.answers = row[4]
                    else:
                        question.answers += "\n\n" + row[4]
                    question.save()
                except (IndexError, ValueError, NotFoundError):
                    continue


@app.cli.command()
def cleanup_database():
    dead_count = 0
    alive_count = 0

    for question in Question.search().scan():
        if question.dead is not None or question.error:
            print(end="_")
            dead_count += 1
            continue

        url = question.url()
        response = requests.head(url)

        if response.status_code == 404:
            dead_count += 1
            question.dead = True
            question.save()
            print(end=".")
        elif response.status_code == 302:
            alive_count += 1
            question.dead = False
            print(end="#")
        elif response.status_code == 500:
            question.error = True
            print(end="!")
        else:
            continue

        question.save()
