import datetime
from sqlite3 import IntegrityError

import redis
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import Base, Article
from bs4 import BeautifulSoup, Comment

class Database(object):
    def __init__(self, engine_name):
        self.engine = create_engine(engine_name, echo=False)
        Session = sessionmaker(bind=self.engine)
        Session.configure(bind=self.engine)
        self.session = Session()

database = Database('sqlite:///' + 'example')
Base.metadata.create_all(database.engine)
redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

def tags_removed(raw):
    soup = BeautifulSoup(raw, 'html.parser')
    text = ""
    for t in soup.find_all(text=True):
        if isinstance(t, Comment):
            continue
        text += " %s" % unicode(t)
    text = " ".join(text.split()).strip().replace("\\n", "")
    re_html_comment = re.compile(r"(<!--.*?-->)")
    tags_removed = re_html_comment.sub("", text)
    return tags_removed

def parse_csv(file_name):
    handler = open(file_name)

    # first line is the header
    header = map(lambda h: h.strip(), handler.readline().split('\t'))

    articles = [{field: entry for field, entry in zip(header, row.split('\t'))} for row in handler]
    clean_articles = map(lambda article: Article(article_id=article['id'],\
                                                    title=unicode(article['title'] if article['title'] else " ", 'utf-8', errors='ignore'),\
                                                    author=unicode(article['author'], 'utf-8', errors='ignore'),\
                                                    published_date=datetime.datetime.strptime(article['published_date'], "%Y-%m-%d %H:%M:%S"),\
                                                    body=tags_removed(article['body']),\
                                                    url=article['slug'].strip()), articles)
    return clean_articles

def store(article):
    try:
        database.session.merge(article)
        database.session.commit()
    except IntegrityError:
        database.engine.execute(Article.update(). \
                       where(Article.article_id == id). \
                       values(article_id=article.article_id,\
                              title=article.title, \
                              body=article.body,
                              published_date=article.published_date, \
                              author=article.author, \
                              url=article.url))
        database.session.commit()
