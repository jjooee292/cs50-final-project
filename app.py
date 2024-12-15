from cs50 import SQL
from flask import Flask, request, flash, redirect, render_template, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from random import randint
from translate_dice import translate_d4, translate_d6, translate_d8, translate_d10, translate_d12, translate_d20
from datetime import datetime
from scrabble import blanks, triple_letter, double_letter, triple_word, double_word
import json

# Config Wordnik API
from wordnik import *
apiUrl = 'http://api.wordnik.com/v4'
apiKey = '2bqocrwqkfk7jetq0a4kz6c51dwmro7olaj8sc5ukx2k4fhxb'
client = swagger.ApiClient(apiKey, apiUrl)
wordApi = WordApi.WordApi(client)

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

@app.route("/games/monopoly", methods=["GET", "POST"])
@login_required
def monopoly():
    if request.method == "POST":
        players = []
        for i in range(len(request.form.getlist("player_name"))):
            players.append({"player_name": request.form.getlist("player_name")[i], "cash": 1500, "houses": "0", "hotels": "0"})
        return render_template("monopoly.html", players = players)
    else:
        return render_template("monopoly-setup.html")
    
@app.route("/games/monopoly/load", methods=["GET", "POST"])
@login_required
def monopoly_load():
    if request.method == "POST":
        players = db.execute (
            "SELECT * FROM monopoly WHERE user_id = ? AND session_id = ?", session.get("user_id"), int(request.form.get("load_file"))
        )
        for i in players:
            i["cards"] = json.loads(i["cards"])
        print(players)
        return render_template("monopoly.html", players = players)
        ## TO DO: handle the ticking of property boxes owned by player upon load with some javascript or jinja code 
    else:
        saves = db.execute (
            "SELECT * FROM monopoly WHERE user_id = ? ORDER BY session_id DESC", session.get("user_id")
        )
        for i in saves:
            i["cards"] = json.loads(i["cards"])
        return render_template("monopoly-load.html", saves=saves)

@app.route("/games/monopoly/save", methods=["POST"])
@login_required
def monopoly_save():
    name = []
    cash = []
    cards = []
    houses = []
    hotels = []
    for i in range(len(request.form.getlist("player_name"))):
        name.append(request.form.getlist("player_name")[i])
        cash.append(request.form.getlist("cash_submit")[i])
        houses.append(request.form.getlist("houses_submit")[i])
        hotels.append(request.form.getlist("hotels_submit")[i])
        fStringName = request.form.getlist("player_name")[i]
        cards.append(request.form.getlist(f"cards_{fStringName}"))
    db.execute(
        "INSERT INTO monopoly_sessions (user_id, date_time) VALUES (?,?)", session.get("user_id"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    monopoly_session_id = db.execute(
        "SELECT id FROM monopoly_sessions WHERE user_id = ? ORDER BY date_time DESC LIMIT 1", session.get("user_id")
    )[0]["id"]
    for i in range(len(name)):
        db.execute(
            "INSERT INTO monopoly (user_id, player_name, cash, cards, houses, hotels, session_id) VALUES (?,?,?,?,?,?,?)", session.get("user_id"), name[i], cash[i], json.dumps(cards[i]), houses[i], hotels[i], monopoly_session_id
        )
    flash("Monopoly game saved successfully")
    return redirect("/")

@app.route("/games/scrabble", methods=["GET", "POST"])
def scrabble():
    if request.method == "POST":
        word = request.form.get("word").lower()
        try:
            result = wordApi.getScrabbleScore(word).value
            modified_result = result
            if request.form.get("blank"): 
                for i in blanks(request.form.get("blank")):
                    modified_result = modified_result - i
            if request.form.get("dbl-ltr"):
                for i in double_letter(request.form.get("dbl-ltr")):
                    modified_result = modified_result + i
            if request.form.get("trb-ltr"):
                for i in triple_letter(request.form.get("trb-ltr")):
                    modified_result = modified_result + i
            if request.form.get("dbl-wrd"):
                modified_result = double_word(modified_result)
            if request.form.get("trb-wrd"):
                modified_result = triple_word(modified_result)
            print(result)
            print(modified_result)
        except:
            result = "Invalid Word"
            modified_result = "Invalid Word"
            print(result)
            print(modified_result)
        return render_template("scrabble.html", word=result, score=modified_result)
    else:
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
        return render_template("scores.html", player_count = player_count, increment = increment, players = players)
    else:
        return render_template("scores-setup.html")
    
@app.route("/tools/timer", methods=["GET", "POST"])
def timer():
    if request.method == "POST":
        hours = int(request.form.get("hours"))
        print(int(hours))
        if int(hours) < 10:
            hours = f"0{hours}"
        mins = int(request.form.get("mins"))
        if int(mins) < 10:
            mins = f"0{mins}"
        secs = int(request.form.get("secs"))
        if int(secs) < 10:
            secs = f"0{secs}"
        audio = request.form.get("timer-chime")
        return render_template("timer.html", hours = hours, mins = mins, secs = secs, audio=audio)
    else:
        return render_template("timer-setup.html")