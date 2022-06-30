from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '3d8fe3b91e58fdf986035dd27dc1fe5a'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quesdom.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from quesdom import routes