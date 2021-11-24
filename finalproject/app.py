from flask import Flask, redirect, url_for, render_template, request, flash


# Configure application
app = Flask(__name__)

@app.route("/")
def index():
    return(render_template("index.html"))

@app.route("/buy", methods=["GET", "POST"])
def buy():
    if request.method == "GET":
        return(render_template("buy.html"))
    else:
        return(render_template("buy.html"))

@app.route("/sell", methods=["GET", "POST"])
def sell():
     if request.method == "GET":
        return(render_template("sell.html"))
     else:
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

