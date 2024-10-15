
from .app import app
from flask import render_template

# Config de la route correspondant au Home de l'app

@app.route("/")
def home():
    return render_template(
        "home.html",
        title="Hello World")