from flask.ext.wtf import Form
from wtforms.fields import TextField, RadioField, TextAreaField, PasswordField, BooleanField, SubmitField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo
import string



class SearchQuery(Form):
    queryfield = TextField('Suchfeld', validators=[DataRequired(), Length(min=1)])
    add = SubmitField('Add')
