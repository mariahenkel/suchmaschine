#!/usr/bin/env python
# -*- coding: utf-8 -*-
import operator
from flask import Flask, render_template, redirect
from forms import SearchQuery

from nltk.corpus import stopwords  # Stoppwortliste
from nltk.stem import PorterStemmer  # Stemmer
from models import Document, ConsistsOf, Wordlist
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config


app = Flask(__name__)
app.debug = True
app.config.from_object(config)

# sqlalchemy session
some_engine = create_engine(config.DB_URI, echo=config.DEBUG)
Session = sessionmaker(bind=some_engine)
session = Session()


# replacing puctuatuion marks from the query
def replace_char(searchquery):
    replacedquery = []
    char_dict = {'?': '', '!': '', '-': '', ';': '', ':': '', '.': '',
                 '...': '', '\n': ' ', '/': '', '+': '', '<': '', '>': '',
                 '}': '', '{': '', '=': '', ']': '', '[': '', ')': '',
                 '(': '', '|': '', ',': ''}
    for element in searchquery:
        for i, j in char_dict.iteritems():
            for letter in element:
                if i == letter:
                    element = element.replace(i, j)
                else:
                    continue
        replacedquery.append(element)
    return replacedquery

# stemming and removing stop words from the query


def process_query(searchqueryreplaced):
    stop = stopwords.words('english')
    stemmer = PorterStemmer()
    newquery = []
    for element in searchqueryreplaced:
        element = element.lower()
        try:
            word_stem = stemmer.stem(element)
            if element in stop:
                continue
            else:
                newquery.append(word_stem)
        except Exception as e:
            print e
    return newquery

# comparing the words in the query with the words of all documents.
# calculation of the overall score for one document with the help of wdf
# and idf.


def select(searchquerynew):
    all_documents = {}
    for element in searchquerynew:
        results = session.query(Document, Wordlist, ConsistsOf).outerjoin(
            ConsistsOf).outerjoin(Wordlist)\
            .filter(Wordlist.word == element).all()
        for result in results:
            website = result[0]
            word = result[1]
            relation = result[2]
            wdf = relation.wdf
            idf = word.idf
            website.wdf = wdf
            website.idf = idf
            wdf = 0 if not wdf else wdf
            idf = 0 if not idf else idf
            wdf_idf = wdf * idf
            if website in all_documents.keys():
                all_documents[website] = all_documents[website] + wdf_idf
            else:
                all_documents[website] = wdf_idf
        sorted_all_documents = sorted(
            all_documents.iteritems(),
            key=operator.itemgetter(1),
            reverse=True)
    return [elem[0] for elem in sorted_all_documents]

# comparing the words in the query with the words of all documents.
# calculation of the overall score for one document with the help of wdf,
# idf and the unusability score.


def sugly(searchquerynew):
    all_documents = {}
    for element in searchquerynew:
        results = session.query(Document, Wordlist, ConsistsOf).outerjoin(
            ConsistsOf).outerjoin(Wordlist)\
            .filter(Wordlist.word == element).all()
        for result in results:
            website = result[0]
            word = result[1]
            relation = result[2]
            wdf = relation.wdf
            idf = word.idf
            website.wdf = wdf
            website.idf = idf
            website.ur = website.overall_score
            wdf = 0 if not wdf else wdf
            idf = 0 if not idf else idf
            wdf_idf = wdf * idf
            Uscore = website.overall_score
            Uscore = 0 if not Uscore else Uscore
            if website in all_documents.keys():
                all_documents[website] = all_documents[
                    website] + (Uscore * 2 + wdf_idf)
            else:
                all_documents[website] = Uscore * 2 + wdf_idf
    sorted_all_documents = sorted(
        all_documents.iteritems(), key=operator.itemgetter(1), reverse=True)
    return [elem[0] for elem in sorted_all_documents]


# @app.teardown_appcontext
# def shutdown_session(exception=None):
#    db_session.remove()

# Index
# Represents the cover page of the search engine smonky.
# Search keywords can be entered into the search field.
# Therby a user can chose between the two search modes:
# “Normal Search” (for a standart search) or “Let’s be crazy!” (for a unitability search).
# Redirects either to the "/normal" route or to the "/sugly" route.

@app.route('/', methods=["GET", "POST"])
def index():
    form = SearchQuery()
    return render_template('index.jinja', form=form)

# Output impressum template.


@app.route('/impressum')
def impressum():
    return render_template('impressum.jinja')

# Output normal-search template plus search results.


@app.route('/normal', methods=["GET", "POST"])
def normalsearch():
    form = SearchQuery()
    if form.validate_on_submit():
        searchquery = form.queryfield.data.encode('utf-8').split()
        searchqueryreplaced = replace_char(searchquery)
        searchquerynew = process_query(searchqueryreplaced)
        results = select(searchquerynew)
        return render_template('index.jinja', form=form,
                               results=results, sugly=False,
                               debug=config.DEBUG)
    else:
        return redirect('/')

# Output unusability-search template plus search results.


@app.route('/sugly', methods=["GET", "POST"])
def suglysearch():
    form = SearchQuery()
    if form.validate_on_submit():
        searchquery = form.queryfield.data.encode('utf-8').split()
        searchqueryreplaced = replace_char(searchquery)
        searchquerynew = process_query(searchqueryreplaced)
        results = sugly(searchquerynew)
        return render_template('index.jinja', form=form,
                               results=results, sugly=True, debug=config.DEBUG)
    else:
        return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
