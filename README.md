# nlp-journalism-workshop
NLP in Journalism Workshop at PyDays

## Setup

1. Clone this repo with `git@github.com:shangyian/nlp-journalism-workshop.git`. 
2. Create a virtualenv environment with `virtualenv env`.
3. Activate it with `source env/bin/activate`
4. Install Python library requirements with `pip install -r requirements.txt`.
5. Install Redis. Start the server with `redis-server`. 

## Loading dataset

We are using the Vox articles dataset, which contains all articles published on Vox.com before March 2017.
You can download the dataset (in TSV format) from https://data.world/elenadata/vox-articles). Copy this into the `data/` directory, so that we have `data/vox_Articles.tsv`.

Then we'll want to load and clean the data. In general, this involves:
- removing HTML tags
- removing stop words
- tokenizing
- stemming

In order for the Flask API to work, we'll need to build a SQLite database with our articles. To do this, run `python main.py --load_from ./data/vox_Articles.tsv`.

Once you’ve loaded the data into SQLite and set up Redis, we can run the API, which lets us see the data in a more organized fashion: `python api.py`. The API should be running on `http://0.0.0.0:8000/`.

We can test that it’s up with `http://0.0.0.0:8000/articles`, which should return a list of article ids from the database that you can query. You can also pick one of the article ids and try `http://0.0.0.0:8000/articles/<article_id>`, which will output specific data about that article. 

## Similarity

### TF-IDF

### Word2Vec/Article2Vec
