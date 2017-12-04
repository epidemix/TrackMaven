import pandas as pd
import numpy as np
import nltk
from stop_words import get_stop_words
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from gensim import corpora, models
import gensim
import pyLDAvis.gensim

# read in the data
print('Reading in data...')
df = pd.read_json('https://s3.amazonaws.com/temp-data-pulls/newdump.json')

# clean up from the json file
print('Cleaning up the dataframe...')
pd.options.mode.chained_assignment = None
rawpin_blog = df[(df["type"]=="pin") | (df["type"]=="blog post")]
rawpin_blog.drop(["has_spend"], axis = 1, inplace=True)
channel_info = rawpin_blog['channel_info'].apply(pd.Series)
channel_info.columns = ["channel", "info"]
content_info = rawpin_blog['content'].apply(pd.Series)
content_info.drop(['author_email', 'content', 'pinned_from'], axis=1, inplace=True) ## THESE HAVE ONLY NULLS
for x in content_info.columns:
    if "count" in x:
        content_info[x].fillna(np.NaN, inplace = True)
        #content_info[x] = content_info[x].astype(int)
master_pinblog = rawpin_blog.join(channel_info).join(content_info)
master_pinblog.drop(['channel_info', 'content'], axis = 1, inplace = True)
master_pinblog.columns = ['brand', 'engagement', 'uniqueid', 'impact', 'share_token', 'timestamp',
       'type', 'urls', 'channel', 'info', 'author_name', 'comment_count',
       'description', 'fb_likecount', 'fb_sharecount',
       'gplus_count', 'hashtags', 'image_url', 'like_count',
       'link', 'linkedin_sharecount', 'links', 'pin_id', 'pin_url',
       'pin_count', 'post_type', 'repin_count', 'summary',
       'thumbnail_url', 'title', 'tweet_count']

master_pinblog["links_count"] = master_pinblog['links'].str.len()
df_new = master_pinblog

# create new df called blogs that only contains blogs
blogs = df_new[df_new.type == 'blog post']
# converts link to string so we can split
blogs.link = blogs.link.astype(str)
# instantiate a new list called new_mag
new_mag = []
# list comprehension that just keeps part before '.com'
# we can use list comprehension because this is true for all values
magazine = [i.split('.com')[0] for i in blogs.link]
# start for loop to get rid of everything before the name of the magazine
for i in magazine:
    if '.' in i:
        new_mag.append(i.split('.')[1])
# if there isn't a '.' it just sends the existing name to the list
    else:
        new_mag.append(i)
# create new column for the df with the publications
blogs['pub'] = new_mag

# preprocess for Latent Dirichlet Allocation

stemmer = SnowballStemmer("english",ignore_stopwords=True)
en_stop = get_stop_words('en')
# when a word is stemmed, contractions are rightfully turned into different stems since 's = is
# however, in reality, all of those words are themselves stop words, so I want to exclude them
# question marks and the like are not helpful for our purpose of figuring out potential categories
contractions = ["'s","s","'",".",",","n't","'d","ll","re","ve","``",
                "''","”","“","’","(",")","?",":","t",";","d","!","-","[","]","w","#"]
# list for tokenized documents in loop
texts = []

# loop through document list
post_text = [i for i in blogs.summary]
count = 1
print("Initializing tokenizer and stemmer...")
print("Number of posts tokenized and stemmed:")
for i in post_text:
    # clean and tokenize document string
    raw = i.lower()
    tokens = word_tokenize(raw)

    # stem tokens and remove stop words
    stemmed_tokens = [stemmer.stem(i) for i in tokens if not i in en_stop]

    #remove stemmed contractions
    contracted_tokens = [i for i in stemmed_tokens if not i in contractions]

    # add tokens to list
    texts.append(contracted_tokens)
    if count % 5000 == 0:
        print(count)
    count += 1
print("Stemming Completed.")

# turn our tokenized documents into a id <-> term dictionary
dictionary = corpora.Dictionary(texts)

# convert tokenized documents into a document-term matrix
corpus = [dictionary.doc2bow(text) for text in texts]

# generate LDA model
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=10, id2word = dictionary, passes=1)
print("Raw LDA Topic Output:")
print(ldamodel.print_topics(num_topics=10, num_words=10))

vis = pyLDAvis.gensim.prepare(ldamodel, corpus, dictionary)
pyLDAvis.display(vis)
