from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, TextAreaField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, NumberRange
from app.models import User


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')
    
    def validate_email_address(self, email_address_to_check):
        # perchè email_address_to_check.data ".data" ???
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Adress already exists! Please try a different username') 
     
    
    username = StringField(label='User Name:', validators=[Length(min=2,max=30), DataRequired()])
    email_address = StringField(label='Email Adress:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label="User Name:", validators=[DataRequired()])
    password = PasswordField(label="Password:", validators=[DataRequired()])
    submit = SubmitField(label='Log In')

class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Acquista!')

class SellItemForm(FlaskForm):
    submit = SubmitField(label='Vendi!')

class AddItemForm(FlaskForm):
    name = StringField(label='Nome Prodotto:', validators=[Length(min=2, max=30), DataRequired()])
    price = IntegerField(label='Prezzo ($):', validators=[DataRequired(), NumberRange(min=1, max=10000)])
    barcode = StringField(label='Codice a Barre:', validators=[Length(min=12, max=12), DataRequired()])
    description = TextAreaField(label='Descrizione:', validators=[Length(min=10, max=1000), DataRequired()])
    submit = SubmitField(label='Aggiungi Prodotto')