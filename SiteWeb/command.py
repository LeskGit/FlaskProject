import click
from .app import app, db

@app.cli.command()
@click.argument('filename')

def loaddb(filename : str) -> None:
    """ Permet de charger des données dans les tables 
        authors et books à d'un fichier YAML
    Args:
        filename (str): le chemin du fichier YAML
    """
    db.create_all()
    
    import yaml
    books = yaml.safe_load(open(filename))
    
    from .models import Author, Book
    
    authors = {}
    for b in books:
        a = b["author"]
        if a not in authors:
            o = Author(name=a)
            db.session.add(o)
            authors[a] = o
    db.session.commit()
    
    for b in books:
        a = authors[b["author"]]
        o = Book(price = b["price"],
                title = b["title"],
                url = b["url"] ,
                img = b["img"] ,
                author_id = a.id)
        db.session.add(o)
    db.session.commit()
    
@app.cli.command()
def syncdb() -> None:
    """ 
    Permet de créer les différentes table de la base de donnée
    """
    db.create_all()

@app.cli.command()
@click.argument('username')
@click.argument('password')
def newuser(username, password):
    """ Enregistre dans la base un nouvel utilisateur associé à un mot de passe
    Args:
        username (str): le nom de l'utilisateur
        password (str): le mot de passe de l'utilisateur
    """
    from .models import User
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    u = User(username=username, password=m.hexdigest())
    db.session.add(u)
    db.session.commit()
    
@app.cli.command()
@click.argument('username')
@click.argument('password')
def passwd(username, password):
    """Update psswd"""
    from .models import User
    from hashlib import sha256
    
    u = User.get_id(username)

    m = sha256()
    m.update(password.encode())
    u.update(password=m.hexdigest())
    db.session.add(u)
    db.session.commit()