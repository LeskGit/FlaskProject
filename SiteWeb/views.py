from SiteWeb.command import newuser
from .app import app
from flask import render_template
from .models import Review, get_sample, get_author, get_book, loadbook, Author, Book, Genre, get_books_by_author, get_all_author
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, EqualTo, NumberRange
from flask import url_for, redirect
from .app import db
from wtforms import PasswordField, SubmitField
from .models import User
from hashlib import sha256
from flask_login import login_user, current_user, login_required
from flask import request, flash
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
    genre = StringField('Type', validators=[DataRequired()])
    
class BookFormImport(FlaskForm):
    livre = FileField('livre', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                      validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class ReviewForm(FlaskForm):
    rating = IntegerField('Note (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    content = TextAreaField('Votre commentaire', validators=[DataRequired()])
    submit = SubmitField('Envoyer')

@app.route ("/")
def home():
    f = BookFormImport()
    # Nombre de livres par page
    page_lim = 30
    # Récupérer le numéro de page à partir de l'URL, par défaut à 1 pour eviter les erreurs
    page = request.args.get('page', 1, type=int)
    
    # Calculer l'offset pour la requête
    offset = (page - 1) * page_lim
    
    # Récupérer les livres pour la page actuelle
    books = Book.query.limit(page_lim).offset(offset).all()
    
    # Compter le nombre total de livres
    total_books = Book.query.count()
    
    # Calculer le nombre total de pages
    total_pages = (total_books + page_lim - 1) // page_lim  # Arrondi vers le haut


    return render_template(
        "home.html",
        title="Livre à l'affiche !",
        form=f,
        books=books,
        page=page,
        total_pages=total_pages)

@app.route("/detail/<int:id>", methods=["GET", "POST"])
def detail(id):
    book = get_book(id)
    if book is None:
        return "Livre non trouvé.", 404

    form = ReviewForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Vous devez être connecté pour laisser un commentaire.")
            return redirect(url_for('login'))

        # Créer un nouvel objet Review
        review = Review(
            content=form.content.data,
            rating=form.rating.data,
            user_id=current_user.username,
            book_id=book.id
        )
        db.session.add(review)
        db.session.commit()
        flash("Votre commentaire a été ajouté.")
        return redirect(url_for('detail', id=book.id))

    # Calculer la note moyenne
    average_rating = db.session.query(db.func.avg(Review.rating)).filter_by(book_id=book.id).scalar()
    if average_rating:
        average_rating = round(average_rating, 2)

    # Récupérer les commentaires associés au livre
    reviews = Review.query.filter_by(book_id=book.id).order_by(Review.timestamp.desc()).all()

    return render_template(
        "detail.html",
        book=book,
        form=form,
        reviews=reviews,
        average_rating=average_rating
    )
    
@app.route("/edit-author/<int:id>")
@login_required
def edit_author(id):
    a = get_author(id)
    books = get_books_by_author(id)
    f = AuthorForm(id=a.id, name=a.name)
    return render_template(
        "edit-author.html",
        author=a, form = f)

@app.route("/edit-book/<int:id>")
def edit_book(id):
    a = get_book(id)
    f = BookForm(id=a.id, title=a.title, genre = a.genre)
    return render_template(
        "edit-book.html",
        book=a, form = f)
    
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
        id = int(f.id.data)
        a = get_author(id)
        
        
        if not a:
            return "Veuillez renseignez des champs corrects."
        
        print(f.data)
        if request.form.get('submit') == 'Enregistrer':
            print("gg")
            a.name = f.name.data
            db.session.commit()
            return redirect(url_for('home'))
        
        elif request.form.get('submit') == 'Supprimer':
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
            genre_obj = Genre.query.filter_by(name=f.genre.data).first()
            if genre_obj is None:
                genre_obj = Genre(name=f.genre.data)
                db.session.add(genre_obj)
            b.genre = genre_obj
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

@app.route('/add_to_favorites/<int:book_id>', methods=['POST'])
@login_required
def add_to_favorites(book_id):
    book = get_book(book_id)
    if book is None:
        return "Livre non trouvé.", 404

    if book in current_user.favorites:
        flash('Ce livre est déjà dans vos favoris.')
    else:
        current_user.favorites.append(book)
        db.session.commit()
        flash('Livre ajouté à vos favoris.')

    return redirect(url_for('detail', id=book_id))

@app.route('/remove_from_favorites/<int:book_id>', methods=['POST'])
@login_required
def remove_from_favorites(book_id):
    book = get_book(book_id)
    if book is None:
        return "Livre non trouvé.", 404

    if book in current_user.favorites:
        current_user.favorites.remove(book)
        db.session.commit()
        flash('Livre retiré de vos favoris.')
    else:
        flash('Ce livre n\'est pas dans vos favoris.')

    return redirect(url_for('detail', id=book_id))

@app.route('/favorites')
@login_required
def favorites():
    user_favorites = current_user.favorites
    return render_template('favorites.html', books=user_favorites)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))