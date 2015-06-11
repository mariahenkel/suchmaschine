from flask.ext.wtf import Form
from wtforms.fields import TextField, RadioField, TextAreaField, PasswordField, BooleanField, SubmitField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo
import string



class SearchQuery(Form):
    queryfield = TextField('Suchfeld', validators=[DataRequired(), Length(min=1)])
    add = SubmitField('Add')
    
class RecipeSearchForm(Form):
    searchfield = SelectField('Suche Nach:', choices=[('recipename', 'Rezeptname'), ('ingredientname', 'Zutatname')])
    searchterm = TextField('searchterm', validators=[DataRequired()])

"""class SearchField(Form):
    username = TextField('Username', validators=[DataRequired(), Length(min=5)])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember = BooleanField('Remember me', default=False)

class EditPasswordForm(Form):
    old_password = PasswordField('Aktuelles Passwort', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired(), EqualTo('confirm', message='Passwoerter muessen uebereinstimmen!'), Length(min=8)])
    confirm = PasswordField('Passwort wiederholen', validators=[DataRequired()])

class EditUserPasswordForm(Form):
    password = PasswordField('Passwort', validators=[DataRequired(), EqualTo('confirm', message='Passwoerter muessen uebereinstimmen!'), Length(min=8)])
    confirm = PasswordField('Passwort wiederholen', validators=[DataRequired()])

class NewUserForm(Form):
    username = TextField('Username', validators=[DataRequired(), Length(min=5)])
    password = PasswordField('Passwort', validators=[DataRequired()])
    active = BooleanField('Active', default=True)

class EditUserForm(Form):
    username = TextField('Username', validators=[DataRequired(), Length(min=5)])
    active = BooleanField('Active', default=True)"""
