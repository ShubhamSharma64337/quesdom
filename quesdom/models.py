from datetime import datetime
from quesdom import db

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique=True, nullable= False)
    email = db.Column(db.String(50), unique=True,nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Users({self.user_id}, '{self.username}', '{self.email}', '{self.password}')"

class Quizzes(db.Model):
    quiz_id = db.Column(db.Integer, primary_key = True)
    quiz_title = db.Column(db.String(30), nullable= False)
    quiz_description = db.Column(db.String(200), nullable=False)
    quiz_category = db.Column(db.String(20), nullable=False)
    quiz_difficulty = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Quizzes('{self.quiz_title}', '{self.quiz_description}','{self.quiz_category}','{self.quiz_difficulty}','{self.date_created}')"

class Questions(db.Model):
    question_id = db.Column(db.Integer, primary_key = True)
    question_statement = db.Column(db.String(200), nullable = False)
    choice_id = db.Column(db.Integer, db.ForeignKey('choices.choice_id'), unique=True, nullable = False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id'), nullable = False)
    duration = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"Questions({self.question_id}, '{self.question_statement}',{self.choice_id},{self.quiz_id},{self.duration})"

class Choices(db.Model):
    choice_id = db.Column(db.Integer, primary_key = True)
    correct_choice = db.Column(db.String(50), nullable = False)
    incorrect_choice_1 = db.Column(db.String(50), nullable = False)
    incorrect_choice_2 = db.Column(db.String(50), nullable = False)
    incorrect_choice_3 = db.Column(db.String(50), nullable = False)
    
    def __repr__(self):
        return f"Choices({self.choice_id}, '{self.correct_choice}','{self.incorrect_choice_1}','{self.incorrect_choice_2}','{self.incorrect_choice_3}')"

class Answers(db.Model):
    answer_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),nullable = False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable = False)
    attempt_no = db.Column(db.Integer, nullable = False)
    selected_choice = db.Column(db.String(50), nullable = True)

    def __repr__(self):
        return f"Answers({self.answer_id}, {self.user_id},{self.question_id},{self.attempt_no},'{self.selected_choice}')"
