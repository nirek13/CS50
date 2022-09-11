import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
#db.execute("CREATE TABLE portfolio (stock TEXT, quantity INTEGER)")

#db.execute("CREATE TABLE transactions ( stock TEXT, quantity INTEGER, price INTEGER, date TEXT, FOREIGN KEY(user_id) REFERENCES users(id)")
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
     '''index shows portfolio'''

     result = db.execute("SELECT cash FROM users WHERE id =:id", id = session["user_id"])
     cash = result[0]['cash']

     portfolio = db.execute("SELECT stock, quantity FROM portfolio2 where id = :id", id = session["user_id"])

     if not portfolio:
        return apology("sorry you have no holdings",200)

     grand_total = cash

     for stock in portfolio:
         price = lookup(stock['stock'])['price']
         total = stock['quantity'] * price
         stock.update({'price': price, 'total': total})
         grand_total += total

     return render_template("index.html", stocks=portfolio, cash=cash, total=grand_total)

     for stock in portfolio:
         price = lookup(stock['stock'])['price']
         total = stock['quantity'] * price
         stock.update({'price': price, 'total': total})
         grand_total += total

     return render_template("index.html", stocks=portfolio, cash=cash, total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "POST":

        if (not request.form.get("symbol")) or (not request.form.get("shares")):
            return apology("must provide stock symbol and number of shares")

        if int(request.form.get("shares")) <= 0:
            return apology("must provide valid number of shares (integer)")

        quote = lookup(request.form.get("symbol"))

        if quote == None:
            return apology("Stock symbol not valid, please try again")

        cost = int(request.form.get("shares")) * quote['price']
        result = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])

        if cost > result[0]["cash"]:
            return apology("you do not have enough cash for this transaction")

        now = datetime.now()
        db.execute("UPDATE users SET cash=cash-:cost WHERE id=:id", cost=cost, id=session["user_id"]);
        add_transaction = db.execute("INSERT INTO transactions (user_id, stock, quantity, price, date) VALUES (:user_id, :stock, :quantity, :price, :date)",
        user_id=session["user_id"], stock=quote["symbol"], quantity=int(request.form.get("shares")), price=quote['price'], date=now.strftime("%Y-%m-%d %H:%M:%S"))
        curr_portfolio = db.execute("SELECT quantity FROM portfolio WHERE stock=:stock", stock=quote["symbol"])

        if not curr_portfolio:
            db.execute("INSERT INTO portfolio (stock, quantity) VALUES (:stock, :quantity)",
                stock=quote["symbol"], quantity=int(request.form.get("shares")))
        else:
            db.execute("UPDATE portfolio SET quantity=quantity+:quantity WHERE stock=:stock",
                quantity=int(request.form.get("shares")), stock=quote["symbol"]);

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    if request.method == "POST":

        port = db.execute("SELECT stock, quantity, price, date FROM transactions WHERE user_id=:id", id=session["user_id"])

        if not port:
            return apology("sorry you have no transactions on record")
    else:
        port = db.execute("SELECT stock, quantity, price, date FROM transactions WHERE user_id=:id", id=session["user_id"])
        return render_template("history.html", stocks = port)



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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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

        if not request.form.get("symbol"):
            return apology("must provide stock symbol")

        quote = lookup(request.form.get("symbol"))

        if quote == None:
            return apology("Stock symbol not valid, please try again")

        else:
            return render_template("quoted.html", quote=quote)

    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("Must provide username.",400)

        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Must provide pasword.",400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match.",400)

        rt = db.execute("select username from users where username = :username",username = request.form.get("username"))

        if len(rt) > 0 :
            return apology("username has already been used",400)

        hashed_password = generate_password_hash(request.form.get("password"))
        usernames = request.form.get("username")
        result = db.execute("insert into users (username,hash) values(:username,:hash_)",username = request.form.get("username"),hash_ = hashed_password)

        userid = db.execute("select id from users where username = :username", username =request.form.get("username"))
        row = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = row[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""

    if not isinstance(e, HTTPException):
        e = InternalServerError()

    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
