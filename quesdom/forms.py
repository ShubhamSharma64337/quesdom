from ast import Str, Sub
from secrets import choice
from tokenize import String
from quesdom.models import Users,Choices
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, SelectField, TextAreaField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange



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

class TeacherRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(),Length(min=2,max=20)])
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

class StudentRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(),Length(min=2,max=20)])
    semester = IntegerField('Semester', validators=[DataRequired(), NumberRange(min=1, max=6, message='Invalid semester')])
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
    difficulty = SelectField('Difficulty',choices=['Easy','Medium','Hard'],validators=[DataRequired()])
    description = TextAreaField('Description',validators=[DataRequired(),Length(min=2,max=200)])
    timed = BooleanField('With Timer?')
    submit = SubmitField('Submit')

class CreateClassForm(FlaskForm):
    name = StringField('Classroom Name', validators=[DataRequired(),Length(min=2,max=30)])
    submit = SubmitField('Submit')


class CreateQuestionForm(FlaskForm):
    statement = StringField('Question Statement',validators=[DataRequired()])
    duration = IntegerField('Question Duration',validators=[DataRequired()])
    correct_choice = StringField('Correct Choice', validators=[DataRequired()])
    incorrect_choice_1 = StringField('Incorrect Choice - 1',validators=[DataRequired()])
    incorrect_choice_2 = StringField('Incorrect Choice - 2',validators=[DataRequired()])
    incorrect_choice_3 = StringField('Incorrect Choice - 3',validators=[DataRequired()])
    submit = SubmitField('Submit')

class UpdateQuestionForm(FlaskForm):
    statement = StringField('Question Statement',validators=[DataRequired()])
    duration = IntegerField('Question Duration',validators=[DataRequired()])
    correct_choice = StringField('Correct Choice', validators=[DataRequired()])
    incorrect_choice_1 = StringField('Incorrect Choice - 1',validators=[DataRequired()])
    incorrect_choice_2 = StringField('Incorrect Choice - 2',validators=[DataRequired()])
    incorrect_choice_3 = StringField('Incorrect Choice - 3',validators=[DataRequired()])
    submit = SubmitField('Update')

class CreateQuizFromApiForm(FlaskForm):
    title = StringField('Quiz Title',validators=[DataRequired()])
    category = SelectField('Quiz Category', validators=[DataRequired()])
    difficulty = SelectField('Difficulty',choices=['Easy','Medium','Hard'],validators=[DataRequired()])
    description = TextAreaField('Description',validators=[DataRequired(),Length(min=2,max=200)])
    numques = IntegerField('Number of questions',validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreateJoinRequestForm(FlaskForm):
    class_id = IntegerField('Classroom ID',validators=[DataRequired()])
    submit = SubmitField('Send Request')