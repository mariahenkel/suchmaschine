#!/usr/bin/env python
# coding: utf8

from flask import Flask, render_template, url_for, redirect, flash, request, session
import config
from sqlalchemy import asc
from forms import SearchQuery
from werkzeug import secure_filename
from flask.ext.bootstrap import Bootstrap
import os
#from database import db_session
from nltk.corpus import stopwords  # Stoppwortliste xxx
from nltk.stem import PorterStemmer  # Stemmer xxx
from models import *  # xxx
from sqlalchemy import create_engine  # xxx
from sqlalchemy.ext.declarative import declarative_base  # xxx
from sqlalchemy.orm import sessionmaker  # xxx
from config import DB_URI, DEBUG  # xxx
import operator  # xxx


app = Flask(__name__)
app.debug = True
app.config.from_object(config)


# Ersetzen von Satzzeichen xxx
def replace_char(searchquery):
    replacedquery = []
    char_dict = {'?': '', '!': '', '-': '', ';': '', ':': '', '.': '', '...': '', '\n': ' ', '/': '', '+':
                 '', '<': '', '>': '', '}': '', '{': '', '=': '', ']': '', '[': '', ')': '', '(': '', '|': '', ',': ''}
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
        except:
            pass
    return newquery

# xxx


def select(searchquerynew):
    all_documents = {}
    for element in searchquerynew:
        read_documents = session.query(Document, Wordlist.idf * ConsistsOf.wdf).outerjoin(
            ConsistsOf).outerjoin(Wordlist).filter(Wordlist.word == element).all()
        for document in read_documents:
            a, b = document
            b = 5
            if a in all_documents.keys():
                all_documents[a] = all_documents[a] + b
            else:
                all_documents[a] = b
        sorted_all_documents = sorted(
            all_documents.iteritems(), key=operator.itemgetter(1), reverse=True)
    return [elem[0] for elem in sorted_all_documents]
    


def sugly(searchquerynew):
    all_documents = {}
    for element in searchquerynew:
        read_documents_ugly = session.query(Document, Document.overall_score, Wordlist.idf*ConsistsOf.wdf).outerjoin(ConsistsOf).outerjoin(Wordlist).filter(Wordlist.word == element).all()
        for document in read_documents_ugly:
            a,b,c = document
            b = 5
            if a in all_documents.keys():
                all_documents[a] = all_documents[a] + (b*5+c)
            else:
                all_documents[a] = b*5+c
    sorted_all_documents = sorted(all_documents.iteritems(), key=operator.itemgetter(1), reverse = True)
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


@app.route('/normal', methods=["GET", "POST"])
def normalsearch():
    form = SearchQuery()
    if form.validate_on_submit():
        searchquery = form.queryfield.data.encode('utf-8').split()
        searchqueryreplaced = replace_char(searchquery)
        searchquerynew = process_query(searchqueryreplaced)
        results = select(searchquerynew)
        # print documents_with_terms
        return render_template('index.jinja', form=form,
                               results=results, sugly=False)
    else:
        return redirect('/')


@app.route('/sugly', methods=["GET", "POST"])
def suglysearch():
    form = SearchQuery()
    if form.validate_on_submit():
        searchquery = form.queryfield.data.encode('utf-8').split()
        searchqueryreplaced = replace_char(searchquery)
        searchquerynew = process_query(searchqueryreplaced)
        # TODO: make sugly search here
        results = sugly(searchquerynew)
        print results
        return render_template('index.jinja', form=form,
                               results=results, sugly=True)
    else:
        return redirect('/')



@app.route('/info')
def info():
    return render_template('info.jinja')


if __name__ == "__main__":
    some_engine = create_engine(DB_URI, echo=DEBUG)  # xxx
    Session = sessionmaker(bind=some_engine)  # xxx
    session = Session()
    app.run(debug=True)
