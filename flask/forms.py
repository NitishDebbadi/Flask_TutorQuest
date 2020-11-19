from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, length, Email, equal_to


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), length(min=6, max=30)])
    usertype = SelectField('Usertype', validators=[DataRequired()], choices=[(1, 'tutor'), (2, 'User')], coerce=int)
    email = StringField('Email', validators=[DataRequired(), Email(), length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), equal_to("password")])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), length(max=50)])
    usertype = SelectField('Usertype', validators=[DataRequired()], choices=[(1, 'tutor'), (2, 'User')], coerce=int)
    password = PasswordField('Password', validators=[DataRequired(), length(min=6)])
    submit = SubmitField("Login")
