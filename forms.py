from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PictureForm(FlaskForm):
    name = StringField('Picture Name', validators=[DataRequired(), Length(min=1, max=100)])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    submit = SubmitField('Add Picture')

class ToggleLikeForm(FlaskForm):
    user_id = HiddenField()
