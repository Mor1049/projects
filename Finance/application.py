import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    rows = db.execute("""
        SELECT symbol, SUM(shares) as Holdings
        FROM transactions
        WHERE user_id = :user_id
        GROUP BY symbol
        HAVING Holdings > 0;
    """, user_id=session["user_id"])
    portfolio = []
    allcash = 0
    for row in rows:
        stock = lookup(row["symbol"])
        portfolio.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "shares": row["Holdings"],
            "price": usd(stock["price"]),
            "total": usd(stock["price"] * row["Holdings"])
        })
        allcash += stock["price"] * row["Holdings"]

    rows = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    cash = rows[0]["cash"]
    allcash += cash

    return render_template("index.html", portfolio=portfolio, cash=usd(cash), allcash=usd(allcash))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        elif not request.form.get("shares"):
            return apology("must provide number of shares to buy", 403)
        elif not request.form.get("shares").isdigit():
            return apology("you must enter a number")
        symbol = request.form.get("symbol").upper()
        shares = int(request.form.get("shares"))
        stockticker = lookup(symbol)
        if stockticker is None:
            return apology("invalid symbol")
        # Ensure password was submitted
        rows = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
        cash = rows[0]["cash"]

        cash_update = cash - shares * stockticker["price"]
        if cash_update < 0:
            return apology("You can not afford the stock")
        db.execute("UPDATE users SET cash=:cash_update WHERE id=:id",
                   cash_update=cash_update,
                   id=session["user_id"])
        db.execute("""
            INSERT INTO transactions
                (user_id, symbol, shares, price)
            VALUES (:user_id, :symbol, :shares, :price)
            """,
                   user_id=session["user_id"],
                   symbol=stockticker["symbol"],
                   shares=shares,
                   price=stockticker["price"]
                   )
        flash("You bought the stock!")
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("""
        SELECT symbol, shares, price, transacted
        FROM transactions
        WHERE user_id=:user_id
    """, user_id=session["user_id"])
    for i in range(len(transactions)):
        transactions[i]["price"] = usd(transactions[i]["price"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

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
        check_result = request.form.get("symbol")
        if check_result is None:
            return check_result
        symbol = request.form.get("symbol").upper()
        stock = lookup(symbol)
        if stock is None:
            return apology("invalid symbol", 400)
        return render_template("quoted.html", stockName={
            "name": stock["name"],
            "symbol": stock["symbol"],
            "price": usd(stock["price"])
        })

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

#        if request.form.get("password") == (";") or ("'"):
#            return apology("invalid password symbols", 400)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure password was submitted
        if request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords do not match", 400)
        try:
            # Query database for username
            primarykey = db.execute("INSERT INTO users (username,hash) VALUES (:username, :hash)",
                                    username=request.form.get("username"),
                                    hash=generate_password_hash(request.form.get("password")))
        except:
            return apology("username exists already", 400)
        if primarykey is None:
            return apology("Error during registratiion", 400)
        session["user_id"] = primarykey

        return render_template("index.html")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        elif not request.form.get("shares"):
            return apology("must provide number of shares to buy", 403)
        elif not request.form.get("shares").isdigit():
            return apology("you must enter a number")
        symbol = request.form.get("symbol").upper()
        shares = int(request.form.get("shares"))
        stockticker = lookup(symbol)
        if stockticker is None:
            return apology("invalid symbol")

        rows = db.execute("""
            SELECT symbol, SUM(shares) as Holdings
            FROM transactions
            WHERE user_id=:user_id
            GROUP BY symbol
            HAVING Holdings > 0;
        """, user_id=session["user_id"])
        for row in rows:
            if row["symbol"] == symbol:
                if shares > row["Holdings"]:
                    return apology("You do not own that many shares")

        # Ensure password was submitted
        rows = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
        cash = rows[0]["cash"]

        cash_update = cash + shares * stockticker["price"]
        db.execute("UPDATE users SET cash=:cash_update WHERE id=:id",
                   cash_update=cash_update,
                   id=session["user_id"])
        db.execute("""
            INSERT INTO transactions
                (user_id, symbol, shares, price)
            VALUES (:user_id, :symbol, :shares, :price)
            """,
                   user_id=session["user_id"],
                   symbol=stockticker["symbol"],
                   shares=-1 * shares,
                   price=stockticker["price"]
                   )
        flash("You sold the stock!")
        return redirect("/")

    else:
        rows = db.execute("""
            SELECT symbol
            FROM transactions
            WHERE user_id=:user_id
            GROUP BY symbol
            HAVING SUM(shares) > 0;
        """, user_id=session["user_id"])
        return render_template("sell.html", symbols=[row["symbol"] for row in rows])


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    # Allow users to change passwords

    if request.method == "POST":

        # Check if current password is empty
        if not request.form.get("currentpassword"):
            return apology("You must provide the current password", 400)

        # Check database for user id
        rows = db.execute("SELECT hash FROM users WHERE id = :user_id", user_id=session["user_id"])

        # Check if currrent password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("currentpassword")):
            return apology("password is invalid", 400)

        # Check if new password is empty
        if not request.form.get("newpassword"):
            return apology("must provide a new password", 400)

        # Check password confirmation of new password
        elif not request.form.get("newpasswordconfirmation"):
            return apology("new password and confirmation do not match", 400)

        elif request.form.get("newpassword") != request.form.get("newpasswordconfirmation"):
            return apology("new password must match confirmation", 400)

        # Database update
        hash = generate_password_hash(request.form.get("newpassword"))
        rows = db.execute("UPDATE users SET hash = :hash WHERE id = :user_id", user_id=session["user_id"], hash=hash)

        # Flash change
        flash("Your password is changed!")

    return render_template("changepassword.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
