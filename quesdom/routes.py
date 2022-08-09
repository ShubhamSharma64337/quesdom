from msilib.schema import Class
from flask import render_template,flash,redirect, request, url_for
from quesdom.forms import CreateClassForm, CreateQuizFromApiForm, RegistrationForm, TeacherRegistrationForm, StudentRegistrationForm, LoginForm,CreateQuizForm,CreateQuestionForm, UpdateQuestionForm, CreateJoinRequestForm
from quesdom.models import Classrooms, Questions, Quizzes, Requests, StudentClassroom, Users, Choices, Answers, Teachers, Students, Classrooms
from quesdom import app,bcrypt,db
from flask_login import login_user,current_user,logout_user,login_required
from datetime import date
from random import shuffle
import json
import requests

# Below are the common methods and routes
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html',title='Home')

@app.route('/about')
def about():
    return render_template('about.html',title='About Page')

@app.route('/allquizzes')
def allquizzes():
    page = request.args.get('page',1, int)
    quizzes = Quizzes.query.paginate(per_page = 8,page = page)
    return render_template('allquizzes.html',title='All Quizzes',quizzes=quizzes)

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
                    return redirect('home')
        else:
            flash('Login unsuccessful, please check email and password!','danger')
    return render_template('login.html',title='Login', form=form)
    
@app.route("/register/type", methods=['GET','POST'])
def registertype():
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

    return render_template('register_type.html',title='Register', form=form)


@app.route("/register/teacher", methods=['GET', 'POST'])
def register_teacher():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = TeacherRegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data,email=form.email.data,password = hashed_pw, role='Teacher')
        teacher = Teachers(name = form.name.data)
        db.session.add(teacher)
        db.session.flush()
        db.session.refresh(teacher)

        user.tr_id = teacher.id
        db.session.add(user)
        db.session.commit()

        flash(f'Account Created for {form.username.data}, You can login now!','success')
        return redirect(url_for('login'))

    return render_template('registerteacher.html',title='Register', form=form)
    
@app.route("/register/student", methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data,email=form.email.data,password = hashed_pw, role='Student')
        
        student = Students(name = form.name.data, semester = form.semester.data)
        db.session.add(student)
        db.session.flush()
        db.session.refresh(student)

        user.stu_id = student.id

        db.session.add(user)
        db.session.commit()

        flash(f'Account Created for {form.username.data}, You can login now!','success')
        return redirect(url_for('login'))

    return render_template('registerstudent.html',title='Register', form=form)
    
@app.route("/register/personal", methods=['GET', 'POST'])
def register_personal():
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

#Admin's routes
@app.route('/admin/dashboard')
@login_required
def admindash():
    if current_user.role == 'Admin':
        return render_template('admindash.html',q_played = get_quizzes_played().count())
    return render_template('admindash.html',title='Account')

@app.route('/admin/indexquiz')
@login_required
def admin_indexquiz():
    if not (current_user.role == 'Admin'):
        flash('You are not authorized to access this page!',category='info')
        return redirect('home')

    if Quizzes.query.filter_by(author=current_user.id).count() == 0:
        flash('No quizzes found, please add a quiz!','info')

    page = request.args.get('page',1,int)
    quizzes = Quizzes.query.filter_by(author=current_user.id).paginate(per_page = 5,page=page)

    return render_template('admin_indexquiz.html',title='All Quizzes',quizzes = quizzes)

@app.route('/admin/createquiz',methods=['GET','POST'])
@login_required
def admin_createquiz():
    if not (current_user.role == 'Admin'):
        flash('You are not authorized to access this page!',category='info')
        return redirect('home')

    form = CreateQuizForm()

    if form.validate_on_submit():
        quiz = Quizzes(quiz_title=form.title.data,quiz_category=form.category.data,quiz_difficulty=form.difficulty.data,quiz_description=form.description.data,date_created=date.today(),author=current_user.id,timed=form.timed.data)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully',category='success')
        return redirect('admin_indexquiz')
    return render_template('admin_createquiz.html',title='Create a Quiz',form=form)

