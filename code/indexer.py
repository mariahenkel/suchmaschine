# -*- coding: utf-8 -*-

import sys

from nltk.corpus import stopwords   # stopwords to detect language
from nltk import wordpunct_tokenize  # function to split up our words
from nltk.stem import PorterStemmer  # Import Stemmer

from bs4 import BeautifulSoup, Comment  # Import BeautifulSoup und Comment


# SQLAlchemy imports

from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table
import config
from math import log
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DB_URI, DEBUG
from models import Wordlist, Document, ConsistsOf

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
session_factory = sessionmaker(bind=some_engine)
session = scoped_session(session_factory)
second_session = scoped_session(session_factory)


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


def index_document(document):
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
        length_website = len(word_list)

        for element in word_list:
            if len(element) <= 50:
                word_count = word_list.count(element)
                word = session.query(Wordlist).filter(
                    Wordlist.word == element).first()
                if not word:
                    # create a new word
                    word_pos = word_pos + 1
                    word = Wordlist()
                    word.word = element
                    word.stem = stemmer.stem(element)
                    word.stopword = element in stop
                    session.add(word)
                    session.commit()

                # check if the relation for this word and document already
                # exists
                existing_consist_of = session.query(ConsistsOf).filter(
                    ConsistsOf.document_documentid == document.id).filter(
                    ConsistsOf.wordlist_wordid == word.id).first()

                if not existing_consist_of:
                    # calculate wdf
                    wdf_word = log(word_count) / log(2) + 1 / \
                        log(length_website) / log(2)

                    # create relationship between word and document
                    consists_of = ConsistsOf()
                    consists_of.document_documentid = document.id
                    consists_of.wordlist_wordid = word.id
                    consists_of.wdf = wdf_word
                    consists_of.stopword = 0
                    consists_of.sentenceno = 0
                    consists_of.position = word_pos
                    session.add(consists_of)
                    session.commit()


def calculate_idf():
    # https://en.wikipedia.org/wiki/Tf%E2%80%93idf#Inverse_document_frequency_2
    big_n = session.query(Document).count()
    for word in session.query(Wordlist).yield_per(100):
        small_n = len(word.document_assocs)
        # use a second session because of yield_per
        # see (http://stackoverflow.com/q/12233115/2175370)
        writeable_word = second_session.query(Wordlist).filter(
            Wordlist.id == word.id).first()
        # adjust the small_n (+1) to avoid division-by-zero
        writeable_word.idf = float(log(big_n / (small_n + 1)))

        second_session.add(writeable_word)
        second_session.commit()

if __name__ == "__main__":
    # get all documents from the db
    print "#### indexing all words from all documents"
    html_document = session.query(
        Document).yield_per(100)
    # index all of them
    for element in html_document:
        index_document(element)
    print "#### calculating IDF for all words"
    # calculate idf
    calculate_idf()
