from scipy import sparse, matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import gensim
from gensim import matutils
from utils import redis_db

class SimilarityModel(object):

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
        id2vector = {i: item[0] for i, item in zip(range(len(self.data)), self.data)}
        for i in range(model.shape[0]):
            current_article_id = id2vector[i]
            similarity_values = cosine_similarity(model[i:i + 1], model)[0]
            print 'Adding similarity values for %s using model %s' % (str(current_article_id), self.model_type)
            for j, value in zip(range(len(similarity_values)), similarity_values):
                redis_db.zadd('%s:%s' % (self.model_type, current_article_id), value, id2vector[j])

    def tfidf_model(cls, data, save_threshold=0):
        model = TfidfVectorizer(stop_words='english').fit_transform(map(lambda x: x[1], data))

        # zero out tfidf's below threshold
        model.data[:] = map(lambda x: x if x > save_threshold else 0, model.data)

        print model.shape[0], " rows, ", model.shape[1], " columns.", "len model.data", len(model.data)
        return model

    def article2vec_model(cls, data, save_threshold=0):
        articles_arr = map(lambda x: x[1].split(), data)
        w2v_model = gensim.models.Word2Vec(articles_arr, workers=4, min_count=1)
        all_articles = []
        for k in range(0, len(articles_arr)):
            kth_article_vector = [w2v_model[word] for word in articles_arr[k]]
            if len(kth_article_vector) == 0:
                all_articles.append(np.zeros(np.array(all_articles[0]).shape))
            else:
                kth_article_vector = matutils.unitvec(np.array(kth_article_vector).mean(axis=0))
                all_articles.append(kth_article_vector)
        sparse_articles = sparse.csr_matrix(matrix(all_articles))
        return sparse_articles
