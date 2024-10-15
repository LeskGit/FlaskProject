import yaml, os.path
from .app import db
from flask_login import UserMixin
from .app import login_manager

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)


class User(db.Model, UserMixin):
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(64))
    
    def get_id(self):
        return self.username
    


class Author(db.Model):
    """
    Représente un auteur dans la base de données
    """
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100))
    
    def __repr__ (self) -> str:
        """ Permet de gérer l'affichage d'un auteur

        Returns:
            str: l'id et le nom d'un auteur
        """
        return "<Author (%d) %s>" % (self.id , self.name)
    
class Book(db.Model):
    """
    Représente un livre dans la base de données
    """
    id = db.Column(db.Integer, primary_key = True)
    price = db.Column(db.Float)
    url = db.Column(db.String(200))
    img = db.Column(db.String(200))
    title = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
    author = db.relationship("Author", backref=db.backref("books", lazy="dynamic"))
    
    def __repr__ (self ):
        """ Permet de gérer l'affichage d'un livre
        Returns:
            str: l'id et le titre du livre
        """
        return "<Book (%d) %s>" % (self.id , self.title)
    

def get_sample() -> list[Book]:
    """ retourne tous les livres

    Returns:
        List[Book]: une liste de livres
    """
    return Book.query.all() 



def get_author(id : int) -> Author:
    """ Renvoie l'auteur associé à l'id entré en paramètre

    Args:
        id (int): un id

    Returns:
        Author: un auteur
    """
    return Author.query.get(id)  # Utilisez .get() pour obtenir l'auteur par son ID
