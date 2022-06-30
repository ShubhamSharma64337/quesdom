from ast import Str, Sub
from secrets import choice
from quesdom.models import Users
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators = [DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    #the code below will check if a user withe username already exists
    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken, please enter another username')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already used, please enter another username')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CreateQuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired(),Length(min=2,max=30)])
    category = StringField('Quiz Category', validators=[DataRequired(),Length(min=2,max=20)])
    difficulty = SelectField('Difficulty',choices=['Easy','Moderate','Hard'],validators=[DataRequired()])
    description = TextAreaField('Description',validators=[DataRequired(),Length(min=2,max=200)])
    submit = SubmitField('Submit')


class CreateQuestionForm(FlaskForm):
    statement = StringField('Question Statement',validators=[DataRequired()])
    duration = IntegerField('Question Duration',validators=[DataRequired()])
    correct_choice = StringField('Correct Choice', validators=[DataRequired()])
    incorrect_choice_1 = StringField('Incorrect Choice - 1',validators=[DataRequired()])
    incorrect_choice_2 = StringField('Incorrect Choice - 2',validators=[DataRequired()])
    incorrect_choice_3 = StringField('Incorrect Choice - 3',validators=[DataRequired()])
    submit = SubmitField('Submit')