from flask import render_template,flash,redirect, request, url_for
from quesdom.forms import CreateQuizFromApiForm, RegistrationForm,LoginForm,CreateQuizForm,CreateQuestionForm, UpdateQuestionForm
from quesdom.models import Questions, Quizzes, Users, Choices, Answers
from quesdom import app,bcrypt,db
from flask_login import login_user,current_user,logout_user,login_required
from datetime import date
from random import shuffle
import json
import requests

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
                if next_page:
                    return redirect(next_page)
                else:
                    if current_user.role == "Admin":
                        return redirect('indexquiz')
                    else:
                        return redirect('account')
                return redirect(next_page) if next_page else redirect('account')
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
    if current_user.role == 'Player':
        return render_template('account.html',q_played = get_quizzes_played().count())
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

    page = request.args.get('page',1,int)
    quizzes = Quizzes.query.paginate(per_page = 5,page=page)

    return render_template('indexquiz.html',title='All Quizzes',quizzes = quizzes)

@app.route('/createquiz',methods=['GET','POST'])
@login_required
def createquiz():
    if not current_user.role == 'Admin':
        flash('You must be an admin to access this page!',category='info')
        return redirect('home')
    form = CreateQuizForm()
    if form.validate_on_submit():
        quiz = Quizzes(quiz_title=form.title.data,quiz_category=form.category.data,quiz_difficulty=form.difficulty.data,quiz_description=form.description.data,date_created=date.today(),author=current_user.id)
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
        question = Questions(question_statement=form.statement.data,quiz_id=request.args.get('quiz_id'),duration=form.duration.data)
        choice = Choices(correct_choice = form.correct_choice.data,incorrect_choice_1=form.incorrect_choice_1.data,incorrect_choice_2=form.incorrect_choice_2.data, incorrect_choice_3=form.incorrect_choice_3.data)
        db.session.add(choice)
        db.session.flush()
        db.session.refresh(choice)
        question.choice_id = choice.id
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully',category='success')
        return redirect(url_for('indexquestions',quiz_id=request.args.get('quiz_id')))
    return render_template('createquestion.html',title='Create a Quiz',form=form,quiz_id=request.args.get('quiz_id'))

@app.route('/updatequestion',methods=['GET','POST'])
def updatequestion():
    if not current_user.role == 'Admin':
        flash('You must be an admin to access this page!',category='info')
        return redirect('home')
    form = UpdateQuestionForm()
    if form.validate_on_submit():
        question = Questions.query.get(request.args.get('question_id'))
        choice = Choices.query.get(question.choice_id)
        choice.correct_choice = form.correct_choice.data
        choice.incorrect_choice_1 = form.incorrect_choice_1.data
        choice.incorrect_choice_2 = form.incorrect_choice_2.data
        choice.incorrect_choice_3 = form.incorrect_choice_3.data
        db.session.commit()
        question.question_statement = form.statement.data
        question.duration = form.duration.data
        db.session.commit()
        flash('Question updated successfully!','success')
        return redirect(url_for('indexquestions',quiz_id=question.quiz_id))
        
    question = Questions.query.get(request.args.get('question_id'))
    form.statement.data = question.question_statement
    form.duration.data = question.duration
    form.correct_choice.data = question.choices.correct_choice
    form.incorrect_choice_1.data = question.choices.incorrect_choice_1
    form.incorrect_choice_2.data = question.choices.incorrect_choice_2
    form.incorrect_choice_3.data = question.choices.incorrect_choice_3
    return render_template('updatequestion.html',title='Update a Question',form=form,quiz_id=question.quiz_id)


@app.route('/indexquestions')
@login_required
def indexquestions():
    if not current_user.role == 'Admin':
        flash('You must be an admin to access this page!',category='info')
        return redirect('home')
    if Questions.query.filter_by(quiz_id=request.args.get('quiz_id')).count() == 0:
        flash('This quiz currently has no questions!','info')
        return redirect('indexquiz')
    return render_template('indexquestions.html',title='Question List',questions = Questions.query.filter_by(quiz_id = request.args.get('quiz_id')),choices= Choices.query.all(),quiz_id=request.args.get('quiz_id'))


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

    page = request.args.get('page',1, int)
    quizzes = Quizzes.query.paginate(per_page = 6,page = page)

    # quizzes_with_questions = []
    # for question in questions:
    #     if not question.id in quizzes_with_questions:
    #         quizzes_with_questions.append(question.quiz_id)
    
    return render_template('allquizzes.html',title='All Quizzes',quizzes=quizzes)

@app.route('/playquiz')
@login_required
def playquiz():
    questions = Questions.query.filter_by(quiz_id=request.args.get('quiz_id'))
    if Questions.query.filter_by(quiz_id=request.args.get('quiz_id')).count() == 0:
        flash('This quiz has no questions added currently, so you cannot play it!','danger')
        return redirect('allquizzes')
    return render_template('quiz.html',questions=questions,title='Playing Quiz',quiz_id=request.args.get('quiz_id'))

#The python's random library cannot be imported inside a jinja template, so we need to create custom
#filter to shuffle the choices inside a template, that's why i have created this function
def filter_shuffle(seq):
    try:
        result = list(seq)
        shuffle(result)
        return result
    except:
        return seq


