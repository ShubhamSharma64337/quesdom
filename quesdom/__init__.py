from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = '3d8fe3b91e58fdf986035dd27dc1fe5a'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qesdom.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

from quesdom import routes