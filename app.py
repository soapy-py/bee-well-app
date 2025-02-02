import requests
import sqlite3
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import HTTPException
# Import helper functions
from helpers import apology, login_required, get_form, extract_top_moods, get_color

# Configure Flask application
app = Flask(__name__)

# Configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///journal.db")

DB_FILE = 'journal.db'

# Create the journalentries database and table if they don't exist
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journalentries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                analysis TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
        """)
        conn.commit()

# Initialize the database
init_db()

# Set API_URL to the NLP model we use
API_URL = "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions"
# Set headers to the Hugging Face Severless Inference API key we created
headers = {"Authorization": "Bearer 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"}

# Call the Huggingface API
def query(payload):
    # Given the API URL and headers, post the journal entry with the requests library
    response = requests.post(API_URL, headers=headers, json=payload)
    # Return NLP analysis results in JSON format
    return response.json()

# Prevent caching to ensure each time the browser makes a request, it fetches fresh data from the server rather than relying on a cached response
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Home page with the user's journal entries
@app.route("/")
@login_required
def home():
    # Query for current user's info
    user_info = db.execute('SELECT firstname FROM users WHERE user_id = ?', session["user_id"])
    # Return error if not found
    if not user_info:
        return apology("User not found", 403)
    # Fetch the first name of the current user since user_info is a list with an element
    firstname = user_info[0]["firstname"]

    # Fetch user's journal entries using the journalentries table
    query = '''
        SELECT journalentries.title, journalentries.text, journalentries.analysis, journalentries.timestamp
        FROM journalentries
        JOIN users ON journalentries.user_id = users.user_id
        WHERE users.user_id = ?
        ORDER BY journalentries.timestamp DESC
    '''
    entries = db.execute(query, session["user_id"])

    # Update the analysis field for each entry to display only the top 3 moods using the helper function extract_top_moods
    for entry in entries:
        entry["top_moods"] = extract_top_moods(entry["analysis"])

    # Update the colors for each entry using the get_color helper function based on its corresponding aura
    for entry in entries:
        if entry["top_moods"]:
            entry["mood_color"] = get_color(entry["top_moods"][0])
        # If something goes wrong and model messes up, display white
        else:
            entry["mood_color"] = "#ffffff"
    # Render home.html to display the results
    return render_template("home.html", entries=entries, firstname=firstname)

# Login function to help users enter their account
# Modified/built off of CS50 Finance starter code
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route by POST
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

        # Check that username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect to home page
        return redirect("/")

    else:
        return render_template("login.html")

# Log user out
# From CS50 Finance starter code
@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# Register user for a new account
@app.route("/register", methods=["GET", "POST"])
def register():

    # User reached route by POST
    if request.method == "POST":
        # Get username and ensure it exists
        username = get_form("username")

        # Get first and last name and ensure they exist
        lastname = get_form("lastname")
        firstname = get_form("firstname")

        # Get password and confirmation and ensure they exist
        password = get_form("password")
        confirmation = get_form("confirmation")

        # Ensure the password and confirmation password match
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

    else:
        return render_template("register.html")

# Allow users to change password
# Modified/built off of code we wrote for CS50 Finance
@app.route("/changepw", methods=["GET", "POST"])
def changepw():

    # User reached route by POST
    if request.method == "POST":

        # Get current password from user
        password = get_form("password")

        # Ensure entered password matches current password
        password = db.execute("SELECT hash FROM users WHERE user_id = ?",
                                session["user_id"])[0]["hash"]
        if not check_password_hash(
            password, request.form.get("password")
        ):
            # Otherwise return an error
            return apology("incorrect password", 403)

        # Get new password from user
        newpassword = get_form("newpassword")
        # Get a confirmation of the new password from the user
        confirmation = get_form("confirmation")

        # Ensure new password matches with confirmation
        if newpassword != confirmation:
            return apology("passwords don't match", 400)
        # Add user to database with the new hashed password
        new_pw = generate_password_hash(request.form.get("newpassword"))
        db.execute("UPDATE users SET hash = ? WHERE user_id = ?",
                   new_pw, session["user_id"])

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changepassword.html")

# Journal page where users enter their journal entries
@app.route("/journal", methods=["GET", "POST"])
@login_required
def journal():
    if request.method == "POST":
        # Get the journal entry input
        text = request.form.get("text")
        # Returns an error if there is no user_input
        if not text:
            return apology("Journal entry cannot be empty", 400)
        # Get the title input for the journal entry
        title = request.form.get("title")

        # Send the entry input to the function calling Hugging Face API for NLP analysis of the emotions
        try:
            response = query({"inputs": text})
        # Return an error if the process was unsuccessful
        except Exception as e:
            return jsonify({"error": f"API error: {str(e)}"}), 500

        # Save the journal entry with the returned results in the journalentries table and associate it with the user through user_id
        try:
            db.execute("INSERT INTO journalentries (user_id, title, text, analysis) VALUES (?, ?, ?, ?)",
                        session["user_id"], title, text, str(response))
        # Return error if something goes wrong
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500

        # Redirect user to home page after successfully posting the entry
        return redirect("/")

    else:
        # Fetch the user's journal entries
        entries = db.execute("SELECT title, text, analysis, timestamp FROM journalentries WHERE user_id = ? ORDER BY timestamp DESC",
                             session["user_id"])

        # Render the journal entries in the home page
        return render_template("journal.html", entries=entries)

# Modified/built off of CS50 Finance starter code
# Handle exception function
@app.errorhandler(HTTPException)
def handle_exception(error):
    return apology(error.description)


# Redirect to about us page
@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

# Redirect to resources page
@app.route("/resources")
@login_required
def resources():
    return render_template("resources.html")

if __name__ == '__main__':
    app.run(debug=True)
