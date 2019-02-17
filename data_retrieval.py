from bs4 import BeautifulSoup
import requests
import uuid
import psycopg2
from peewee import *

page_links = ['https://stopgame.ru/news/all/p1', 'https://stopgame.ru/news/all/p2']
titles = []
texts = []
tags = []
hrefs = []

for page_link in page_links:
    page_response = requests.get(page_link, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")

    articles = page_content.find_all(class_='title lent-title')
    for article in articles:
        titles.append(article.a.get_text()) if (len(titles) < 30) else 0
        hrefs.append('https://stopgame.ru' + article.a.get('href'))

for link in hrefs:
    page_response = requests.get(link, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")

    text = page_content.find(class_='main_text')
    for tag in text.find_all('a'):
        tag.replaceWith('')
    texts.append(text.get_text())

    raw_tags = page_content.find(class_='tags')
    tags.append(raw_tags.get_text().replace(',', ';'))


pg_db = PostgresqlDatabase('stopgame', user='postgres', password='postgres',
                           host='localhost', port=5432)


class Students(Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=32)
    surname = CharField(max_length=32)
    mygroup = CharField(max_length=6)
    class Meta:
        database = pg_db
        db_table = 'students'


class Article(Model):
    id = UUIDField(primary_key=True)
    title = CharField(max_length=256)
    keywords = CharField(max_length=256)
    content = TextField()
    url = CharField(max_length=128)
    student_id = ForeignKeyField(Students, to_field='id', db_column='student_id')
    class Meta:
        database = pg_db
        db_table = 'articles'


Students.create_table()
Article.create_table()

my_id = uuid.uuid4()
me = Students(id=my_id, name='Амир',surname='Кадыров',mygroup='11-501')
me.save(force_insert=True)

for i in range(len(titles)):
    data = Article(id=uuid.uuid4(), title=titles[i], keywords=tags[i], content=texts[i],url=hrefs[i], student_id=my_id)
    data.save(force_insert=True)