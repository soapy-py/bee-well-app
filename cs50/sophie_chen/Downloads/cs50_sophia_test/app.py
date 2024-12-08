import os
import requests
import sqlite3
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import HTTPException

from helpers import apology, login_required, get_form, extract_top_moods, get_color

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///journal.db")

DB_FILE = 'journal.db'

# Create the database and table if they don't exist
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journalentries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                analysis TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

# Initialize the database
init_db()

API_URL = "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions"
headers = {"Authorization": "Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    """Analyze the user's journal entry."""
    user_input = request.form.get("text")
    user_title = request.form.get("title")
    if not user_input:
        return apology("Must provide journal entry text", 400)

    # Call the Hugging Face API
    try:
        response = query({"inputs": user_input})
    except Exception as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500

    # Save the journal entry and associate it with the user
    try:
        db.execute("INSERT INTO journalentries (user_id, title, text, analysis) VALUES (?, ?, ?, ?)",
                   session["user_id"], user_title, user_input, str(response))
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    # Redirect user back to home page
    return redirect("/")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def home():
    """Display the home page with the user's journal entries."""
    # Query for current user's info
    user_info = db.execute('SELECT firstname FROM users WHERE user_id = ?', session["user_id"])
    if not user_info:
        return apology("User not found", 403)

    firstname = user_info[0]["firstname"]

    # Fetch user's journal entries using the user_journal table
    query = '''
        SELECT journalentries.title, journalentries.text, journalentries.analysis, journalentries.timestamp
        FROM journalentries
        JOIN users ON journalentries.user_id = users.user_id
        WHERE users.user_id = ?
        ORDER BY journalentries.timestamp DESC
    '''
    entries = db.execute(query, session["user_id"])
    for entry in entries:
        # Safely update the 'analysis' field
        entry["top_moods"] = extract_top_moods(entry["analysis"])

    # Add the color for each entry
    for entry in entries:
        if entry["top_moods"]:
            entry["mood_color"] = get_color(entry["top_moods"][0])
        else:
            entry["mood_color"] = "#ffffff" # if something goes wrong and model messes up, just color

    return render_template("home.html", entries=entries, firstname=firstname)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

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

    # User reached route via POST (submitting form)
    if request.method == "POST":
        # Get username and ensure it exists
        username = get_form("username")

        # Get first and last name, ensure they exist
        lastname = get_form("lastname")
        firstname = get_form("firstname")

        # Get password and confirmation and ensure they exist
        password = get_form("password")
        confirmation = get_form("confirmation")
        # Ensure passwords match
        if password != confirmation:
            return apology("passwords don't match", 400)
        # Add user to database
        try:
            # Hash password
            db.execute("INSERT INTO users (username, firstname, lastname, hash) VALUES (?, ?, ?, ?)",
                       username, firstname, lastname, generate_password_hash(request.form.get("password")))
            # Redirect user to home page
            return redirect("/")
        # Ensure username wasn't already taken
        except (ValueError):
            return apology("username taken", 400)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/changepw", methods=["GET", "POST"])
def changepw():
    """Edit user profile"""

    # User reached route via POST (submitting form)
    if request.method == "POST":
        # Ensure proper username
        password = get_form("password")

        # Ensure password matches current password
        current_pw = db.execute("SELECT hash FROM users WHERE id = ?",
                                session["user_id"])[0]["hash"]
        if not check_password_hash(
            current_pw, request.form.get("password")
        ):
            return apology("incorrect password", 403)

        # Ensure new passwords exist
        newpassword = get_form("newpassword")
        confirmation = get_form("confirmation")

        # Ensure new passwords match
        if newpassword != confirmation:
            return apology("passwords don't match", 400)
        # Add user to database
        new_pw = generate_password_hash(request.form.get("newpassword"))
        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   new_pw, session["user_id"])

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changepassword.html")

@app.route("/journal", methods=["GET", "POST"])
@login_required
def journal():
    if request.method == "POST":
        # Get the form input for the journal entry text
        text = request.form.get("text")
        print(f"Text from form: {text}")
        if not text:
            return apology("Journal entry cannot be empty", 400)

        title = request.form.get("title")

        # Call the Hugging Face API for analysis
        response = query({"inputs": text})
        analysis = response  # Process the response from Hugging Face API as needed

        # Insert the journal entry into the journalentries table
        db.execute("INSERT INTO journalentries (user_id, title, text, analysis) VALUES (?, ?, ?, ?)",
                   session["user_id"], title, text, str(analysis))

        # Redirect user to home page after successfully posting the entry
        return redirect("/")

    else:
        # Fetch the user's journal entries
        entries = db.execute("SELECT title, text, analysis, timestamp FROM journalentries WHERE user_id = ? ORDER BY timestamp DESC",
                             session["user_id"])

        # Render the journal entries in the home page
        return render_template("journal.html", entries=entries)


@app.errorhandler(HTTPException)
def handle_exception(error):
    return apology(error.description)

@app.route("/report/<int:entry_id>", methods=["GET"])
@login_required
def report(entry_id):
    """Fetch the analysis of a specific journal entry."""
    query = '''
        SELECT journalentries.text, journalentries.analysis
        FROM journalentries
        JOIN users ON journalentries.user_id = users.user_id
        WHERE journalentries.user_id = ? AND users.user_id = ?
    '''
    entry = db.execute(query, entry_id, session["user_id"])
    if not entry:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"text": entry[0]["text"], "analysis": entry[0]["analysis"]})


@app.route('/clear_all', methods=['POST'])
def clear_all():
    try:
        # Delete all entries from the journalentries table
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM journalentries")
            conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/aboutus")
@login_required
def aboutus():
    return render_template("aboutus.html")

@app.route("/resources")
@login_required
def resources():
    return render_template("resources.html")

if __name__ == '__main__':
    app.run(debug=True)
