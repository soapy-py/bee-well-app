import json, heapq

from flask import redirect, render_template, session, request, abort
from functools import wraps

# Extract the top 3 moods from the jounral entry for display on the home page
def extract_top_moods(emotion_data):

    # Replace single quotes with double quotes to make it valid JSON
    emotion_data = emotion_data.replace("'", '"')

    # Parse the input string into a Python object
    data = json.loads(emotion_data)

    # Flatten the nested structure (if the input is [[{...}]])
    emotions = data[0] if isinstance(data, list) and len(data) > 0 else []

    # Find the top 3 emotions with the highest scores
    top_emotions = heapq.nlargest(3, emotions, key=lambda x: x['score'])

    # Extract only the labels of the top 3 emotions
    top_labels = [emotion['label'] for emotion in top_emotions]

    return top_labels

# Identify the color corresponding to the journal entry's emotional aura based on Inside Out's colors, inspired by Spotify Aura from pset 7
def get_color(mood):
    joy = ["admiration", "amusement", "approval", "caring", "curiosity", "desire", "excitement", "gratitude", "joy", "love", "optimism", "pride", "realization", "relief", "surprise"]
    sadness = ["disappointment", "grief", "sadness"]
    anger = ["anger", "remorse"]
    disgust = ["annoyance", "disapproval", "disgust", "embarassment"]
    fear = ["confusion", "fear", "nervousness"]

    # Mapping of the mood to the corresponding HEX color for the journal entry's background
    if mood in joy:
        return"#FEF5A5"
    if mood in sadness:
        return "#A5E6FE"
    if mood in anger:
        return "#FEA5A5"
    if mood in fear:
        return "#CEB8FF"
    if mood in disgust:
        return "#A2FCA3"
    else:
        return "#C4C4C4"

# Modified/built off of CS50 Finance starter code
# Render message as an apology to user.
def apology(message, code=400):

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

    return render_template("apology.html", code=code, message=escape(message))

# Used CS50 Finance starter code
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# Created helper function to get form input and check if its missing/invalid
def get_form(form_name, type=None, min_val=None, max_val=None):
    form = request.form.get(form_name)

    # Ensure submission
    if not form:
        return abort(400, description=f"missing {form_name}")

    # Enforce typing, if given
    if type is not None:
        try:
            form = type(form)
        except (ValueError, TypeError):
            return abort(400, description=f"invalid {form_name}")

    # Enforce range for numerical values
    if isinstance(form, (int)):
        if min_val is not None and form < min_val:
            return abort(400, description=f"{form_name} must be greater than {min_val}")

        if max_val is not None and form > max_val:
            return abort(400, description=f"too many {form_name}")

    return form