@app.route('/admin/createquizfromapi',methods=['GET','POST'])
def admin_createquizfromapi():
    if not current_user.role == 'Admin':
       flash('You must be an admin to access this page!',category='info')
       return redirect('home')
    form = CreateQuizFromApiForm()
    categoryurl = "https://opentdb.com/api_category.php"

    try:
            categories = requests.get(categoryurl)
    except:
            flash('Could not retrieve categories for the create quiz from api form, make sure you are connected to the internet','danger')
            return redirect('admin_indexquiz')

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
            return redirect('admin_indexquiz')
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
        return redirect('admin_indexquiz')
    return render_template('admin_createquizfromapi.html',title='API Quiz Form', form=form)

@app.route('/admin/deletequiz')
@login_required
def admin_deletequiz():
    if not current_user.role == 'Admin':
        flash('You must be an admin to access this page!',category='info')
        return redirect('home')
    
    quiz = Quizzes.query.get(request.args.get('quiz_id'))
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully','success')
    return redirect('admin_indexquiz')

@app.route('/admin/createquestion',methods=['GET','POST'])
@login_required
def admin_createquestion():
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
        return redirect(url_for('admin_indexquestions',quiz_id=request.args.get('quiz_id')))
    return render_template('admin_createquestion.html',title='Create a Quiz',form=form,quiz_id=request.args.get('quiz_id'))

@app.route('/admin/updatequestion',methods=['GET','POST'])
def admin_updatequestion():
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
        return redirect(url_for('admin_indexquestions',quiz_id=question.quiz_id))
        
    question = Questions.query.get(request.args.get('question_id'))
    form.statement.data = question.question_statement
    form.duration.data = question.duration
    form.correct_choice.data = question.choices.correct_choice
    form.incorrect_choice_1.data = question.choices.incorrect_choice_1
    form.incorrect_choice_2.data = question.choices.incorrect_choice_2
    form.incorrect_choice_3.data = question.choices.incorrect_choice_3
    return render_template('admin_updatequestion.html',title='Update a Question',form=form,quiz_id=question.quiz_id)


@app.route('/admin/indexquestions')
@login_required
def admin_indexquestions():
    if not current_user.role == 'Admin':
        flash('You must be an admin to access this page!',category='info')
        return redirect('home')
    if Questions.query.filter_by(quiz_id=request.args.get('quiz_id')).count() == 0:
        flash('This quiz currently has no questions!','info')
        return redirect('admin_indexquiz')
    return render_template('admin_indexquestions.html',title='Question List',questions = Questions.query.filter_by(quiz_id = request.args.get('quiz_id')),choices= Choices.query.all(),quiz_id=request.args.get('quiz_id'))


@app.route('/admin/deletequestion')
@login_required
def admin_deletequestion():
    if not current_user.role == 'Admin':
       flash('You must be an admin to access this page!',category='info')
       return redirect('home')
    question = Questions.query.get(request.args.get('question_id'))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('admin_indexquestions',quiz_id=request.args.get('quiz_id')))

# Teacher's routes and methods
@app.route("/teacher/classrooms")
def teacher_indexclassrooms():
    if not current_user.role == 'Teacher':
        flash('You must be a teacher to access this feature!','danger')
        return redirect('home')
    page = request.args.get('page',1,int)
    classes = Classrooms.query.filter_by(tr_id = current_user.tr_id).paginate(per_page = 5, page = page)
    return render_template('teacher_indexclassrooms.html', title='Classrooms', classes = classes)


@app.route("/teacher/indexstudents")
def teacher_indexstudents():
    if not current_user.role == 'Teacher':
        flash('You must be a teacher to access this feature!','danger')
        return redirect('home')
    students = StudentClassroom.query.filter_by(class_id = request.args.get("class_id"))
    return render_template('teacher_indexstudents.html', title = 'Students', students = students)

