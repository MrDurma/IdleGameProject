import re
import datetime

import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
#from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

from helpers import error, login_required, usd, building_name, building_price, building_time
from generator import building_income, update_busy_status

# TODO: make index.html look better, make new building models and background picture.

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure application to use SQLite database
data = sqlite3.connect('data.db', check_same_thread=False)
# https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
data.row_factory = sqlite3.Row
db = data.cursor()

building_income()
update_busy_status()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Check if user entered username
        if not request.form.get("username"):
            return error("You must enter the username", 401)

        # Check if user entered password
        elif not request.form.get("password"):
            return error("You must enter the password", 401)

        # Query database for username
        db.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
        rows = db.fetchall()
        # Ensure username exists
        if len(rows) == 0:
            return error("Incorrect username and/or password", 403)

        # Ensure username exists and password is correct
        for row in rows:
            if len(rows) != 1 or not check_password_hash(row[2], request.form.get("password")):
                return error("Incorrect username and/or password", 403)
            # Remember which user has logged in
            session["user_id"] = row[0]
            session["username"] = row[1]

            # Redirect user to home page
            return redirect("/")

    else:
        return render_template("login.html")

# For now this app requires only name and password to create an account.
# TODO: add email requirement and email confirmation code to improve security.
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Check if user entered username
        if not request.form.get("username"):
            return error("You must enter the username", 401)

        # Check if user entered password
        elif not request.form.get("password"):
            return error("You must enter the password", 401)
        # Check if password and confirmation password matche
        elif request.form.get("password") != request.form.get("confirmation"):
            return error("passwords must match!", 401)

        # Check if password is at least 5 characters long
        elif len(request.form.get("password")) < 5:
            return error("Password must be at least 6 characters long", 401)

        # Checking if password has 1 number
        elif re.search('[0-9]', request.form.get("password")) is None:
            return error("Password must contain at least 1 number.", 401)

        # Query database for username
        db.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
        dupe = db.fetchall()

        # Ensure username isn't taken
        if len(dupe) != 0:
            return error("username already exists", 401)

         # Registering new user and hashing the password.
        else:
            db.execute("INSERT INTO users(username, hash) values(?, ?)", 
                       (request.form.get("username"), 
                       generate_password_hash(request.form.get("password"), 
                       method='pbkdf2:sha256', salt_length=8)))
            data.commit()

            # Keep user logged in after registering.
            db.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
            rows = db.fetchall()
            session["user_id"] = rows[0]["user_id"]
            session["username"] = rows[0]["username"]


            # Adding default buildings (slots 1, 2, 3, 4, 5, 6) to db for given user upon registration.
            for counter in range(1, 7):
                db.execute("INSERT INTO buildings(user_id, b_slot) VALUES(?, ?)", 
                           (session["user_id"], counter))
                data.commit()
        # Redirect user to home page
        return redirect("/")

    # request.method == "GET"
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/map", methods=["GET", "POST"])
@login_required
def game_map():
    """ Game map """
    db.execute("""
        SELECT username, money, experience, level, max_b
        FROM users 
        WHERE user_id=?
    """, [session["user_id"]])
    user_info = db.fetchall()
    db.execute("""
        SELECT * 
        FROM buildings 
        WHERE user_id=? 
        ORDER BY b_slot
    """, [session["user_id"]])
    binfo = db.fetchall()
    db.execute("SELECT * FROM test")
    test = db.fetchall()
    time_left = {}
    for building in binfo:
        if building["is_busy"] == 1:
            time_left[building["b_id"]] = str(datetime.strptime(building["busy_until"], 
                                              "%Y-%m-%d %H:%M:%S") - datetime.now())
            #time_left[building] = datetime.strptime(time_left[building["b_id"]], "%H:%M:%S")

    return render_template("map.html", user_info=user_info, 
                           binfo=binfo, test=test, time_left=time_left)

@app.route("/headquarters", methods=["GET", "POST"])
@login_required
def headquarters():
    """ Displays inventory to user"""
    #TODO: add more info to display to user
    if request.method == "GET":
        return render_template("headquarters.html")

