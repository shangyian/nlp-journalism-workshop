#!flask/bin/python
from flask import Flask
from flask.json import jsonify
from utils import database, redis_db
from db_models import Article

app = Flask(__name__)

def single_article_json(article_id, fields=["article_id", "title", "body", "published_date", "url"]):
    info = database.session.query(Article).filter(Article.article_id == article_id).first()
    if info is not None:
        return {field: info.__dict__[field] for field in fields}
    return None

def check_cache(model_type, article_id, n=100):
    similar = redis_db.zrange('%s:%s' % (model_type, str(article_id)), 1, n, desc=True, withscores=True)
    #print similar
    if len(similar) > 0:
        return similar
    return None

@app.route('/articles/')
def all_articles():
    article_ids = database.session.query(Article.article_id).all()
    return jsonify({
        "status": "success",
        "ids": article_ids
    })

@app.route('/articles/<article_id>')
def t(article_id):
    article_json = single_article_json(article_id)
    if article_id is None or article_json is None:
        article_ids = database.session.query(Article.article_id).all()
        return jsonify({
            "status": "error",
            "message": "Article ID does not exist or not provided. See list of possible IDs",
            "ids": article_ids
        })

    return jsonify({
        "status": "success",
        "article": article_json
    })

@app.route('/similar/<article_id>/<model_type>/<n>')
def index(article_id, model_type, n):
    if article_id is None:
        return jsonify({"status": "error", "message": "No article ID provided"})
    if model_type is None:
        return jsonify({"status": "error", "message": "No model type provided"})

    if n is None or int(n) > 100:
        return jsonify({"status": "error", "message": "N too large"})

    articles = []
    rank = 1
    similar = check_cache(model_type, article_id, n)
    #print similar
    for (sim_article_id, score) in similar:
        json_article = single_article_json(sim_article_id, fields=["article_id", "title", "published_date", "url"])
        json_article['score'] = score
        articles.append(json_article)
        rank += 1
    return jsonify({"status": "success", "original_article": single_article_json(article_id), "similar_articles": articles})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
