import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# COLLABORATED WITH MOHAMMED MAAROUF

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

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# create table in sql
#db.execute("CREATE TABLE profile(id INTEGER, Symbol TEXT, Shares INTEGER, Price INTEGER, Operation TEXT, time DATETIME)")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # query database for user cash
    user_cash = db.execute(
        "SELECT cash FROM users WHERE id = ?", session["user_id"])
    stocks = db.execute(
        "SELECT symbol, SUM(shares) as shares, operation FROM profile WHERE id = ? GROUP BY symbol HAVING (SUM(shares)) > 0;", session["user_id"])

    # loop through stocks and get the user cash, total cash, symbol, name, price, total
    total_cash_stocks = 0
    for stock in stocks:
        quote = lookup(stock["Symbol"])
        stock["Symbol"] = quote["symbol"]
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["total"] = stock["price"] * stock["shares"]
        total_cash_stocks = total_cash_stocks + stock["total"]

    total_cash = total_cash_stocks + user_cash[0]["cash"]
    return render_template("index.html", stocks=stocks, user_cash=user_cash[0], total_cash=total_cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    #get symbol, price, shares, user cash
    if request.method == "POST":
        symbol = request.form.get("symbol")
        price = lookup(symbol)
        shares = request.form.get("shares")
        user_cash = db.execute("SELECT cash FROM users WHERE id = ? ", session["user_id"])[0]["cash"]

        #check if symbol is true and valid
        if not symbol:
            return apology("a valid symbol must be provide")
        elif price is None:
            return apology("must provide valid symbol")

        #make sure there are no digits
        if price == None:
            return apology("Must provide a stock with a price that is greater than 0.")
        if not shares.isdigit():
            return apology("Must provide a positive number of shares")

        #need the int number of shares
        num_shares = int(shares)

        #make sure the shares number is greater than 1
        if num_shares < 1:
            return apology("Must provide a positive number of shares")

        #calc the total cost
        #make sure the user has enough cash
        shares_price = num_shares * price["price"]
        if user_cash < (shares_price):
            return apology("cash is not sufficient", 400)
        else:
            #update cash and insert into profile
            db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", shares_price, session["user_id"])
            db.execute("INSERT INTO profile (id, Symbol, Shares, Price, Operation) VALUES (?, ?, ?, ?, ?)", session["user_id"], symbol.upper(), shares, price["price"], "buy")

            flash("Transaction successful")
            return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    stocks = db.execute(
        "SELECT * FROM profile WHERE id = ?", session["user_id"])
    return render_template("history.html", stocks=stocks)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        #lookup the symbol
        quote = lookup(request.form.get("symbol"))

        #make sure it's a valid quote
        if quote is None:
            return apology("Please use a valid symbol", 400)
        else:
            #get the name, symbol, and price to display to user
            name = quote["name"]
            symbol = quote["symbol"]
            price = quote["price"]

            return render_template("alreadyquoted.html", name=quote["name"], symbol=quote["symbol"], price=quote["price"])

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get(("shares")))

        if shares < 1:
            return apology("shares must be a positive integer")

        if not symbol:
            return apology("missing symbol")

        stocks = db.execute(
            "SELECT SUM(shares) as shares FROM profile WHERE id = ? AND symbol = ?;", session["user_id"], symbol)[0]

        if shares > stocks["shares"]:
            return apology("You don't have this number of shares")

        price = lookup(symbol)["price"]
        shares_value = price * shares

        db.execute("INSERT INTO profile (id, symbol, shares, price, operation) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], symbol.upper(), -shares, price, "sell")

        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?",
                   shares_value, session["user_id"])

        flash("Sold!")
        return redirect("/")
    else:
        stocks = db.execute(
            "SELECT symbol FROM profile WHERE id = ? GROUP BY symbol", session["user_id"])
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
