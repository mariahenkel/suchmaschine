# -*- coding: utf-8 -*-

from math import log  # log for idf and wdf calculation

from nltk.corpus import stopwords   # stopwords to detect language
from nltk import wordpunct_tokenize  # function to split up our words
from nltk.stem import PorterStemmer  # Import Stemmer
from bs4 import BeautifulSoup, Comment  # Import BeautifulSoup und Comment
# SQLAlchemy imports
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, scoped_session

from config import DB_URI, DEBUG
from models import Wordlist, ConsistsOf, Document


# ----------------------------------------------------------------------
# From here on: Stemming / Stopword Recognition / Saving into Database
# ----------------------------------------------------------------------


engine = create_engine(DB_URI, echo=DEBUG)
session_factory = sessionmaker(bind=engine)
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

    doc = second_session.query(Document).filter(
        Document.id == document.id).first()
    doc.language = get_language(document.html_document)[:3]
    second_session.add(doc)
    second_session.commit()
    if document.language == "eng":
        soup = BeautifulSoup(document.html_document)

        # remove javascript
        for s in soup('script'):
            s.extract()
        # remove all comments
        if soup.body:
            for child in soup.body:
                if isinstance(child, Comment):
                    child.extract()

            body_text = soup.body.getText()

            char_dict = {'?': '', '!': '', '-': '', ';': '', ':': '',
                         '.': '', '...': '', '\n': ' ', '/': '',
                         '+': '', '<': '', '>': '', '}': '', '{': '', '=': '',
                         ']': '', '[': '', ')': '', '(': '', '|': ''}
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
                if len(element) <= 50 and length_website > 1:
                    word_count = word_list.count(element)
                    word = second_session.query(Wordlist).filter(
                        Wordlist.word == element).first()
                    if not word:
                        # create a new word
                        word_pos = word_pos + 1
                        word = Wordlist()
                        word.word = element
                        word.stem = stemmer.stem(element)
                        word.stopword = element in stop
                        second_session.add(word)
                        second_session.commit()

                    # check if the relation for this word and document already
                    # exists
                    existing_consist_of = second_session.query(ConsistsOf).\
                        filter(
                        ConsistsOf.document_documentid == document.id).filter(
                        ConsistsOf.wordlist_wordid == word.id).first()

                    if not existing_consist_of:
                        # calculate wdf
                        wdf_word = log(word_count + 1) / log(length_website)

                        # create relationship between word and document
                        consists_of = ConsistsOf()
                        consists_of.document_documentid = document.id
                        consists_of.wordlist_wordid = word.id
                        consists_of.wdf = wdf_word
                        consists_of.stopword = 0
                        consists_of.sentenceno = 0
                        consists_of.position = word_pos
                        second_session.add(consists_of)
                        second_session.commit()


def calculate_idf():
    # https://en.wikipedia.org/wiki/Tf%E2%80%93idf#Inverse_document_frequency_2
    # get number of indexed Documents
    big_n = session.query(
        func.count(distinct(ConsistsOf.document_documentid))).first()[0]
    for word in session.query(Wordlist).yield_per(100):
        small_n = len(word.document_assocs)
        # use a second session because of yield_per
        # (see http://stackoverflow.com/q/12233115/2175370)
        writeable_word = second_session.query(Wordlist).filter(
            Wordlist.id == word.id).first()
        # adjust the small_n (+1) to avoid division-by-zero
        writeable_word.idf = float(log(big_n / (small_n + 1)))

        second_session.add(writeable_word)
        second_session.commit()

if __name__ == "__main__":
    # get all documents from the db
    print "#### indexing all words from all documents"
    counter = 0
    html_document = session.query(
        Document).yield_per(100)
    # index all of them
    for element in html_document:
        counter += 1
        if counter % 100 == 0:
            print 'indexed {0} documents so far'.format(counter)
        index_document(element)
    print "#### calculating IDF for all words"
    # calculate idf
    calculate_idf()
