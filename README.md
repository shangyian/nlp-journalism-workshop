# nlp-journalism-workshop
NLP in Journalism Workshop at PyDays

## Setup

1. Clone this repo with `git@github.com:shangyian/nlp-journalism-workshop.git`. 
2. Create a virtualenv environment with `virtualenv env`.
3. Activate it with `source env/bin/activate`
4. Install Python library requirements with `pip install -r requirements.txt`.

## Cleaning the dataset

In general, this involves anything from filtering out HTML tags and punctuation to removing stop words. 

We are using the Vox articles dataset, which contains all articles published on Vox.com before March 2017 as a CSV file.

This particular dataset has HTML in it, so we want to remove HTML tags and filter out stop words. Stop words are frequently the most common words in a language, and we'll filter them out because they typically aren't semantically significant.

## Modelling Articles

### TF-IDF



### Word2Vec/Article2Vec

### Topic Clustering

### 
