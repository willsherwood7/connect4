import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps

from datetime import datetime

from cs50 import SQL
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///connect4.db")

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def check_password_requirements(password):
    # Ensure sure password is at least 7 characters
    if len(password) <= 7:
        return False

    # Ensure password has one uppercase letter, one lower case letter, and one number
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)

    if not has_upper or not has_lower or not has_digit:
        return False
    return True


def update_stats(player1_id, player2_id, result):
    # Get timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(player2_id)

    if result!=0:
        winner_id = player1_id if result == 1 else player2_id
        loser_id = player2_id if result == 1 else player1_id

        # Increase individual users stats
        db.execute("UPDATE users SET wins = wins+1 WHERE id=?", winner_id)
        db.execute("UPDATE users SET losses = losses+1 WHERE id=?", loser_id)
        db.execute("INSERT INTO games (player1_id, player2_id,time,result) VALUES (?, ?, ?, ?)", winner_id, loser_id, timestamp, 1)
        db.execute("INSERT INTO games (player1_id, player2_id,time,result) VALUES (?, ?, ?, ?)", loser_id, winner_id, timestamp, -1)
    else:
        db.execute("INSERT INTO games (player1_id,player2_id,time,result) VALUES (?, ?, ?, ?)", player1_id,player2_id, timestamp, 0)
        db.execute("INSERT INTO games (player1_id,player2_id,time,result) VALUES (?, ?, ?, ?)", player2_id,player1_id, timestamp, 0)
        db.execute("UPDATE users SET ties = ties+1 WHERE id=?", player1_id)
        db.execute("UPDATE users SET ties = ties+1 WHERE id=?", player2_id)

    # Find old elos
    player1_data=db.execute("SELECT rating AS player1_elo, (wins + losses + ties) AS player1_games_played FROM users WHERE id = ?", player1_id)
    player2_data=db.execute("SELECT rating AS player2_elo, (wins + losses + ties) AS player2_games_played FROM users WHERE id = ?", player2_id)

    # Make loss appear as -1 for elo calculator
    if result==2:
        result=-1

    # Find old elos
    print(player1_data)
    print(player2_data)

    player1_elo_old = player1_data[0]['player1_elo']
    player2_elo_old = player2_data[0]['player2_elo']

    # Update elos
    player1_elo_new = max(0, player1_data[0]["player1_elo"] + update_elo(player1_elo_old, player2_elo_old, player1_data[0]["player1_games_played"], result))
    player2_elo_new = max(0, player2_data[0]["player2_elo"] + update_elo(player2_elo_old, player1_elo_old, player2_data[0]["player2_games_played"], -1 * result))
    db.execute("UPDATE users SET rating = ? WHERE id=?", player1_elo_new, player1_id)
    db.execute("UPDATE users SET rating = ? WHERE id=?", player2_elo_new, player2_id)


def update_elo(player1_elo, player2_elo, games_played, result):
    # returns change in player 1 elo
    # games become less and less impactful until 10 games
    # players gain more from playing higher elo players
    # result is for player 1: -1 , 0, or 1
    # -1 is loss, 0 is tie, 1 is win
    multiplier = max(11 - int(games_played), 1)
    difference = (int(player1_elo) - int(player2_elo)) // 100

    if difference < 0 and result == 1:
        difference += 1
    if result == 1:
        return multiplier * (10 - difference)
    elif result == -1:
        return -(multiplier * (10 + difference))
    else:
        return - (multiplier * difference)
