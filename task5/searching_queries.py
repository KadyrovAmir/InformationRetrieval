import math, string
from task1.data_retrieval import Article
from task3.index_inversion import TermsList
from task4.tfidf import ArticleTerm
from nltk.stem.snowball import RussianStemmer
from peewee import *
from nltk.corpus import stopwords

pg_db = PostgresqlDatabase('stopgame', user='postgres', password='postgres',
                           host='localhost', port=5432)

N = 30

def preprocessing(sentence):
    porter = RussianStemmer()
    punctuation = string.punctuation + "«»—•’"
    stop = stopwords.words('russian')

    for p in punctuation:
        sentence = sentence.replace(p, "")
    sentence = [porter.stem(word) for word in sentence.split() if word not in stop]
    return sentence


def calculate_idf(term):
    try:
        word_id = TermsList.select(TermsList.term_id).where(TermsList.term_text == term)
        x = ArticleTerm.select().where(ArticleTerm.term_id == word_id).count()
        idf = math.log(N / x)
        return idf
    except ZeroDivisionError:
        return 0


def cos_measure(v1, v2):
    try:
        pairs = zip(v1, v2)
        num = sum(pair[0] * pair[1] for pair in pairs)
        den = math.sqrt(sum(a * a for a in v1)) * math.sqrt(sum(b * b for b in v2))
        return num / den
    except ZeroDivisionError:
        return 0


if __name__ == '__main__':
    query = "вчера разработчик всем сказал сделать"
    prep_words = preprocessing(query)

    query_vector = list(map(calculate_idf, prep_words))
    query_terms_id = []

    for prep_word in prep_words:
        query_terms_id.append(TermsList.get(TermsList.term_text == prep_word).term_id)

    docs_tfidf = {}

    for term_id in query_terms_id:
        article_terms = ArticleTerm.select().where(ArticleTerm.term_id == term_id)
        for article_term in article_terms:
            docs_tfidf[article_term.article_id] = []

    for article_id in docs_tfidf.keys():
        for term_id in query_terms_id:
            tfidf = ArticleTerm.select(ArticleTerm.tf_idf)\
                .where((ArticleTerm.article_id == article_id) & (ArticleTerm.term_id == term_id))
            if tfidf:
                docs_tfidf[article_id].append(tfidf[0].tf_idf)
            else:
                docs_tfidf[article_id].append(0)

    cos_meas = {}
    for doc in docs_tfidf.keys():
        vector = docs_tfidf[doc]
        cos_meas[doc] = cos_measure(query_vector, vector)

    sorted_cos_mes = sorted(cos_meas.items(), key=lambda kv: kv[1], reverse=True)

    for i in range(10):
        article_id = sorted_cos_mes[i][0]
        cos = sorted_cos_mes[i][1]
        print("{} — URL: {}, cos = {} ".format(i + 1, Article.get_by_id(article_id).url, cos))