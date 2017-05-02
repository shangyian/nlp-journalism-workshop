# nlp-journalism-workshop
NLP in Journalism Workshop at PyDays

## Cleaning the dataset
This particular dataset has HTML in it, so we want to remove HTML tags.

```
from bs4 import BeautifulSoup, Comment
def clean_html(self, raw_text):
    soup = BeautifulSoup(raw_text, 'html.parser')
    text = ""
    for t in soup.find_all(text=True):
        if isinstance(t, Comment):
            continue
        text += " %s" % unicode(t)
    text = " ".join(text.split()).strip()
    tags_removed = self.re_html_comment.sub("", text)
    return tags_removed
```

After parsing out tags, we also want to remove stop words. Stop words are frequently the most common words in a language, and we'll filter them out because they typically aren't semantically significant.

## Modelling Articles

### TF-IDF



### Word2Vec/Article2Vec

### Topic Clustering

### 
