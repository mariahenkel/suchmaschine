#!/usr/bin/env python
# coding: utf8

from flask import Flask, render_template, url_for, redirect, flash, request, session
import config
from sqlalchemy import asc
from forms import SearchQuery
from werkzeug import secure_filename
from flask.ext.bootstrap import Bootstrap
import os
from database import db_session




app = Flask(__name__)
app.debug = True
app.config.from_object(config)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Index site.
# Stellt die Startseite dar, hier sollte aber auch direkt die Eingabe in das Suchfeld weiterverarbeitet werden, damit dann, je nach gewählter Suche,
# das Template für Smonky-Normal, oder Smonky-Ugly ausgegeben werden kann.
@app.route('/', methods=["GET", "POST"])
def index():
    form = SearchQuery()
    results = []
     """if form.validate_on_submit():
        #@ Julia, ab hier müsstet ihr dann ja eure Suche einfügen. Ich hab jetzt erstmal noch eine Suche stehen gelassen, die ich damals bei nem anderen Projekt hatte.
        if form.searchfield.data == 'queryfield':
            results = Recipe.query.filter_by().filter(Recipe.recipename.like('%'+form.searchterm.data+'%')).order_by('???').all()
            return render_template('index.jinja', form=form, results=results)
        elif form.searchfield.data == 'ingredientname':
            results = ingredients.query.filter_by().filter(ingredients.ingredientname.like('%'+form.searchterm.data+'%')).order_by('ingredientname').all()
            return render_template('search.jinja', form=form, results = results)
        else:
            flash(gettext('Ungueltige Feldoption!'))
            return redirect(url_for('index'))
    return render_template('index.jinja', form=form)"""
    


    

# Shows the results for the search with smonky normal.  
@app.route('/results_snormal')
@login_required
def results_snormal():
    results = Document.query.order_by(asc('???')).all()
    return render_template('results_snormal.jinja', results=results)

# Shows the results for the search with smonky ugly.  
@app.route('/results_sugly')
@login_required
def results_sugly():
    results = Document.query.order_by(asc('???')).all()
    return render_template('results_sugly.jinja', results=results)
    

"""
    
@app.route('/help')
def helpsite():
    return render_template('help.jinja')"""


if __name__ == "__main__":
    app.run()
