from flask.ext.wtf import Form
from wtforms.fields import TextField, RadioField, TextAreaField, PasswordField, BooleanField, SubmitField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo
import string



class SearchQuery(Form):
    queryfield = TextField('Query', validators=[DataRequired(), Length(min=1)])
    normalsearch = SubmitField('Add Smonky-Normal')
    uglysearch = SubmitField('Add Smonky-Ugly')
