from cs50 import SQL
from flask import Flask, request, flash, redirect, render_template, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from random import randint
from translate_dice import translate_d4, translate_d6, translate_d8, translate_d10, translate_d12, translate_d20
from datetime import datetime

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
    return render_template("index.html")

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
    return render_template("account.html", username = session["username"])

@app.route("/games")
def games():
    return render_template("games.html")

@app.route("/games/scrabble")
def scrabble():
    return render_template("scrabble.html")

@app.route("/tools")
def tools():
    return render_template("tools.html")

@app.route("/tools/dice", methods=["GET", "POST"])
def dice():
    if session.get("user_id") is None:
        history = None
    else:   
        history = db.execute(
            "SELECT * FROM dice_history WHERE user_id = ? ORDER BY id DESC LIMIT 5", session.get("user_id")
        )
    if request.method == "POST":
        dice = {'D4': request.form.get("D4"), 'D6': request.form.get("D6"), 'D8': request.form.get("D8"), 'D10': request.form.get("D10"), 'D12': request.form.get("D12"),'D20': request.form.get("D20")}
        D4_results = []
        D4_total = 0
        for i in range(int(dice["D4"])):
            roll = randint(1,4)
            D4_total += roll
            D4_results.append(translate_d4(roll))
        D6_results = []
        D6_total = 0
        for i in range(int(dice["D6"])):
            roll = randint(1,6)
            D6_total += roll
            D6_results.append(translate_d6(roll))
        D8_results = []
        D8_total = 0
        for i in range(int(dice["D8"])):
            roll = randint(1,8)
            D8_total += roll
            D8_results.append(translate_d8(roll))
        D10_results = []
        D10_total = 0
        for i in range(int(dice["D10"])):
            roll = randint(1,10)
            D10_total += roll
            D10_results.append(translate_d10(roll))
        D12_results = []
        D12_total = 0
        for i in range(int(dice["D12"])):
            roll = randint(1,12)
            D12_total += roll
            D12_results.append(translate_d12(roll))
        D20_results = []
        D20_total = 0
        for i in range(int(dice["D20"])):
            roll = randint(1,20)
            D20_total += roll
            D20_results.append(translate_d20(roll))
        if session.get("user_id") is not None:
            db.execute(
                "INSERT INTO dice_history (user_id, date_time, D4, D6, D8, D10, D12, D20) VALUES (?,?,?,?,?,?,?,?)", session["user_id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), D4_total, D6_total, D8_total, D10_total, D12_total, D20_total
            )
        return render_template("dice-roll.html", D4 = D4_results, D6 = D6_results, D8 = D8_results, D10 = D10_results, D12 = D12_results, D20 = D20_results, D4_t = D4_total, D6_t = D6_total, D8_t = D8_total, D10_t = D10_total, D12_t = D12_total, D20_t = D20_total, history = history)
    else:
        return render_template("dice.html", history = history)

@app.route("/tools/keep-scores", methods=["GET", "POST"])
def scores():
    if request.method == "POST":
        player_count = request.form.get("players_count")
        increment = request.form.get("increment")
        players = []
        for i in range(len(request.form.getlist("player_name"))):
            players.append({"name": request.form.getlist("player_name")[i], "score": request.form.getlist("starting_score")[i]})
        print(players)
        return render_template("scores.html", player_count = player_count, increment = increment, players = players)
    else:
        return render_template("scores-setup.html")