import argparse
import re
from sqlite3 import IntegrityError
from types import FunctionType

import redis as redis
from bs4 import BeautifulSoup, Comment
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import database
import numpy as np
import gensim
from gensim import matutils
from models import Article
from utils import redis_db
import datetime

class Text(object):

    def __init__(self, raw):
        self.raw = raw

    #with warnings.catch_warnings():
    #    warnings.simplefilter("ignore", category=RuntimeWarning)

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

def clean_text(data):
    articles = []
    for article in data:
        text = Text(article['body'])
        article['clean_body'] = text.tags_removed()
        articles.append(article['clean_body'])
        #break
    return articles

class ArticleVector(object):
    def __init__(self, id, vector):
        self.id = id
        self.vector = vector

class SimilarityModel(object):

    AVAILABLE_MODELS = {'tfidf': 'tfidf_model'}

    def __init__(self, redis_db, data, model_type):
        self.redis_db = redis_db
        self.data = data
        self.model_type = model_type

    def get_model(self):
        try:
            create_model = getattr(self, '%s_model' % self.model_type)
            return create_model
        except AttributeError as ae:
            print 'Model %s does not exist' % self.model_type
            raise AttributeError

    def save(self, save_threshold = 0):
        # This learns the vocabulary and then generates a term-document matrix
        # The term-document matrix describes the frequency of terms that occur in a
        # collection of documents.
        create_model = self.get_model()
        model = create_model(self.data, save_threshold)

        # print tfidf.shape[0], " rows, ", tfidf.shape[1], " columns."
        # zero out tfidf's below threshold
        #model.data[:] = map(lambda x: x if x > save_threshold else 0, model.data) # model_type

        id2vector = {i: item[0] for i, item in zip(range(len(self.data)), self.data)}
        for i in range(model.shape[0]):
            current_article_id = id2vector[i]
            similarity_values = cosine_similarity(model[i:i + 1], model)[0]
            print 'Adding similarity values for %s' % str(current_article_id)
            for j, value in zip(range(len(similarity_values)), similarity_values):
                redis_db.zadd('%s:%s' % (self.model_type, current_article_id), value, id2vector[j])

    def tfidf_model(cls, data, save_threshold=0):
        id2vector = {i: item[0] for i, item in zip(range(len(data)), data)}
        model = TfidfVectorizer(stop_words='english').fit_transform(map(lambda x: x[1], data))
        model.data[:] = map(lambda x: x if x > save_threshold else 0, model.data)
        print model.shape[0], " rows, ", model.shape[1], " columns.", "len model.data", len(model.data)
        return model

    def article2vec_model(cls, data, save_threshold=0):
        id2vector = {i: item[0] for i, item in zip(range(len(data)), data)}
        articles_arr = map(lambda x: x[1].split(), data)
        w2v_model = gensim.models.Word2Vec(articles_arr, workers=4, min_count=1)
        final_model = []
        for k in range(0, len(articles_arr)):
            kth_article_vector = [w2v_model[word] for word in articles_arr[k]]
            final_model.append(ArticleVector(id2vector[k], matutils.unitvec(np.array(kth_article_vector).mean(axis=0))))
        return final_model


def main(args):
    if args.load_from is not None:
        parsed_articles = parse_csv(args.load_from)
        for parsed in parsed_articles:
            print "Storing parsed article %s" % parsed.article_id
            store(parsed)

    if args.build_model is not None:
        data = database.session.query(Article.article_id, Article.body).all()
        #data = map(lambda article: (article.article_id, article.body), parsed_articles)

        tfidf_sim_model = SimilarityModel(redis_db, data, args.build_model)
        #word2vec_sim_model = SimilarityModel(redis_db, data, 'article2vec')

        # saves model to redis
        tfidf_sim_model.save()
        #word2vec_sim_model.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--load_from', help='Load articles from CSV', action="store")
    parser.add_argument('--build_model', help='Build model of specified type (tfidf, word2vec etc)', action="store")

    args = parser.parse_args()
    main(args)