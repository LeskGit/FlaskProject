from datetime import datetime
import yaml, os.path
from .app import db
from flask_login import UserMixin
from .app import login_manager

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

favorites = db.Table('favorites',
    db.Column('user_id', db.String(50), db.ForeignKey('user.username'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(64))
    favorites = db.relationship('Book', secondary='favorites', backref='favorited_by')
    
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
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    url = db.Column(db.String(200))
    img = db.Column(db.String(200))
    title = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
    genre_id = db.Column(db.String(100), db.ForeignKey("genre.name"), default="Aucun") 
    author = db.relationship("Author", backref=db.backref("books", lazy="dynamic"))
    genre = db.relationship("Genre", backref=db.backref("books", lazy="dynamic"))

    
    def __repr__ (self ):
        """ Permet de gérer l'affichage d'un livre
        Returns:
            str: l'id et le titre du livre
        """
        return "<Book (%d) %s>" % (self.id , self.title)
    
class Genre(db.Model):
    """
    Représente un livre dans la base de données
    """
    name = db.Column(db.String(200), primary_key = True)
    
    
    def __repr__ (self ):
        """ Permet de gérer l'affichage d'un genre
        Returns:
            str: le nom du genre
        """
        return self.name
    

    

def get_sample() -> list[Book]:

    """ retourne tous les livres


    Returns:
        List[Book]: une liste de livres
    """
    return Book.query.limit(10).all() 

def get_all_author() -> list[Book]:

    """ retourne tous les auteurs


    Returns:
        List[Author]: une liste d'auteurs
    """
    return Author.query.all() 



def get_author(id : int) -> Author:
    """ Renvoie l'auteur associé à l'id entré en paramètre

    Args:
        id (int): un id

    Returns:
        Author: un auteur
    """
    return Author.query.get(id)  # Utilisez .get() pour obtenir l'auteur par son ID

def get_book(id : int) -> Book:
    """ Renvoie l'auteur associé à l'id entré en paramètre

    Args:
        id (int): un id

    Returns:
        Author: un auteur
    """
    return Book.query.get(id)  # Utilisez .get() pour obtenir le livre par son ID

def loadbook(file) -> None:
    """ Permet de charger des données dans les tables 
        authors et books à d'un fichier YAML
    Args:
        file: le fichier YAML en tant qu'objet de fichier
    """
    
    try:
        import yaml
        # Chargement du contenu YAML
        book = yaml.safe_load(file.read())  
        
        # Récupération de tous les auteurs
        authors = get_all_author()
        
        # Récupération de l'auteur du livre
        author_name = book[0]["author"]
        
        # Vérification de l'existence de l'auteur
        if not any(a.name == author_name for a in authors):
            print(f"Creating new author: {author_name}")
            o = Author(name=author_name)  # Utilisation de name pour le constructeur
            db.session.add(o)
            db.session.commit()
        
        print("Author check passed")
        
        # Récupération de l'auteur ajouté
        author = Author.query.filter_by(name=author_name).first()
        
        # Création d'une nouvelle entrée pour le livre
        b = Book(price=book[0]["price"],
                 title=book[0]["title"],
                 url=book[0]["url"],
                 img=book[0]["img"],
                 author_id=author.id)
        # Ajout du livre à la session et sauvegarde dans la BD
        db.session.add(b)
        db.session.commit()
    
    except Exception as e:
        print(f"Erreur lors de l'import du livre dans la BD: {e}")

def get_books_by_author(author_id):
    return Book.query.filter_by(author_id=author_id).all()

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  
    rating = db.Column(db.Integer, nullable=False)  
    timestamp = db.Column(db.DateTime, default=datetime.now) 

    user_id = db.Column(db.String(50), db.ForeignKey('user.username'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('reviews', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('reviews', lazy='dynamic'))

    def __repr__(self):
        return f"<Review {self.id} by {self.user_id} on book {self.book_id}>"


