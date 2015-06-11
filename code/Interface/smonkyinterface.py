from flask import Flask, render_template, url_for, redirect, flash, request, session
import config
from sqlalchemy import asc
from forms import SearchQuery
from werkzeug import secure_filename
from flask.ext.bootstrap import Bootstrap
import os
"""from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user"""
"""from models import User"""
"""from database import db_session"""
"""from hash_passwords import make_hash"""
from sqlalchemy import asc


app = Flask(__name__)
app.debug = True
app.config.from_object(config)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    form = SearchQuery()
    return render_template('index.jinja', form=form)

"""@app.route('/smonkynormal')
def smonkynormal():
    form = SearchQuery()
    return render_template('smonkynormal.jinja', form=form)
    
@app.route('/smonkycrazy')
def smonkycrazy():
    form = SearchQuery()
    return render_template('smonkycrazy.jinja', form=form)
    
@app.route('/help')
def helpsite():
    return render_template('help.jinja')"""

"""
@app.route('/recipe/add', methods=["GET", "POST"])
@login_required
def recipe_add():
    form = NewRecipeForm()
    if form.validate_on_submit():
        new_recipe = Recipe(recipename=form.recipename.data, instruction=form.instruction.data, grade=form.grade.data,  recipe_username=current_user.username)
        if new_recipe:
            db_session.add(new_recipe)
            db_session.commit()
            flash(gettext('Neues Rezept erfolgreich angelegt!'))
            return redirect(url_for('recipes_list'))
        else:
            flash(gettext('Neues Rezept konnte nicht angelegt werden!'))
    return render_template('recipe_add.jinja', form=form)

"""



if __name__ == "__main__":
    app.run()
