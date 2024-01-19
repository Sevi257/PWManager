from flask import Flask, request, redirect, session, render_template_string
import os
import sqlite3
import bcrypt
import flask
from flask.sessions import SessionInterface, SessionMixin
import flask_login
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from flask_login import LoginManager, current_user, login_user, login_required
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import logout_user
import database
from database import db
from models import UserDB, Sites
from rdoclient import RandomOrgClient

login_manager = LoginManager()
r = RandomOrgClient("27d32e23-3c59-4136-bc21-500629524fcb")


app = Flask(__name__)

if not os.path.exists("app-secret.key"):
    with open("app-secret.key", "wb") as f:
        f.write(os.urandom(32))

with open("app-secret.key", "rb") as f:
    app.secret_key = f.read()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///C:/Users/sevi1/PycharmProjects/pythonProject3/tmp/test.db'
db.init_app(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate
database.init_db()
login_manager.refresh_view = "/"
login_manager.session_protection = "strong"
PAGE = """
<!doctype html>
<html>
<head>
<title>PasswordManager</title>
<style>
body {
    text-align: center;
}

h1 {
    font-family: sans-serif;
    color: #0065bd;
}
#results {
    margin-top: 10px;
    text-align: left;
}
</style>

</head>

<body>
    <h1><span>Sevis</span>PasswortManager</h1>
    {% if current_user.is_authenticated %}
    <h2>Add Password:</h2>
    <form action="/vault" method="post">
        <input type="text" name="website" placeholder="Website">
        <input type="text" name="username" placeholder="Username">
        <input type="password" name="password" placeholder="Password">
        <input type="submit" value="ADD">
        <a href="{{ url_for('logout') }}">Logout</a>
        <a href="{{ url_for('display') }}">Display</a>
    </form>
    <form action="/random" method="post">
        <a href="{{ url_for('random') }}">Generate RNGPW</a>
    </form>
    {% else %}
    <h2>Backend login:</h2>
    <form action="/" method="post">
        <input type="text" name="username" placeholder="Username">
        <input type="password" name="password" placeholder="Password">
        <input type="submit" value="Login">
        <h3> Add a new User </h3>
        <input type="text" name="newusername" placeholder="NewUsername">
        <input type="password" name="newpassword" placeholder="NewPassword">
        <input type="submit" value="Add">
    </form>
    {% endif %}
</body>
</html>
"""


@app.teardown_appcontext
def shutdown_session(exception=None):
    print("hello")
    database.db_session.remove()
    db.session.remove()


@login_manager.user_loader
def load_user(user_id):
    return UserDB.query.get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/display')
@login_required
def display():
    printDB()
    return redirect('/vault')


def checkMasterUser(provided, salt, hashedpw):
    hashedProvided = bcrypt.hashpw(provided, salt)
    # Vielleicht mit bcrypt.hash
    return hashedProvided == hashedpw


def generateRandomPW(length=12):
    chars = '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
    randomstring = r.generate_strings(1, length, chars)
    return randomstring

def printDB():
    allUsers = db.session.query(UserDB).all()
    allSites = db.session.query(Sites).all()
    print("hello db")
    for user in allUsers:
        if user.__eq__(current_user):
            print(f"User {user.email} with pw: {user.password}")
            for site in allSites:
                if site.user_id.__eq__(user.id):
                    print(f"Sites {site.website} for user: {site.username}")


@app.route("/random", methods=["POST", "GET"])
@login_required
def random():
    print(generateRandomPW())
    flask.flash(generateRandomPW())
    return render_template_string(PAGE, msg=True)

@app.route("/vault", methods=["POST", "GET"])
@login_required
def vault():
    print("Vault")
    if request.method == "POST":
        website = request.form["website"]
        username = request.form["username"]
        password = request.form["password"]
        salz = bcrypt.gensalt()
        pw = bcrypt.hashpw(password.encode(), salz)
        users = db.session.query(UserDB).all()
        for user in users:
            if current_user.__eq__(user):
                entry = Sites(website, username, pw, user_id=user.id)
                db.session.add(entry)
                db.session.commit()
                printDB()
        return render_template_string(PAGE, msg=True)
    else:
        return render_template_string(PAGE, msg=True)


# What actually happens during login
@app.route("/", methods=["POST", "GET"])
def index():
    print(request.form)
    if request.method == "POST":
        if request.form["username"] != '' and request.form["newusername"] != '':
            return redirect("/")
        elif request.form["newusername"] != '':
            # Es soll ein neuer User geadded werden
            # Jetzt Password hashen und dann zusammen mit Salt und Email in DB speicher
            email = request.form["newusername"]
            password = request.form["newpassword"]
            salt = bcrypt.gensalt()
            hashedPW = bcrypt.hashpw(password.encode(), salt)
            u = UserDB(email, hashedPW, salt)
            db.session.add(u)
            db.session.commit()
            return redirect("/")
        else:
            email = request.form["username"]
            password = request.form["password"]
            user = UserDB.query.filter(UserDB.email == email).first()

            if user and checkMasterUser(password.encode(), user.salt, user.password):
                user.authenticated = True
                login_user(user)
                flask.flash("Logged in successfully!")
                return redirect('/vault')
            else:
                flask.flash("Login Failed! ")
                return redirect('/')
    else:
        return render_template_string(PAGE)
