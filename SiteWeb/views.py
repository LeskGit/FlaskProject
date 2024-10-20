from SiteWeb.command import newuser
from .app import app
from flask import render_template
from .models import get_books_by_author, get_sample, get_author, get_book, loadbook, Author, Book
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired, EqualTo
from flask import url_for, redirect
from .app import db
from wtforms import PasswordField, SubmitField
from .models import User
from hashlib import sha256
from flask_login import login_user, current_user, login_required
from flask import request
from flask_login import logout_user
from .command import loaddb
from wtforms import FileField, SubmitField
from sqlalchemy import or_


class loginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    
    def get_authenticated_user(self):
        user = User.query.get(self.username.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None

class AuthorForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])
    
class BookForm(FlaskForm):
    id = HiddenField('id')
    title = StringField('Nom', validators=[DataRequired()])
    
class BookFormImport(FlaskForm):
    livre = FileField('livre', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                      validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

@app.route ("/")
def home():
    f = BookFormImport()
    return render_template(
        "home.html",
        title="Livre à l'affiche !",
        books=get_sample(),
        form=f)

@app.route("/detail/<id>")
def detail(id):
    books = get_sample()
    book = books[int(id)-1]
    return render_template(
    "detail.html",
    b=book)
    
@app.route("/edit-author/<int:id>")
@login_required
def edit_author(id):
    a = get_author(id)
    books = get_books_by_author(id)
    f = AuthorForm(id=a.id, name=a.name)
    return render_template(
        "edit-author.html",
        author=a,
        form=f,
        books=books
    )
    
@app.route("/add-author/")
def ajout_author():
    f = AuthorForm()  # Crée une instance du formulaire pour l'ajout
    return render_template(
        "add-author.html",
        form=f
    )
    
@app.route("/save/author/", methods=("POST",))
def save_author():
    f = AuthorForm()
    if f.validate_on_submit():
        print(f.id.data)
        id = int(f.id.data)
        a = get_author(id)
        
        if not a:
            return "Veuillez renseignez des champs corrects."
        
        print(f.data)
        if request.form.get('value') == 'Enregistrer':
            a.name = f.name.data
            db.session.commit()
        
        elif request.form.get('value') == 'Supprimer':
            db.session.delete(a)
            db.session.commit()
            return redirect(url_for('home'))  
        
        return redirect(url_for('home'))

    a = get_author(int(f.id.data)) if f.id.data else None
    return render_template("edit-author.html", author=a, form=f)

@app.route("/save/book/", methods=("POST",))
def save_book():
    f = BookForm()
    if f.validate_on_submit():
        id = int(f.id.data)
        b = get_book(id)
        
        if not b:
            return "Veuillez renseignez des champs corrects."
        
        print(f.data)
        if request.form.get('value') == 'Enregistrer':
            b.title = f.title.data
            db.session.commit()
        
        elif request.form.get('value') == 'Supprimer':
            db.session.delete(b)
            db.session.commit()
            return redirect(url_for('home'))  
        
        return redirect(url_for('home'))

    b = get_book(int(f.id.data)) if f.id.data else None
    return render_template("edit-book.html", book=b, form=f)

        
@app.route("/add/author/", methods=("POST",))
def add_author():
    f = AuthorForm()  # Crée une instance du formulaire à partir des données envoyées
    if f.validate_on_submit():
        # Création d'un nouvel auteur sans fournir d'ID, la base de données le générera
        nameA = f.name.data
        author = Author(name=nameA)
        db.session.add(author)  # Ajoute l'auteur à la session de la base de données
        db.session.commit()  # Sauvegarde les modifications dans la base de données
        return redirect(url_for('home'))  # Redirige vers la page de détails de l'auteur
    return render_template("add-author.html", form=f) 

@app.route("/add/book/", methods=("POST",))
def add_book():
    f = BookFormImport()  # Crée une instance du formulaire à partir des données envoyées
    if f.validate_on_submit():
        book = f.livre.data
        loadbook(book)
        return redirect(url_for('home'))  # Redirige vers la page de détails de l'auteur
    return render_template("add-book.html", form=f) 
        
@app.route("/login/",methods=("GET","POST" ,))
def login():
    f = loginForm()
    if f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            return redirect(url_for("home"))
    return render_template(
        "login.html",
        form = f)

@app.route("/register/", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        from .models import User
        from hashlib import sha256
        m = sha256()
        m.update(password.encode())
        u = User(username=username, password=m.hexdigest())
        db.session.add(u)
        db.session.commit()
        
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')

    # Récupérer tous les auteurs correspondant à la requête
    authors = Author.query.filter(Author.name.ilike(f'%{query}%')).all()

    # Récupérer tous les livres correspondant à la requête
    books = Book.query.filter(Book.title.ilike(f'%{query}%')).all()

    if not authors:
        matching_authors = []
    else:
        # Regrouper les auteurs par nom
        grouped_authors = {}
        for author in authors:
            if author.name not in grouped_authors:
                grouped_authors[author.name] = []
            grouped_authors[author.name].append(author)

        # Déterminer l'auteur à afficher
        matching_authors = []
        for author_group in grouped_authors.values():
            if len(author_group) > 1:
                # Plus d'un auteur avec le même nom : choisir celui avec le plus de livres
                author_with_most_books = max(author_group, key=lambda a: a.books.count())
                matching_authors.append(author_with_most_books)
            else:
                # Un seul auteur avec ce nom
                matching_authors.append(author_group[0])

    return render_template('search.html', authors=matching_authors, books=books, query=query)

def perform_advanced_search(search_query, author_id, price_min, price_max):
    # Base query
    query = db.session.query(Book, Author).join(Author)
    
    # Filtrer par mot-clé
    if search_query:
        query = query.filter(or_(
            Book.title.ilike(f'%{search_query}%'),
            Author.name.ilike(f'%{search_query}%')
        ))
    
    # Filtrer par auteur
    if author_id:
        query = query.filter(Book.author_id == author_id)
    
    # Filtrer par prix
    if price_min:
        query = query.filter(Book.price >= price_min)
    if price_max:
        query = query.filter(Book.price <= price_max)
    
    # Récupérer les résultats
    results = query.all()
    return results

@app.route('/advanced-search', methods=['GET', 'POST'])
def advanced_search():
    authors = Author.query.all()  # Récupérer la liste des auteurs
    results = None
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        author_id = request.form.get('author_id')
        price_min = request.form.get('price_min')
        price_max = request.form.get('price_max')
        results = perform_advanced_search(search_query, author_id, price_min, price_max)
    
    return render_template('advanced-search.html', authors=authors, results=results)

@app.route('/authors')
def show_authors():
    authors = Author.query.all()  # Récupérer tous les auteurs de la base de données
    return render_template('authors.html', authors=authors)

@app.route("/author_detail/<int:id>")
def author_details(id):
    a = get_author(id)  # Récupère l'auteur par son ID
    books = get_books_by_author(id)  # Récupère les livres de l'auteur
    return render_template("author-details.html", author=a, books=books)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))