@app.route('/submitquiz',methods=['GET','POST'])
@login_required
def submitquiz():
    this_attempt = get_this_attempt(request.form.get('quiz_id'))
    questions = Questions.query.filter_by(quiz_id=request.form.get('quiz_id'))
    answers = []
    choices = []
    
    for question in questions:
        try:
            selected_choice = request.form[f'{question.id}']
        except:
            answer = Answers(user_id=current_user.id,question_id=question.id,selected_choice= "Not Attempted",attempt_no=this_attempt)

        else:
            answer = Answers(user_id=current_user.id,question_id=question.id,selected_choice= request.form[f'{question.id}'],attempt_no=this_attempt)

        answers.append(answer)
        choices.append(question.choices)
        db.session.add(answer)
        db.session.commit()
    flash('You finished the quiz!','success')
    percentage=calc_percentage(quiz_id=request.form.get('quiz_id'),attempt=this_attempt)
    return render_template('result.html',percentage=percentage,answers=answers,questions=questions,choices=choices)

#This method takes the quiz_id as an argument and returns the attempt number for the new quiz submitted by the 
#currently logged in user
def get_this_attempt(quiz_id):
    questions = Questions.query.filter_by(quiz_id=quiz_id)
    max_attempts = 0
    has_played = False
    this_attempt = 1
    #the code below will check the previous attempts and appropriately set the value of this attempt
    for question in questions:
        if Answers.query.filter_by(user_id=current_user.id,question_id=question.id).count() > 0:
            has_played = True
            for answer in Answers.query.filter_by(user_id=current_user.id,question_id=question.id):
                if answer.attempt_no > max_attempts:
                    max_attempts = answer.attempt_no
            
    if has_played:
        this_attempt = max_attempts + 1
    return this_attempt


#This function takes the quiz id and attempt number as an argument and returns the percentage of the currently logged in user for that attempt
#of the quiz
def calc_percentage(quiz_id,attempt):
    score = 0
    max_score = 0
    quiz = Quizzes.query.get(quiz_id)
    max_score = 0
    for question in quiz.questions:
        answer = Answers.query.filter_by(user_id=current_user.id,question_id=question.id,attempt_no=attempt).first()
        if answer == None:
            continue
        correct_choice = question.choices.correct_choice
        selected_choice = answer.selected_choice
        max_score = max_score + 1
        if correct_choice == selected_choice:
            score = score + 1
    if score == 0:
        return 0
    
    percentage = (score/max_score)*100
    return percentage

@app.route('/myquizzes')
def myquizzes():
        
        quizzes_played = get_quizzes_played()
        return render_template('myquizzes.html',title='All Quizzes',quizzes=quizzes_played)

def get_quizzes_played():
    quizzes = []
    for answer in Answers.query.all():
            if answer.user_id == current_user.id:
                questions = Questions.query.filter_by(id = answer.question_id)
                for question in questions:
                    quiz = Quizzes.query.get(question.quiz_id)
                    if not quiz.id in quizzes:
                        quizzes.append(quiz.id)
    return Quizzes.query.filter(Quizzes.id.in_(quizzes))

@app.route('/scores')
def scores():
    total_attempts = get_this_attempt(request.args.get('quiz_id')) - 1
    percentages = []
    for attempt in range(1,total_attempts+1):
        percentages.append(calc_percentage(request.args.get('quiz_id'),attempt))
    return render_template('scores.html',percentages = percentages)

@app.route('/createquizfromapi',methods=['GET','POST'])
def createquizfromapi():
    if not current_user.role == 'Admin':
       flash('You must be an admin to access this page!',category='info')
       return redirect('home')
    form = CreateQuizFromApiForm()
    categoryurl = "https://opentdb.com/api_category.php"
    categories = requests.get(categoryurl)
    categories_obj = json.loads(categories.text)
    i = 0
    categories_list = []
    for i in range(len(categories_obj['trivia_categories'])):
        categories_list.append((categories_obj['trivia_categories'][i]['id'],categories_obj['trivia_categories'][i]['name']))
        i = i + 1
    form.category.choices = categories_list

    if form.validate_on_submit() :
        category = request.form.get('category')
        category_name = list(filter(lambda item: item['id'] == int(category), categories_obj['trivia_categories']))
        category_name = category_name[0]['name']
        quiz = Quizzes(quiz_title=form.title.data,quiz_description=form.description.data,quiz_category=category_name,quiz_difficulty=form.difficulty.data,author=current_user.id,date_created=date.today())
        questions_url = "https://opentdb.com/api.php?type=multiple&amount=" + str(form.numques.data) + "&category=" + str(form.category.data) + "&difficulty=" + str.lower(form.difficulty.data)
        questions = requests.get(questions_url)
        questions_obj = json.loads(questions.text)
        if questions_obj['response_code'] == 1:
            flash('Could not retrieve questions, try reducing the amount of questions or change the difficulty', 'danger')
            return redirect('indexquiz')
        db.session.add(quiz)
        db.session.commit()
        db.session.refresh(quiz)
        for j in range(len(questions_obj['results'])):
            correct_choice = questions_obj['results'][j]['correct_answer']
            incorrect_choice_1 = questions_obj['results'][j]['incorrect_answers'][0]
            incorrect_choice_2 = questions_obj['results'][j]['incorrect_answers'][1]
            incorrect_choice_3 = questions_obj['results'][j]['incorrect_answers'][2]
            question = Questions(question_statement=questions_obj['results'][j]['question'],quiz_id=quiz.id,duration=10)
            choice = Choices(correct_choice = correct_choice,incorrect_choice_1=incorrect_choice_1,incorrect_choice_2=incorrect_choice_2, incorrect_choice_3=incorrect_choice_3)
            db.session.add(choice)
            db.session.flush()
            db.session.refresh(choice)
            question.choice_id = choice.id
            db.session.add(question)
            db.session.commit()
        flash('Quiz created from API successfully','success')
        return redirect('indexquiz')
    return render_template('createquizfromapi.html',title='API Quiz Form', form=form)