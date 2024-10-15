from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os.path


app = Flask(__name__)
app. config['BOOTSTRAP_SERVE_LOCAL'] = True
bootstrap = Bootstrap5(app)
login_manager = LoginManager(app)

def mkpath (p):
    return os.path. normpath(
        os.path.join(
            os.path.dirname( __file__ ),
            p))
    

app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///'+mkpath('../FlaskProject.db'))
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = "524c0dc7-d78d-43f2-91f9-14eff822f086"
