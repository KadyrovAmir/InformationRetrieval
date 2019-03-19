from task5.searching_queries import preprocessing
from task3.index_inversion import TermsList
from task2.data_preprocessing import WordsPorter
from task4.tfidf import ArticleTerm
from task1.data_retrieval import Article
import math

N = 30


def calculate_idf(term):
    try:
        word_id = TermsList.select(TermsList.term_id).where(TermsList.term_text == term)
        x = ArticleTerm.select().where(ArticleTerm.term_id == word_id).count()
        idf = math.log((N - x + 0.5) / (x + 0.5))
        return idf
    except ZeroDivisionError:
        return 0


if __name__ == '__main__':
    query = "вчера разработчик всем сказал сделать"
    prep_words = preprocessing(query)

    k = 1.2
    b = 0.75

    articles = Article.select(Article.id)

    avg_dl = 0
    for article in articles:
        avg_dl += WordsPorter.select().where(WordsPorter.article_id == article).count()
    avg_dl = avg_dl / N

    score = {}

    for article in articles:
        local_dl = WordsPorter.select().where(WordsPorter.article_id == article).count()
        s = 0
        for word in prep_words:
            n_t = WordsPorter.select().where((WordsPorter.article_id == article) & (WordsPorter.term == word)).count()
            s += (calculate_idf(word) * (n_t * (k + 1))) / (n_t + k * (1 - b + b * (local_dl/avg_dl)))

        url = Article.get_by_id(article).url
        score[url] = s
    sorted_score = sorted(score.items(), key=lambda kv: kv[1], reverse=True)

    for i in range(10):
        url = sorted_score[i][0]
        score_value = sorted_score[i][1]
        print("{} — URL: {}, score = {} ".format(i + 1, url, score_value))