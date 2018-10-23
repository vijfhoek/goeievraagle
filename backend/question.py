from elasticsearch_dsl import Document, Date, Keyword, Text


class Question(Document):
    title = Text(analyzer="snowball")
    body = Text(
        analyzer="snowball",
        fielddata=True,
    )
    category = Keyword()
    date = Date()

    class Index:
        name = "goeievraag"

    def save(self, **kwargs):
        return super(Question, self).save(**kwargs)

    def url(self):
        id_ = self.meta.id
        return f"https://www.startpagina.nl/v/vraag/{id_}/"

    def summary(self, length=128):
        if len(self.body) > length:
            return self.body[:length - 3] + "..."

        return self.body
