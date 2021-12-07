# final project link: https://vault.cs50.io/552eaac7-821c-4a50-b9ec-60220974cd61

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required


# Configure application
app = Flask(__name__)

# declare db
db = SQL("sqlite:///listings.db")

# define path for upload_folder
upload_folder = "static/uploads/"

app.config['UPLOAD_FOLDER'] = upload_folder

# define app secret key - won't affect anything but needs to be defined
app.secret_key = "super secret key"


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return render_template("index2.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Register user"""
    if request.method == "GET":
        return render_template("signup.html")

    # check username and password
    username = request.form.get("username")

    password = request.form.get("password")

    # ensure len is at least 5
    if len(password) < 5:
        return apology("Password insecure. Make it longer")

    # check for nums and letters
    numbers = sum(c.isdigit() for c in password)
    letters = sum(c.isalpha() for c in password)

    # check to make sure at least 2 nums and 2 letters
    if numbers <= 1:
        return apology("Password insecure. Insert at least 2 numeric characters")
    elif letters <= 1:
        return apology("Password insecure. Insert at least 2 alphabetic characters")

    confirmation = request.form.get("confirmation")

    if username == "" or len(db.execute('SELECT username FROM users WHERE username = ?', username)) > 0:
        return apology("Your entered username is already taken or is blank. Please input a different username.")
    if password == "" or password != confirmation:
        return apology("Your entered password doesn't match or is blank. Please input a correct password.")

    # Add new user to users db (includes: username and HASH of password)
    db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
               username, generate_password_hash(password))

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)
    # Log user in, i.e. Remember that this user has logged in
    session["user_id"] = rows[0]["id"]
    # Redirect user to home page
    # db.execute("ALTER )
    return render_template("index2.html")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    # find len of total items
    if request.method == "GET":
        return render_template("delete.html")
    else:
        email = request.form.get("emailauth")
        password = request.form.get("passauth")
        if not email:
            return apology("Incorrect Credentials")
        if not password:
            return apology("Incorrect Credentials")
        if email and password:
            rows = db.execute("SELECT * FROM users WHERE username = ?", email)
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
                return apology("invalid username and/or password", 403)
            else:
                db.execute("DELETE FROM listings WHERE email = ?", email)
        return(render_template("delete.html"))


@app.route("/")
def index():
    return(render_template("index.html"))

# buy function that is from listings


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    # find len of total items
    if request.method == "GET":
        totalitems = db.execute("SELECT * FROM listings")
        dictlen = len(totalitems)
        # define each item so that it can be printed in jinja
        for x in range(dictlen):
            item = db.execute("SELECT item FROM listings WHERE id = ?", x+1)

        return(render_template("buy.html", items=totalitems))
    else:
        return(render_template("delete.html"))


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # return sell template if method = get
    if request.method == "GET":
        return(render_template("sell.html"))
    else:
        # get the information for individual
        name = request.form.get("name")
        email = request.form.get("email")
        item = request.form.get("item").lower()
        location = request.form.get("location")
        price = request.form.get("price")
        description = request.form.get("description")
        f = request.files['itemimg']
        getname = f.filename
        # saves the file into the static uploads folder
        f.save(os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))

        # store everything in the databse
        db.execute("INSERT INTO listings(name, item, location, price, description, imgsrc, email) VALUES (?,?,?,?,?,?,?)",
                   name, item, location, price, description, getname, email)

        return(render_template("sell.html"))


@app.route("/mylistings", methods=["GET", "POST"])
@login_required
def mylistings():
    # need to return template my_listings if its get
    if request.method == "GET":
        return(render_template("mylistings.html"))
    else:
        # change to lower to allow any combination of word in uppercase and lowercase to be found when searching
        useremail = request.form.get("useremail").lower()
        searchitem = request.form.get("product").lower()

        if not useremail and searchitem:
            totalitems = db.execute(
                "SELECT * FROM listings WHERE item = ?", searchitem)
        if useremail and not searchitem:
            totalitems = db.execute(
                "SELECT * FROM listings WHERE email = ?", useremail)
        if useremail and searchitem:
            totalitems = db.execute(
                "SELECT * FROM listings WHERE email =? AND item = ?", useremail, searchitem)

        return(render_template("mylistingspost.html", items=totalitems))


@app.route("/contact", methods=["GET"])
@login_required
def contact():
    # get the contact template
    return(render_template("contact.html"))


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form - Harvard Key Authentication to ensure that it's a harvard student
    # credit to https://cs50.readthedocs.io/vault/
    return redirect("https://vault.cs50.io/552eaac7-821c-4a50-b9ec-60220974cd61")

# handles the errors


def errorhandler(e):
    """Handle error"""
    # credit to finance
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