@app.route("/build", methods=["POST"])
@login_required
def build():
    """ Handles building on map """
    if request.method == "POST":
        db.execute("SELECT * FROM buildings WHERE b_id=?", (request.form.get("b_id") ,))
        building = db.fetchone()
        if building:
            if (session["user_id"] == building["user_id"]):
                db.execute("SELECT money FROM users WHERE user_id=?", (building["user_id"] ,))
                user_money = db.fetchone()
                b_type = request.form.get("b_type")
                b_name = building_name(b_type)
                price = building_price(b_type)
                if user_money[0] < price:
                    return error("You can't afford this building", 401)
                build_time = building_time(b_type, 1)
                build_time = datetime.now() + timedelta(minutes = build_time)
                db.execute("""
                    UPDATE buildings 
                    SET b_type=?, b_name=?, status='Constructing', is_busy=1, busy_until=? 
                    WHERE b_id=?
                """, (b_type, b_name, build_time.strftime("%Y-%m-%d %H:%M:%S"), 
                          request.form.get("b_id")))
                data.commit()
                db.execute("UPDATE users SET money=money-? WHERE user_id=?", 
                           (price, session["user_id"]))
                data.commit()
                return redirect("/map")
                
        return error("You can't build selected building", 401)

@app.route("/b/<b_id>", methods = ["GET", "POST"])
@login_required
def b(b_id):
    """ Shows building menu when user selects building """
    if request.method == "POST":
        return redirect("/map")
    else:
        db.execute("SELECT * FROM buildings WHERE b_id=?", (b_id ,))
        b_info = db.fetchone()
        price = building_price(b_info["b_type"])
        time = building_time(b_info["b_type"])
        return render_template("/b/b.html", b_id=b_id, b_info = b_info, price=price, time=time)

@app.route("/upgrade", methods = ["POST"])
@login_required
def upgrade():
    """ Handles upgrading buildings """
    if request.method == "POST":
        b_id = request.form.get("hidden")

        # Making sure user didn't change b_id to illegal value. Code below executes only if
        # b_id is linked to correct user_id.
        db.execute("SELECT * FROM buildings WHERE b_id=?", (b_id,))
        building = db.fetchone()
        if building:
            if (session["user_id"] == building["user_id"]) or (building["is_busy"] == 0):

                 
                db.execute("SELECT money FROM users WHERE user_id=?",(building["user_id"],))
                user_money = db.fetchone()
                user_money = int(user_money[0])
                upgrade_price = building_price(building["b_type"], building["b_lvl"])
                if user_money < upgrade_price:
                    return error("You don't have enough money", 401)

                upgrade_time = building_time(building["b_type"], building["b_lvl"])
                upgrade_time = datetime.now() + timedelta(hours = upgrade_time)
                db.execute("""
                    UPDATE buildings 
                    SET busy_until=?, is_busy=1, status='Upgrading' 
                    WHERE b_id=?
                """, (upgrade_time.strftime("%Y-%m-%d %H:%M:%S"), building["b_id"]))
                data.commit()
                db.execute("UPDATE users SET money=money-? WHERE user_id=?",
                           (upgrade_price, building["user_id"]))
                data.commit()
                return redirect("/map")
        return error("Upgrading this building is not possible", 401)

@app.route("/deconstruct", methods = ["POST"])
@login_required
def deconstruct():
    """ Handles deconstructing buildings """
    if request.method == "POST":
        b_id = request.form.get("hidden")

        # Making sure user didn't change b_id to illegal value. Code below executes only if
        # b_id is linked to correct user_id.
        db.execute("SELECT * FROM buildings WHERE b_id=?", (b_id,))
        building = db.fetchone()
        if building:
            if (session["user_id"] == building["user_id"]) or (building["is_busy"] == 0):
                db.execute("""
                    UPDATE buildings 
                    SET b_type='Empty', b_lvl='1', b_name='Empty' 
                    WHERE b_id=?
                """, (building["b_id"] ,))
                data.commit()
                return redirect("/map")
        return error("Deconstructing this building is not possible", 401)

@app.route("/test", methods=["GET", "POST"])
def test():
    return render_template("test.html")

