import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


class Database(object):
    def __init__(self, engine_name):
        self.engine = create_engine(engine_name, echo=False)
        Session = sessionmaker(bind=self.engine)
        Session.configure(bind=self.engine)
        self.session = Session()

database = Database('sqlite:///' + 'example')
Base.metadata.create_all(database.engine)
redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)
