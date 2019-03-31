import numpy as np
from numpy.linalg import svd

from task1.data_retrieval import Article
from task3.index_inversion import TermsList
from task4.tfidf import ArticleTerm
from task5.searching_queries import preprocessing, cos_measure


def get_needed_docs(terms_id):
    arr = []
    for term_id in terms_id:
        articles = ArticleTerm.select().where(ArticleTerm.term_id == term_id).distinct()
        for article in articles:
            arr.append(article.article_id)
    return arr

if __name__ == '__main__':
    query = "вчера разработчик всем сказал сделать"
    prep_words = preprocessing(query)

    query_terms_id = []
    for prep_word in prep_words:
        query_terms_id.append(TermsList.get(TermsList.term_text == prep_word).term_id)

    needed_docs = get_needed_docs(query_terms_id)
    needed_docs = list(set(needed_docs))

    matrix = []

    all_terms = TermsList.select(TermsList.term_id)

    for t in all_terms:
        term_count = []
        for doc in needed_docs:
            term_count.append(ArticleTerm.select().where((ArticleTerm.term_id == t) &(ArticleTerm.article_id == doc))
                              .count())
        matrix.append(term_count)

    query_vector = []
    for t in all_terms:
        query_flag_check = True
        for query_t in query_terms_id:
            if str(t) == str(query_t):
                query_vector.append(1)
                query_flag_check = False
                break
        if query_flag_check:
            query_vector.append(0)

    rank = 5

    U, S, V = svd(matrix, full_matrices=False)
    U = U[:, :rank]
    S = np.diag(S)
    S = S[:rank, :rank]
    V = np.transpose(V)[:, :rank]
    q = np.dot(np.dot(query_vector, U), np.linalg.inv(S))

    result = []
    for i in range(V.shape[0]):
        result.append((needed_docs[i], cos_measure(q, V[i])))

    result.sort(key=lambda x: x[1])
    sorted_lsi = list(reversed(result))[:10]

    print("Запрос: \"{}\" \nРейтинг ответов:".format(query))
    for i in range(10):
        url = sorted_lsi[i][0]
        cos = sorted_lsi[i][1]
        print("{} — URL: {}, lsi = {} ".format(i + 1, Article.get_by_id(url).url, cos))