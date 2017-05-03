from utils import redis_db

def check_cache(model_type, article_id, n=100):
    similar = redis_db.zrange('%s:%s' % (model_type, str(article_id)), 0, int(n), withscores=True)
    print similar
    if len(similar) > 0:
        return similar
    return None
