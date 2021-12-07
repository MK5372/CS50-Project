#final project link: https://vault.cs50.io/552eaac7-821c-4a50-b9ec-60220974cd61

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology


# Configure application
app = Flask(__name__)

#declare db
db = SQL("sqlite:///finance.db")

#define path for upload_folder
upload_folder = "static/uploads/"

app.config['UPLOAD_FOLDER'] = upload_folder

#define app secret key - won't affect anything but needs to be defined
app.secret_key = "super secret key"

@app.route("/")
def index():
    return(render_template("index.html"))

#buy function that is from listings
@app.route("/buy", methods=["GET", "POST"])
def buy():
    #find len of total items
    if request.method == "GET":
        totalitems = db.execute("SELECT * FROM listings")
        dictlen = len(totalitems)
        #define each item so that it can be printed in jinja
        for x in range(dictlen):
            item = db.execute("SELECT item FROM listings WHERE id = ?", x+1)

        return(render_template("buy.html", items=totalitems))
    else:
        return(render_template("buy.html"))


@app.route("/sell", methods=["GET", "POST"])
def sell():
    #return sell template if method = get
    if request.method == "GET":
        return(render_template("sell.html"))
    else:
        #get the information for individual
        name = request.form.get("name")
        email = request.form.get("email")
        item = request.form.get("item")
        location = request.form.get("location")
        price = request.form.get("price")
        description = request.form.get("description")
        f = request.files['itemimg']
        getname = f.filename
        #saves the file into the static uploads folder
        f.save(os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))

        #store everything in the databse
        db.execute("INSERT INTO listings(name, item, location, price, description, imgsrc, email) VALUES (?,?,?,?,?,?,?)",
                   name, item, location, price, description, getname, email)

        return(render_template("sell.html"))


@app.route("/mylistings", methods=["GET", "POST"])
def mylistings():
    #need to return template my_listings if its get
    if request.method == "GET":
        return(render_template("mylistings.html"))
    else:
    #ask for user email and select listings from database to show
        useremail = request.form.get("useremail")
        totalitems = db.execute(
            "SELECT * FROM listings WHERE email = ?", useremail)
        dictlen = len(totalitems)

        #loop through len of totalitems to list everything
        for x in range(dictlen):
            item = db.execute("SELECT item FROM listings WHERE id = ?", x+1)

        return(render_template("mylistingspost.html",items=totalitems))


@app.route("/contact", methods=["GET", "POST"])
def contact():
    #get the contact template
    if request.method == "GET":
        return(render_template("contact.html"))
    else:
        return(render_template("contact.html"))


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form - Harvard Key Authentication to ensure that it's a harvard student
    return redirect("https://vault.cs50.io/552eaac7-821c-4a50-b9ec-60220974cd61")

#handles the errors
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
