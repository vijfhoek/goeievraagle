from elasticsearch_dsl import FacetedSearch, TermsFacet, DateHistogramFacet
from .question import Question


class QuestionSearch(FacetedSearch):
    doc_types = Question,
    fields = "title", "body"

    facets = {
        "date_frequency": DateHistogramFacet(field="date", interval="month"),
        "category": TermsFacet(field="category"),
    }
