#!/usr/bin/env python
# coding: utf8

from flask import Flask, render_template, redirect
import config
from forms import SearchQuery

from nltk.corpus import stopwords  # Stoppwortliste xxx
from nltk.stem import PorterStemmer  # Stemmer xxx
from models import *  # xxx
from sqlalchemy import create_engine  # xxx
from sqlalchemy.orm import sessionmaker  # xxx
from config import DB_URI, DEBUG  # xxx
import operator  # xxx


app = Flask(__name__)
app.debug = True
app.config.from_object(config)

# sqlalchemy session
some_engine = create_engine(DB_URI, echo=DEBUG)  # xxx
Session = sessionmaker(bind=some_engine)  # xxx
session = Session()


# Ersetzen von Satzzeichen xxx
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

# Stemming der Suchanfrage und entfernen von Stoppworten xxx


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

# xxx


def select(searchquerynew):
    all_documents = {}
    for element in searchquerynew:
        results = session.query(Document, Wordlist, ConsistsOf).outerjoin(
            ConsistsOf).outerjoin(Wordlist).filter(Wordlist.word == element).all()
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
            all_documents.iteritems(), key=operator.itemgetter(1), reverse=True)
    return [elem[0] for elem in sorted_all_documents]


def sugly(searchquerynew):
    all_documents = {}
    for element in searchquerynew:
        results = session.query(Document, Wordlist, ConsistsOf).outerjoin(
            ConsistsOf).outerjoin(Wordlist).filter(Wordlist.word == element).all()
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


#@app.teardown_appcontext
# def shutdown_session(exception=None):
#    db_session.remove()

# Index-Seite.
# Stellt die Startseite dar, hier sollte aber auch direkt die Eingabe in das Suchfeld weiterverarbeitet werden, damit dann, je nach gewählter Suche,
# das Template für Smonky-Normal, oder Smonky-Ugly ausgegeben werden kann.

@app.route('/', methods=["GET", "POST"])
def index():
    form = SearchQuery()
    return render_template('index.jinja', form=form)


@app.route('/impressum')
def impressum():
    return render_template('impressum.jinja')


@app.route('/normal', methods=["GET", "POST"])
def normalsearch():
    form = SearchQuery()
#    results = []
    if form.validate_on_submit():
        searchquery = form.queryfield.data.encode('utf-8').split()
        searchqueryreplaced = replace_char(searchquery)
        searchquerynew = process_query(searchqueryreplaced)
        results = select(searchquerynew)
        return render_template('index.jinja', form=form,
                               results=results, sugly=False, debug=DEBUG)
    else:
        return redirect('/')


@app.route('/sugly', methods=["GET", "POST"])
def suglysearch():
    form = SearchQuery()
    if form.validate_on_submit():
        searchquery = form.queryfield.data.encode('utf-8').split()
        searchqueryreplaced = replace_char(searchquery)
        searchquerynew = process_query(searchqueryreplaced)
        results = sugly(searchquerynew)
        return render_template('index.jinja', form=form,
                               results=results, sugly=True, debug=DEBUG)
    else:
        return redirect('/')


@app.route('/info')
def info():
    return render_template('info.jinja')


if __name__ == "__main__":
    app.run(debug=True)
