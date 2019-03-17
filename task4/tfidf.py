from collections import Counter
from task2.data_preprocessing import WordsPorter
from task1.data_retrieval import Article
from task3.index_inversion import TermsList
import uuid
from peewee import *
import math


pg_db = PostgresqlDatabase('stopgame', user='postgres', password='postgres',
                           host='localhost', port=5432)

class ArticleTerm(Model):
    article_id = ForeignKeyField(Article, to_field='id', db_column='article_id')
    term_id = ForeignKeyField(TermsList, to_field='term_id', db_column='term_id')
    tf_idf = FloatField()

    class Meta:
        database = pg_db
        primary_key = CompositeKey('article_id', 'term_id')
        db_table = 'article_term'

if __name__ == '__main__':
    words = WordsPorter.select()

    word_article_id = {}
    word_id = {}

    for word in words:
        if word.article_id not in word_article_id:
            word_article_id[word.article_id] = {}
        word_article_id[word.article_id][word.term] = word.id

    article_word = {}
    for word in words:
        t_id = TermsList.get(TermsList.term_text == word.term).term_id
        word_id[word.term] = t_id

        if word.article_id not in article_word:
            article_word[word.article_id] = [word.term]
        else:
            article_word[word.article_id].append(word.term)
    tf = {}
    # Compute TF
    for key in article_word.keys():
        local_tf = {}
        word_count = Counter(article_word[key])
        for word in word_count:
            local_tf[word] = word_count[word] / float(len(article_word[key]))
        tf[key] = local_tf

    word_article = {}
    for word in words:
        if word.term not in word_article:
            word_article[word.term] = [word.article_id]
        else:
            word_article[word.term].append(word.article_id)

    idf = {}
    # Compute IDF
    for word in word_article.keys():
        idf[word] = math.log10(len(tf.keys()) / len(word_article[word]))

    ArticleTerm.create_table()

    for article_id in tf.keys():
        for word in tf[article_id].keys():
            tf_idf = tf[article_id][word] * idf[word]
            article_term = ArticleTerm(article_id=article_id, term_id=word_id[word], tf_idf=tf_idf)
            article_term.save(force_insert=True)