@app.route("/teacher/indexrequests")
def teacher_indexrequests():
    if not current_user.role == 'Teacher':
        flash('You must be a teacher to access this feature!','danger')
        return redirect('home')
    requests = Requests.query.filter_by(class_id = request.args.get("class_id"), status = False)
    return render_template('teacher_indexrequests.html', title = "Joining Requests", requests = requests)

@app.route("/teacher/acceptrequest")
def acceptrequest():
    if not current_user.role == 'Teacher':
        flash('You must be a teacher to access this feature!','danger')
        return redirect('home')
    req = Requests.query.get(request.args.get("request_id"))
    req.status = True
    stu_class = StudentClassroom(stu_id = req.stu_id , class_id = req.class_id)
    db.session.add(stu_class)
    db.session.commit()
    flash('Student Added', 'success')
    return redirect(url_for('indexrequests',class_id = req.class_id))

@app.route("/teacher/createclassroom", methods=['GET', 'POST'])
@login_required
def teacher_createclassroom():
    if not current_user.role == 'Teacher':
        flash('You must be a teacher to access this feature!','danger')
        return redirect('home')
    if not current_user.tr_id:
        flash('You must be a teacher to access this page', 'danger')
        return redirect('home')
    form = CreateClassForm()
    if form.validate_on_submit():
        classroom = Classrooms(name=form.name.data,tr_id=current_user.tr_id)
        db.session.add(classroom)
        db.session.commit()
        flash('Class created!', 'success')
        return redirect('teacher_indexclassrooms')
    return render_template('teacher_createclassroom.html', title='Create a Classroom', form = form)

@app.route('/teacher/dashboard')
@login_required
def teacherdash():
    if current_user.role == 'Teacher':
        return render_template('teacherdash.html',q_played = get_quizzes_played().count())
    return render_template('teacherdash.html',title='Account')

@app.route('/teacher/indexquiz')
@login_required
def teacher_indexquiz():
    if not (current_user.role == 'Teacher'):
        flash('You are not authorized to access this page!',category='info')
        return redirect('home')

    if Quizzes.query.filter_by(author=current_user.id).count() == 0:
        flash('No quizzes found, please add a quiz!','info')

    page = request.args.get('page',1,int)
    quizzes = Quizzes.query.filter_by(author=current_user.id).paginate(per_page = 5,page=page)

    return render_template('teacher_indexquiz.html',title='All Quizzes',quizzes = quizzes)

@app.route('/teacher/createquiz',methods=['GET','POST'])
@login_required
def teacher_createquiz():
    if not (current_user.role == 'Teacher'):
        flash('You are not authorized to access this page!',category='info')
        return redirect('home')

    form = CreateQuizForm()

    if not(request.args.get("class_id")): #this checks if the teacher is trying to add quiz without specifying a class which actually
        #adds quizzes to the main Quiz page of website
        flash('You must access this feature through a classroom!','danger')
        return redirect('teacherclassrooms')
    thisclass = Classrooms.query.get(request.args.get("class_id"))
    if not thisclass: #this checks whether the class_id specified by the teacher actually exists in case someone
        #tries to manipulate the url
        flash('This classroom does not exist','danger')
        return redirect('home')
    if not thisclass.tr_id == current_user.tr_id:#this ensures that the quiz will be added to a classroom which
        #belongs to the teacher
        flash('This class does not belong to you','danger')
        return redirect('home')
    
    class_id = request.args.get("class_id")

    if form.validate_on_submit():
        quiz = Quizzes(quiz_title=form.title.data,quiz_category=form.category.data,quiz_difficulty=form.difficulty.data,quiz_description=form.description.data,date_created=date.today(),author=current_user.id,timed=form.timed.data)
        quiz.class_id = class_id
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully',category='success')
        return redirect('teacher_indexquiz')
    return render_template('teacher_createquiz.html',title='Create a Quiz',form=form)

