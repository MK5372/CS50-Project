from flask import Flask, redirect, url_for, render_template, request, flash
from cs50 import SQL
import os
from werkzeug.utils import secure_filename


# Configure application
app = Flask(__name__)

db = SQL("sqlite:///finance.db")

upload_folder = "static/uploads/"

app.config['UPLOAD_FOLDER'] = upload_folder

@app.route("/")
def index():
    return(render_template("index.html"))

@app.route("/buy", methods=["GET", "POST"])
def buy():
    if request.method == "GET":
        totalitems = db.execute("SELECT id,location,item,price,description,name FROM listings")
        dictlen = len(totalitems)

        for x in range(dictlen):
           item = db.execute("SELECT item FROM listings WHERE id = ?", x+1)

        return(render_template("buy.html", items = totalitems))
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
        imgsrc = request.form.get("itemimg")

        db.execute("INSERT INTO listings(name, item, location, price, description, imgsrc) VALUES (?,?,?,?,?,?)", name, item, location, price, description, imgsrc)

        f = request.files['itemimg']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))

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


