from turtle import title
from flask import render_template,flash,redirect, request, url_for
from quesdom.forms import RegistrationForm,LoginForm,CreateQuizForm,CreateQuestionForm
from quesdom.models import Questions, Quizzes, Users, Choices
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
@login_required
def logout():
    logout_user()
    flash('You have been logged out!',category='info')
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html',title='Account')

@app.route('/indexquiz')
@login_required
def indexquiz():
    if not current_user.role == 'Admin':
        flash('You must be an admin to access this page!',category='info')
        return redirect('home')
    if Quizzes.query.filter_by().count() == 0:
        flash('No quizzes found, please add a quiz!','info')
        return redirect('home')
    return render_template('indexquiz.html',title='All Quizzes',quizzes = Quizzes.query.all())
    

@app.route('/createquiz',methods=['GET','POST'])
@login_required
def createquiz():
    if not current_user.role == 'Admin':
        flash('You must be an admin to access this page!',category='info')
        return redirect('home')
    form = CreateQuizForm()
    if form.validate_on_submit():
        quiz = Quizzes(quiz_title=form.title.data,quiz_category=form.category.data,quiz_difficulty=form.difficulty.data,quiz_description=form.description.data,date_created=date.today())
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully',category='success')
        return redirect('indexquiz')
    return render_template('createquiz.html',title='Create a Quiz',form=form)

@app.route('/deletequiz')
@login_required
def deletequiz():
    if not current_user.role == 'Admin':
        flash('You must be an admin to access this page!',category='info')
        return redirect('home')
    quiz = Quizzes.query.get(request.args.get('quiz_id'))
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully','success')
    return redirect('indexquiz')
@app.route('/createquestion',methods=['GET','POST'])
@login_required
def createquestion():
    if not current_user.role == 'Admin':
        flash('You must be an admin to access this page!',category='info')
        return redirect('home')
    form = CreateQuestionForm()
    if form.validate_on_submit():
        question = Questions(question_statement=form.statement.data,quiz_id=request.args.get('id'),duration=form.duration.data)
        choice = Choices(correct_choice = form.correct_choice.data,incorrect_choice_1=form.incorrect_choice_1.data,incorrect_choice_2=form.incorrect_choice_2.data, incorrect_choice_3=form.incorrect_choice_3.data)
        db.session.add(choice)
        db.session.flush()
        db.session.refresh(choice)
        question.choice_id = choice.id
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully',category='success')
        return redirect('indexquiz')
    return render_template('createquestion.html',title='Create a Quiz',form=form)

@app.route('/indexquestions')
@login_required
def indexquestions():
    if not current_user.role == 'Admin':
        flash('You must be an admin to access this page!',category='info')
        return redirect('home')
    if Questions.query.filter_by(quiz_id=request.args.get('quiz_id')).count() == 0:
        flash('This quiz currently has no questions!','info')
        return redirect('indexquiz')
    return render_template('indexquestions.html',title='Question List',questions = Questions.query.filter_by(quiz_id = request.args.get('quiz_id')),choices= Choices.query.all())


@app.route('/deletequestion')
@login_required
def deletequestion():
    if not current_user.role == 'Admin':
       flash('You must be an admin to access this page!',category='info')
       return redirect('home')
    question = Questions.query.get(request.args.get('question_id'))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('indexquestions',quiz_id=request.args.get('quiz_id')))

@app.route('/allquizzes')
def allquizzes():
    return render_template('allquizzes.html',title='All Quizzes',quizzes=Quizzes.query.all())