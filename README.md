# FlaskProject

### Devs : 
Axel MEUNIER
Corentin THUAULT

### Lien du git 

https://github.com/LeskGit/FlaskProject.git

## Web server with Flask python.

### Installation : 

- Ouvrez un terminal.
- Utilisez la commande **virtualenv -p python3 venv**.
- Utilisez la commande **source venv/bin/activate**.
Vous êtes maintenant dans votre virtualenv.
- Déplacez-vous dans le dossier `FlaskProject`.
- Utilisez la commande **pip install -r requirements.txt**.
Vous êtes maintenant prêt à lancer l'application.

### Lancement :

- Lancez votre virtualenv.
- Déplacez-vous dans le dossier `FlaskProject`.
- Utilisez la commande **flask loaddb SiteWeb/data/data.yml**
- Utilisez la commande **flask syncdb**
- Utilisez la commande **FLASK_APP=SiteWeb/app.py flask run**.
Vous n'aurez besoin d'utiliser cette commande qu'une seule fois. Si vous souhaitez relancer l'application, utilisez simplement **flask run**.

### Fonctionnalités ajoutées :
