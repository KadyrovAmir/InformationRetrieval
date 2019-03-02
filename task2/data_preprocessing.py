from peewee import *
import string
import re
import uuid
from task1.data_retrieval import Article
from nltk.stem.snowball import RussianStemmer
from pymystem3 import Mystem
from nltk.corpus import stopwords

pg_db = PostgresqlDatabase('stopgame', user='postgres', password='postgres',
                           host='localhost', port=5432)

class WordsPorter(Model):
    id = UUIDField(primary_key=True)
    term = CharField(max_length=64)
    article_id = ForeignKeyField(Article, to_field='id', db_column='article_id')

    class Meta:
        database = pg_db
        db_table = 'words_porter'

class WordsMyStem(Model):
    id = UUIDField(primary_key=True)
    term = CharField(max_length=64)
    article_id = ForeignKeyField(Article, to_field='id', db_column='article_id')

    class Meta:
        database = pg_db
        db_table = 'words_mystem'

if __name__ == '__main__':
    articles = Article.select()
    punctuation = string.punctuation + "«»—•’"

    porter = RussianStemmer()
    mystem = Mystem()

    WordsMyStem.create_table()
    WordsPorter.create_table()

    stop = stopwords.words('russian')
    for article in articles:
        text = " ".join([article.title.lower(), article.content.lower(), article.keywords.lower()])
        for p in punctuation:
            text = text.replace(p, "")
        text = text.replace("\\n", "")
        text = re.sub(' +', ' ', text)

        text = [word for word in text.split() if word not in stop]
        text = " ".join(text)

        # Mystem
        mystem_words = mystem.lemmatize(text)

        raw_words = text.split()
        # Porter Stemmer
        porter_words = [porter.stem(word) for word in raw_words]

        for word in porter_words:
            data_porter = WordsPorter(id=uuid.uuid4(), term=word, article_id=article.id)
            data_porter.save(force_insert=True)

        for word in mystem_words:
            if word != ' ':
                data_mystem = WordsMyStem(id=uuid.uuid4(), term=word, article_id=article.id)
                data_mystem.save(force_insert=True)
