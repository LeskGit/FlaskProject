from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os.path

# Initialisation de Flask et Bootstrap
app = Flask(__name__)
app. config['BOOTSTRAP_SERVE_LOCAL'] = True
bootstrap = Bootstrap5(app)

# Initialisation de l'authentification des utilisateurs
login_manager = LoginManager(app)

def mkpath (p) -> None:
    """ Permet la création d'un chemin absolu vers la base de donnée

    Args:
        p (str): le chemin vers la base de données
    """
    return os.path. normpath(
        os.path.join(
            os.path.dirname( __file__ ),
            p))
    
# Chargement de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///'+mkpath('../ServWeb.db'))
db = SQLAlchemy(app)

# Configuration d'une clé secrète (pour les sessions utilisateurs)
app.config['SECRET_KEY'] = "524c0dc7-d78d-43f2-91f9-14eff822f086"
