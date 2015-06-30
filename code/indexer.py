# -*- coding: utf-8 -*-

import sys
import re

# Die folgende Zeile führt unter Linux zu einer Fehlermeldung. Bitte ggf. (ent)kommentieren.
#from BeautifulSoup import BeautifulSoup

from nltk.corpus import stopwords   # stopwords to detect language
from nltk import wordpunct_tokenize  # function to split up our words
from nltk.stem import PorterStemmer  # Import Stemmer

from bs4 import BeautifulSoup, Comment  # Import BeautifulSoup und Comment


# SQLAlchemy imports

from sqlalchemy import create_engine, select
from sqlalchemy import MetaData, Table
import config
from math import log
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_URI, DEBUG
from models import Wordlist, Document, ConsistsOf
#from models import wordlist, document
#from database import db_session

# Encoding for the file
reload(sys)
sys.setdefaultencoding("utf-8")

# Establish connection, load all necessary tables
engine = create_engine(config.DB_URI, echo=False)
metadata = MetaData(bind=engine)
wordtable = Table("wordlist", metadata, autoload=True)
webpage = Table("document", metadata, autoload=True)
relation = Table("consists_of", metadata, autoload=True)

Base = declarative_base()


#----------------------------------------------------------------------
# From here on: Stemming / Stopword Recognition / Saving into Database
#----------------------------------------------------------------------


some_engine = create_engine(DB_URI, echo=DEBUG)
Session = sessionmaker(bind=some_engine)
session = Session()


def get_language_likelihood(website):
    """Return a dictionary of languages and their likelihood of being the
    natural language of the input text
    """

    """ tokenize lower case web source """
    website = website.lower()
    words = wordpunct_tokenize(website)

    candidates = {}
    for language in stopwords._fileids:
        candidates[language] = len(
            set(words) & set(stopwords.words(language)))

    return candidates


def get_language(input_text):
    """Return the most likely language of the given text
    """

    likelihoods = get_language_likelihood(input_text)

    return sorted(likelihoods, key=likelihoods.get, reverse=True)[0]


def indexer(document):
    if get_language(document.html_document) == "english":
        soup = BeautifulSoup(document.html_document)
        # remove javascript
        for s in soup('script'):
            s.extract()
        # remove all comments
        for child in soup.body:
            if isinstance(child, Comment):
                child.extract()

        body_text = soup.body.getText()

        char_dict = {'?': '', '!': '', '-': '', ';': '', ':': '', '.': '', '...': '', '\n': ' ', '/': '',
                     '+': '', '<': '', '>': '', '}': '', '{': '', '=': '', ']': '', '[': '', ')': '', '(': '', '|': ''}
        for i, j in char_dict.iteritems():
            body_text = body_text.replace(i, j)
        word_list = body_text.lower().split()

        # save every word plus stem, count, etc. in the database/dictionary
        # Use english stopword list from nltk corpus
        stop = stopwords.words('english')

        word_pos = 0  # Counter for word position
        stemmer = PorterStemmer()
        length_website = 0  # Counter for text length

        dict_duplicate = {}
        for element in word_list:
            length_website = length_website + 1
            word_count = word_list.count(element)
            if element not in dict_duplicate.keys():
                dict_duplicate[element] = True
                try:
                    word_stem = stemmer.stem(element)
                    # Number of the word in this text
                    if element in stop:
                        is_stop = 1
                    else:
                        is_stop = 0
                    word_insert = wordtable.insert().execute(
                        word=element, stem=word_stem, stopword=is_stop, number=word_count)
                    word_id = word_insert.inserted_primary_key
                    wdf_word = log(word_count) / log(2) + 1 / \
                        log(length_website) / log(2)
                    #
                    relation.insert().execute(
                        document_documentid=document.id, wordlist_wordid=word_id[0], wdf=wdf_word)
                    word_pos = word_pos + 1
                except:
                    pass
            else:
                wdf_word = log(word_count) / log(2) + 1 / \
                    log(length_website) / log(2)
                relation.update(
                    document_documentid=document.id, wordlist_wordid=word_id[0], wdf=wdf_word)


if __name__ == "__main__":
    # get all documents from the db
    html_document = session.query(
        Document).yield_per(100)

    # index all of them
    for element in html_document:
        indexer(element)

    # calculate idf
    N = session.query(Document).count()
    dictidf = {}
    words = session.query(ConsistsOf.wordlist_wordid).all()
    # print words
    for element in words:
        if element not in dictidf.keys():
            dictidf[element] = 1
        else:
            dictidf[element] = dictidf[element] + 1
    print dictidf

    # for values in dictidf.values():
    #   IDF = float(log(N/values))+1/log(2)
    # print IDF
# wordtable.update().execute(idf=IDF)
