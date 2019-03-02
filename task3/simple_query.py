from peewee import *
from nltk.corpus import stopwords
from nltk.stem.snowball import RussianStemmer
import string
from task3.index_inversion import TermsList, ArticleTerm
from task1.data_retrieval import Article

pg_db = PostgresqlDatabase('stopgame', user='postgres', password='postgres',
                           host='localhost', port=5432)


def preprocessing(sentence):
    porter = RussianStemmer()
    punctuation = string.punctuation + "«»—•’"
    stop = stopwords.words('russian')

    for p in punctuation:
        sentence = sentence.replace(p, "")
    sentence = [porter.stem(word) for word in sentence.split() if word not in stop]
    return sentence

def execute_query(text):
    preprocessed_text = preprocessing(text)
    word_articles = {}
    for word in preprocessed_text:
        articles_term = ArticleTerm.select().join(TermsList, on=(ArticleTerm.term_id == TermsList.term_id)).where(TermsList.term_text == word)
        articles_id = [ar_term.article_id for ar_term in articles_term]
        for ar_id in articles_id:
            try:
                article = Article.get(Article.id == ar_id)
                if word in word_articles:
                    word_articles[word].append(article.url)
                else:
                    word_articles[word] = [article.url]
            except DoesNotExist:
                word_articles[word] = []

    for word in word_articles.keys():
        word_articles[word] = set(word_articles[word])

    result = set.intersection(*word_articles.values())
    if len(result) == 0:
        print("По запросу '{}' не нашлось статей ".format(text))
    else:
        print("По запросу '{}' нашлись статьи: {}".format(text, result))

if __name__ == '__main__':
    texts = ['Слова программиста', 'Состоялся релиз игры', 'Выход игры был перенесён', 'Ведущий разработчик студии покинул команду']
    for sentence in texts:
        execute_query(sentence)