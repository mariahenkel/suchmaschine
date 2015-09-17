# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms.fields import TextField, SubmitField
from wtforms.validators import DataRequired

# Defines the queryfield and submit buttons.
class SearchQuery(Form):
    queryfield = TextField('Query', validators=[DataRequired()])
    normalsearch = SubmitField('Add Smonky-Normal')
    uglysearch = SubmitField('Add Smonky-Ugly')
