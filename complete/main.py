import argparse

from utils import parse_csv, store, database, redis_db
from similarity_model import SimilarityModel
from db_models import Article

def main(args):
    if args.load_from is not None:
        parsed_articles = parse_csv(args.load_from)
        for parsed in parsed_articles:
            print "Storing parsed article %s" % parsed.article_id
            store(parsed)

    if args.build_model is not None:
        data = database.session.query(Article.article_id, Article.body).filter(Article.body != '').all()
        sim_model = SimilarityModel(redis_db, data, args.build_model)
        sim_model.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--load_from', help='Load articles from CSV', action="store")
    parser.add_argument('--build_model', help='Build model of specified type (tfidf, word2vec etc)', action="store")

    args = parser.parse_args()
    main(args)