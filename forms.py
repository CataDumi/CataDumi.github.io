from flask_wtf import FlaskForm, Form
from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators, TextField, TextAreaField, \
    IntegerField,FloatField,RadioField,SelectField
from wtforms.validators import DataRequired, URL, InputRequired, NumberRange, Email,Length


class EquipmentForm(FlaskForm):
    marca = IntegerField('Marca', validators=[DataRequired()])
    name = StringField('Nume echipament', validators=[DataRequired()])
    quantity = IntegerField('Cantitate valabila ', validators=[DataRequired(message='Error: Sunt acceptate doar numere intregi'),NumberRange(min=0,max=99999)])
    submit = SubmitField('Submit ')

class MaterialsForm(FlaskForm):
    marca = IntegerField('Marca', validators=[DataRequired()])
    name = StringField('Nume material', validators=[DataRequired()])
    quantity = IntegerField('Cantitate valabila ', validators=[DataRequired(message='Error: Sunt acceptate doar numere intregi'),NumberRange(min=0,max=99999)])
    submit = SubmitField('Submit ')

#Form pt inregistrare users
class RegisterForm(FlaskForm):
    marca=StringField('Marca ', validators=[DataRequired()])
    name = StringField('Nume ', validators=[DataRequired()])
    funct = SelectField('Functia',choices=['Inginer','Electrician'], validators=[DataRequired()])
    telephone = IntegerField('Numar de telefon', validators=[DataRequired()])
    email = TextField('Email', validators=[DataRequired(),Email()])
    submit = SubmitField('Inregistreaza persoanal')

class LoginForm(FlaskForm):
    email = TextField('Enter email', validators=[DataRequired(), Email()])
    password = PasswordField('Enter password', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Submit login')
