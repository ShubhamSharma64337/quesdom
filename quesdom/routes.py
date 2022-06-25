from flask import render_template,flash,redirect, url_for
from quesdom.forms import RegistrationForm,LoginForm
from quesdom.models import Users,Quizzes,Questions,Answers,Choices
from quesdom import app,bcrypt,db

@app.route('/')
def home():
    return render_template('index.html',title='Home')

@app.route('/about')
def about():
    return render_template('about.html',title='About Page')

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@admin.com' and form.password.data == 'password':
            flash('You have been logged in!','success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful, please check email and password!','danger')
    return render_template('login.html',title='Login', form=form)
    
@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data,email=form.email.data,password = hashed_pw)
        
        db.session.add(user)
        db.session.commit()

        flash(f'Account Created for {form.username.data}, You can login now!','success')
        return redirect(url_for('login'))

    return render_template('register.html',title='Register', form=form)
    