@app.route('/teacher/createquizfromapi',methods=['GET','POST'])
def teacher_createquizfromapi():
    if not current_user.role == 'Teacher':
       flash('You must be an teacher to access this page!',category='info')
       return redirect('home')
    form = CreateQuizFromApiForm()
    categoryurl = "https://opentdb.com/api_category.php"

    try:
            categories = requests.get(categoryurl)
    except:
            flash('Could not retrieve categories for the create quiz from api form, make sure you are connected to the internet','danger')
            return redirect('teacher_indexquiz')

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
            return redirect('teacher_indexquiz')
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
        return redirect('teacher_indexquiz')
    return render_template('teacher_createquizfromapi.html',title='API Quiz Form', form=form)

@app.route('/teacher/deletequiz')
@login_required
def teacher_deletequiz():
    if not current_user.role == 'Teacher':
        flash('You must be a teacher to access this page!',category='info')
        return redirect('home')
    
    quiz = Quizzes.query.get(request.args.get('quiz_id'))
    if not quiz.author == current_user.id:
        flash('You are not authorized to delete this quiz!','danger')
        return redirect('teacher_indexquiz')
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully','success')
    return redirect('teacher_indexquiz')

@app.route('/teacher/createquestion',methods=['GET','POST'])
@login_required
def teacher_createquestion():
    if not current_user.role == 'Teacher':
        flash('You must be an teacher to access this page!',category='info')
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
        return redirect(url_for('teacher_indexquestions',quiz_id=request.args.get('quiz_id')))
    return render_template('teacher_createquestion.html',title='Create a Quiz',form=form,quiz_id=request.args.get('quiz_id'))

@app.route('/teacher/updatequestion',methods=['GET','POST'])
def teacher_updatequestion():
    if not current_user.role == 'Teacher':
        flash('You must be an teacher to access this page!',category='info')
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
        return redirect(url_for('teacher_indexquestions',quiz_id=question.quiz_id))
        
    question = Questions.query.get(request.args.get('question_id'))
    form.statement.data = question.question_statement
    form.duration.data = question.duration
    form.correct_choice.data = question.choices.correct_choice
    form.incorrect_choice_1.data = question.choices.incorrect_choice_1
    form.incorrect_choice_2.data = question.choices.incorrect_choice_2
    form.incorrect_choice_3.data = question.choices.incorrect_choice_3
    return render_template('teacher_updatequestion.html',title='Update a Question',form=form,quiz_id=question.quiz_id)


@app.route('/teacher/indexquestions')
@login_required
def teacher_indexquestions():
    if not current_user.role == 'Teacher':
        flash('You must be an teacher to access this page!',category='info')
        return redirect('home')
    if Questions.query.filter_by(quiz_id=request.args.get('quiz_id')).count() == 0:
        flash('This quiz currently has no questions!','info')
        return redirect('teacher_indexquiz')
    return render_template('teacher_indexquestions.html',title='Question List',questions = Questions.query.filter_by(quiz_id = request.args.get('quiz_id')),choices= Choices.query.all(),quiz_id=request.args.get('quiz_id'))


@app.route('/teacher/deletequestion')
@login_required
def teacher_deletequestion():
    if not current_user.role == 'Teacher':
       flash('You must be an teacher to access this page!',category='info')
       return redirect('home')
    question = Questions.query.get(request.args.get('question_id'))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('teacher_indexquestions',quiz_id=request.args.get('quiz_id')))

#Student's routes and methods
@app.route("/student/indexclassrooms")
def student_indexclassrooms():
    page = request.args.get('page',1,int)
    current_students_classes = []
    for pair in StudentClassroom.query.filter_by(stu_id = current_user.stu_id):
        current_students_classes.append(pair.class_id)
    classes = Classrooms.query.filter(Classrooms.id.in_(current_students_classes)).paginate(per_page = 5, page = page)
    return render_template('student_indexclassrooms.html', title='Classrooms', classes = classes)

