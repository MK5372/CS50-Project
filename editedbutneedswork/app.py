from flask import Flask, redirect, url_for, render_template, request, flash
from cs50 import SQL
import os
from werkzeug.utils import secure_filename

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

db = SQL("sqlite:///finance.db")

upload_folder = "static/uploads/"

app.config['UPLOAD_FOLDER'] = upload_folder

# (Receive token by HTTPS POST)
# ...

@app.route("/")
@login_required
def index():
    return(render_template("index.html"))

@app.route("/buy", methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
def profile():
     if request.method == "GET":
        return(render_template("profile.html"))
     else:
        return(render_template("profile.html"))


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
     if request.method == "GET":
        return(render_template("contact.html"))
     else:
        return(render_template("contact.html"))

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
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Register user"""
    if request.method == "GET":
        return render_template("signup.html")

    # check username and password
    username = request.form.get("username")

    password = request.form.get("password")

    #ensure len is at least 5
    if len(password) < 5:
        return apology("Password insecure. Make it longer")

    #check for nums and letters
    numbers = sum(c.isdigit() for c in password)
    letters = sum(c.isalpha() for c in password)

    #check to make sure at least 2 nums and 2 letters
    if numbers <= 1:
        return apology("Password insecure. Insert at least 2 numeric characters")
    elif letters <= 1:
        return apology("Password insecure. Insert at least 2 alphabetic characters")

    numbers = 0
    letters = 0

    confirmation = request.form.get("confirmation")

    if username == "" or len(db.execute('SELECT username FROM users WHERE username = ?', username)) > 0:
        return apology("Your entered username is already taken or is blank. Please input a different username.")
    if password == "" or password != confirmation:
        return apology("Your entered username doesn't match or is blank. Please input a password.")

    # Add new user to users db (includes: username and HASH of password)
    db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
               username, generate_password_hash(password))
    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)
    # Log user in, i.e. Remember that this user has logged in
    session["user_id"] = rows[0]["id"]
    # Redirect user to home page
    # db.execute("ALTER )
    return redirect("/")


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code



