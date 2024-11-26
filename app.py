from cs50 import SQL
from flask import Flask, request, flash, redirect, render_template, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///boardgame.db")

def login_required(f):
    # Decorate routes to require login.https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Login required to access this page")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    username = "Not Logged In"
    if session.get("user_id") is not None:
        username = session["username"]
    return render_template("index.html", username = username)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if len(password) < 8:
            flash("Password too short, please try again")
            return redirect("/register")
        i, j = 0, 0
        for char in password:
            if char.isupper() == True:
                i = 1
            if char.isalnum() == False:
                j = 1
        if i == 0 or j == 0:
            flash("Password must include one upper case character and one special character, please try again")
            return redirect("/register")
        try:
            db.execute(
                "INSERT INTO users (username,password_hash) VALUES (?,?)", username, generate_password_hash(password)
                )
            flash("Account created successfully! Please log in")
            return redirect("/login")
        except ValueError:
            flash("Username already exists, please try again")
            return redirect("/register")
    else:
        return render_template("register.html")

    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Error: Please provide a username")
            return redirect("/login")
        elif not request.form.get("password"):
            flash("Error: Please provide a password")
            return redirect("/login")
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        print(rows)
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password_hash"], request.form.get("password")
        ):
            flash("Error: Invalid username and/or password")
            return redirect("/login")
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        flash(session["username"])
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Forget user_id & Redirect to homepage
    session.clear()
    return redirect("/")


@app.route("/account")
@login_required
def account():
    return render_template("account.html")