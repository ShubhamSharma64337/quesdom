from flask import render_template,flash,redirect, request, url_for
from quesdom.forms import RegistrationForm,LoginForm,CreateQuizForm
from quesdom.models import Quizzes, Users
from quesdom import app,bcrypt,db
from flask_login import login_user,current_user,logout_user,login_required
from datetime import date

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html',title='Home')

@app.route('/about')
def about():
    return render_template('about.html',title='About Page')

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash('Login successful!',category='success')
                return redirect(next_page) if next_page else redirect('home')
        else:
            flash('Login unsuccessful, please check email and password!','danger')
    return render_template('login.html',title='Login', form=form)
    
@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data,email=form.email.data,password = hashed_pw, role='Player')
        
        db.session.add(user)
        db.session.commit()

        flash(f'Account Created for {form.username.data}, You can login now!','success')
        return redirect(url_for('login'))

    return render_template('register.html',title='Register', form=form)
    
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!',category='info')
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html',title='Account')

@app.route('/indexquiz')
def indexquiz():
    return render_template('indexquiz.html',title='All Quizzes',quizzes = Quizzes.query.all())

@app.route('/createquiz',methods=['GET','POST'])
def createquiz():
    form = CreateQuizForm()
    if form.validate_on_submit():
        quiz = Quizzes(quiz_title=form.title.data,quiz_category=form.category.data,quiz_difficulty=form.difficulty.data,quiz_description=form.description.data,date_created=date.today())
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully',category='success')
        return redirect('indexquiz')
    return render_template('createquiz.html',title='Create a Quiz',form=form)
