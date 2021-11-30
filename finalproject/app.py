from flask import Flask, redirect, url_for, render_template, request, flash
from cs50 import SQL


# Configure application
app = Flask(__name__)

db = SQL("sqlite:///finance.db")

@app.route("/")
def index():
    return(render_template("index.html"))

@app.route("/buy", methods=["GET", "POST"])
def buy():
    if request.method == "GET":
        totalitems = db.execute("SELECT id FROM listings")
        dictlen = len(totalitems)

        for x in range(dictlen):
           item = db.execute("SELECT item FROM listings WHERE id = ?", x)

        return(render_template("buy.html",item=item))
    else:
        return(render_template("buy.html"))

@app.route("/sell", methods=["GET", "POST"])
def sell():
     if request.method == "GET":
        return(render_template("sell.html"))
     else:
        name = request.form.get("name")
        item = request.form.get("item")
        location = request.form.get("location")
        price = request.form.get("price")
        description = request.form.get("description")
        db.execute("INSERT INTO listings(name, item, location, price, description) VALUES (?,?,?,?,?)", name, item, location, price, description)

        return(render_template("sell.html"))

@app.route("/profile", methods=["GET", "POST"])
def profile():
     if request.method == "GET":
        return(render_template("profile.html"))
     else:
        return(render_template("profile.html"))

@app.route("/contact", methods=["GET", "POST"])
def contact():
     if request.method == "GET":
        return(render_template("contact.html"))
     else:
        return(render_template("contact.html"))
@app.route("/signup", methods=["GET", "POST"])
def signup():
   if request.method == "GET":
        return(render_template("signup.html"))
   else:
        return(render_template("signup.html"))


