import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, check_password_requirements, update_stats

import game

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///connect4.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    # Clear game
    game.start_game()

    # Set game_over in session to be False
    session["game_over"] = False

    # Remove user2 from session
    session.pop('user2', None)

    """Show game options"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        players = request.form.get("players")

        if (players == "1"):
            if not request.form.get("difficulty"):
                return apology("must provide cpu difficulty", 400)

            # Store cpu difficulty in session
            session['cpu_difficulty'] = request.form.get("difficulty")

            # Redirect to 1 player page
            flash("Game started!")
            return redirect('/play1')

        if (players == "2"):
            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 400)

            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("must provide password", 400)

            # Query database for username
            rows = db.execute(
                "SELECT * FROM users WHERE username = ?", request.form.get("username")
            )

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")
            ):
                return apology("user 2 invalid username and/or password", 400)

            try:
                # Ensure user 1 can't also log in as user2
                if (rows[0]['id']) == session.get("user_id"):
                    return apology("user 1 cannot also be user 2", 400)
            except TypeError:
                # Handle the case where 'username' is not in the session
                return apology("session not found, please try logging in again", 400)

            # Add user 2 to the session
            session["user2"] = rows[0]["id"]

            # Redirect user to 2 player page
            flash("Game started!")
            return redirect("/play2")

    # User reached route via GET (as by clicking a link or via redirect)
    # Display a form for user to input preferences
    else:
        return render_template("index.html")

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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not confirmation:
            return apology("must confirm password", 400)

        # Ensure password and confirmation are identical
        elif password != confirmation:
            return apology("passwords must match", 400)

        # Ensure password meets requirement THIS IS MY PERSONAL TOUCH
        elif not check_password_requirements(password):
            return apology("password must be at least 7 letters, contain both upper and lower case letters, and include a number", 400)

        # Insert new user into the data base
        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)",
                username,
                generate_password_hash(password),
            )
        except ValueError:
            # Failed to add
            return apology("username already taken", 400)

        # Redirect user to home page
        flash("Registered!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/play2", methods=["GET", "POST"])
def play2():
    """Two player gameplay"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get button
        column = request.form['buttonId']

        # Ensure move is valid
        if not game.check_move(column):
            flash("That column is full.")
            return redirect("/play2")

        # Check if the move wins the game
        if game.check_win(column):
            # Get info about winner and loser
            winner = game.whos_turn()
            user1_id = session.get("user_id")
            user2_id = session.get("user2")

            # Make move in game.py
            game.make_move(column)

            # Set game_over in session to be True
            session["game_over"] = True

            # Update stats
            update_stats(user1_id, user2_id, winner)
            flash("Player " + str(winner) + " wins!")
            return redirect("/play2")

        # Make move in game.py
        game.make_move(column)

        # Check if game is tied after move
        if game.check_tied():
            # Get info about winner
            user1_id = session.get("user_id")
            user2_id = session.get("user2")

            # Set game_over in session to be True
            session["game_over"] = True

            # Update stats
            update_stats(user1_id, user2_id, 0)
            flash("It's a tie!")
            return redirect("/play2")

    # Whether GET or POST, always render new board
    return render_template("play.html", board=game.get_board(), numPlayers=2, turn=game.whos_turn(), game_over=session.get("game_over"))

@app.route("/play1", methods=["GET", "POST"])
def play1():
    """One player gameplay"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get the CPU difficulty
        cpu_difficulty = session.get('cpu_difficulty')

        # HUMAN move
        # Get button
        column = request.form['buttonId']

        # Ensure move is valid
        if not game.check_move(column):
            flash("That column is full.")
            return redirect("/play1")

        # Check if the move wins the game
        if game.check_win(column):
            # Get info about winner
            user1_id = session.get("user_id")

            # Set game_over in session to be True
            session["game_over"] = True

            # Make move in game.py
            game.make_move(column)

            # Update stats
            update_stats(user1_id, int(cpu_difficulty), 1)

            flash("Player 1 wins!")
            return redirect("/play1")

        # Make move in game.py
        game.make_move(column)

        # Check if game is tied after player move
        if game.check_tied():
            # Get info about winner
            user1_id = session.get("user_id")

            # Set game_over in session to be True
            session["game_over"] = True

            # Update stats
            update_stats(user1_id, ("cpu" + cpu_difficulty), 0)
            flash("It's a tie!")
            return redirect("/play1")

        # CPU MOVE
        # Make move with correct difficulty
        game.make_bot_move(cpu_difficulty)

        # Check if this move won the game
        if game.check_bot_won():
            # Update stats with CPU winner
            user1_id = session.get("user_id")

            # Update stats
            update_stats(user1_id, int(cpu_difficulty), 2)

            # Set game_over in session to be True
            session["game_over"] = True

            flash("CPU wins!")
            return redirect("/play1")

        # Check if game is tied after CPU move
        if game.check_tied():
            # Get info about winner
            user1_id = session.get("user_id")

            # Set game_over in session to be True
            session["game_over"] = True

            # Update stats
            update_stats(user1_id, int(cpu_difficulty), 0)
            flash("It's a tie!")
            return redirect("/play1")
    return render_template("play.html", board=game.get_board(), numPlayers=1, turn=game.whos_turn(), game_over=session.get("game_over"))

@app.route("/history")
@login_required
def history():
    """Show history of games played."""
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for('login'))  # Redirect to login if the user is not logged in.

    # Retrieve games, results, and the opponent's username in one query.
    games = db.execute(
        """
        SELECT g.time, g.result, u.username as opponent
        FROM games g
        JOIN users u ON g.player2_id = u.id
        WHERE g.player1_id = ?
        ORDER BY g.time DESC
        """,
        user_id
    )

    # Map numerical results to string representations.
    result_mapping = {1: 'Win', -1: 'Loss', 0: 'Tie'}
    for game in games:
        game['result'] = result_mapping.get(game['result'], 'Unknown')

    # Get the current user's username.
    username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]['username']
    return render_template("history.html", username=username, games=games)

@app.route("/stats")
@login_required
def stats():
    """Show player stats"""
    user_id = session.get("user_id")
    stats = db.execute("SELECT username,rating,wins,losses,ties FROM users WHERE id=?", user_id)
    return render_template("stats.html", stats=stats)

@app.route('/play-again/<int:num_players>')
@login_required
def play_again(num_players):
    # Clear game
    game.start_game()

    # Set game_over in session to be False
    session["game_over"] = False

    # Handle different scenarios based on num_players
    # Redirect user to correct player page
    flash("Game started!")
    return redirect("/play" + str(num_players))
