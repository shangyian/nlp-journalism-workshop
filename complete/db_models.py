from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'

    article_id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(String)
    published_date = Column(DateTime)
    url = Column(String)
    author = Column(String)