@app.route("/student/createjoinrequest",methods=['GET','POST'])
def student_createjoinrequest():
    if not current_user.stu_id:
        flash('You must be a student to access this page', 'danger')
        return redirect('home')
    form = CreateJoinRequestForm()
    if form.validate_on_submit():
        req = Requests(stu_id = current_user.stu_id, class_id = form.class_id.data, status = False)
        if not Classrooms.query.get(form.class_id.data):
            flash('Invalid class ID, please make sure the class ID you enter is correct', 'danger')
            return redirect('student_createjoinrequest')
        db.session.add(req)
        db.session.commit()
        flash('Request submitted it might take some time for your teacher to accept the request!', 'success')
        return redirect('student_indexclassrooms')
    return render_template('student_createjoinrequest.html', title='Join a classroom', form = form)


@app.route('/student/dashboard')
@login_required
def studentdash():
    if current_user.role == 'Student':
        return render_template('studentdash.html',q_played = get_quizzes_played().count())
    return render_template('studentdash.html',title='Account')

#Player's routes and methods
@app.route('/player/dashboard')
@login_required
def playerdash():
    if current_user.role == 'Player':
        return render_template('playerdash.html',q_played = get_quizzes_played().count())
    return render_template('playerdash.html',title='Account')

@app.route('/playquiz')
@login_required
def playquiz():
    questions = Questions.query.filter_by(quiz_id=request.args.get('quiz_id'))
    if Questions.query.filter_by(quiz_id=request.args.get('quiz_id')).count() == 0:
        flash('This quiz has no questions added currently, so you cannot play it!','danger')
        return redirect('allquizzes')
    if not Quizzes.query.get(request.args.get('quiz_id')).timed:
        return render_template('quiz.html', questions=questions,title='Playing Quiz',quiz_id=request.args.get('quiz_id'))
    return render_template('quiztimed.html',questions=questions,title='Playing Quiz',quiz_id=request.args.get('quiz_id'))

@app.route('/myquizzes')
def myquizzes():
        
        quizzes_played = get_quizzes_played()
        return render_template('myquizzes.html',title='My Quizzes',quizzes=quizzes_played)

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
    answercount = 0
    for question in questions:
        try:
            selected_choice = request.form[f'{question.id}']
        except:
            answer = Answers(user_id=current_user.id,question_id=question.id,selected_choice= "Not Attempted",attempt_no=this_attempt)

        else:
            answercount = answercount + 1
            answer = Answers(user_id=current_user.id,question_id=question.id,selected_choice= request.form[f'{question.id}'],attempt_no=this_attempt)

        answers.append(answer)
        choices.append(question.choices)
        db.session.add(answer)
        db.session.commit()
    
    correct_answercount = get_correct_answercount(quiz_id=request.form.get('quiz_id'),attempt=this_attempt)
    flash('You finished the quiz!','success')
    percentage=calc_percentage(quiz_id=request.form.get('quiz_id'),attempt=this_attempt)
    return render_template('result.html',title="Result",correct_answercount = correct_answercount, percentage=int(percentage),answers=answers,answercount = answercount, questions=questions,choices=choices)

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

#This function returns the number of attempted answers which are correct in a quiz for a particular attempt
def get_correct_answercount(quiz_id,attempt):
    quiz = Quizzes.query.get(quiz_id)
    correct_answercount = 0
    for question in quiz.questions:
        answer = Answers.query.filter_by(user_id=current_user.id,question_id=question.id,attempt_no=attempt).first()
        if answer == None:
            continue
        correct_choice = question.choices.correct_choice
        selected_choice = answer.selected_choice
        if correct_choice == selected_choice:
            correct_answercount = correct_answercount + 1
    return correct_answercount

@app.route('/scores')
def scores():
    total_attempts = get_this_attempt(request.args.get('quiz_id')) - 1
    percentages = []
    for attempt in range(1,total_attempts+1):
        percentages.append(calc_percentage(request.args.get('quiz_id'),attempt))
    return render_template('scores.html',percentages = percentages)