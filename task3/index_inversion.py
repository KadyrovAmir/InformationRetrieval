from task1.data_retrieval import Article
from nltk.corpus import stopwords
import re, string, uuid
from nltk.stem.snowball import RussianStemmer
from peewee import *

pg_db = PostgresqlDatabase('stopgame', user='postgres', password='postgres',
                           host='localhost', port=5432)

class TermsList(Model):
    term_id = UUIDField(primary_key=True)
    term_text = CharField(unique=True, max_length=64)

    class Meta:
        database = pg_db
        db_table = 'terms_list'

class ArticleTerm(Model):
    article_id = ForeignKeyField(Article, to_field='id', db_column='article_id')
    term_id = ForeignKeyField(TermsList, to_field='term_id', db_column='term_id')

    class Meta:
        database = pg_db
        db_table = 'article_term'

if __name__ == '__main__':
    TermsList.create_table()
    ArticleTerm.create_table()

    articles = Article.select()
    punctuation = string.punctuation + "«»—•’"

    porter = RussianStemmer()

    stop = stopwords.words('russian')
    terms = {}

    for article in articles:
        text = " ".join([article.title.lower(), article.content.lower(), article.keywords.lower()])
        for p in punctuation:
            text = text.replace(p, "")
        text = text.replace("\\n", "")
        text = re.sub(' +', ' ', text)

        text = [porter.stem(word) for word in text.split() if word not in stop]

        for word in text:
            if word in terms:
                if article.id not in terms[word]:
                    terms[word].append(article.id)
            else:
                terms[word] = [article.id]


    for word in terms.keys():
        article_ids = terms[word]
        term_id = uuid.uuid4()
        term = TermsList(term_id=term_id, term_text=word)
        term.save(force_insert=True)

        for article_single_id in article_ids:
            article_term = ArticleTerm(article_id=article_single_id, term_id=term_id)
            article_term.save(force_insert=True)
