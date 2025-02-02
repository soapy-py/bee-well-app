Project Video: https://youtu.be/hWx4Kftxm7U

Project Name: Bee Well Web App

Description
The Bee Well Web App is a personal wellness tracker that allows users to track their mood, habits, and progress in a variety of wellness categories. It includes a journal feature, personalized tracking, and a playlist integration to aid mindfulness and relaxation.

Folder Structure
The repository includes the following components: 
├── __pycache__/
├── flask_session/
├── static/
│   ├── favicon.ico
│   ├── l_heart_validator.py
│   ├── jasmine.png
│   ├── sophie.png
│   └── styles.css
├── templates/
│   ├── aboutus.html
│   ├── apology.html
│   ├── changepassword.html
│   ├── home.html
│   ├── journal.html
│   ├── layout.html
│   ├── login.html
│   ├── register.html
│   └── resources.html
├── app.py
├── helpers.py
├── journal.db
└── requirements.txt

Description of files and folders
static/: Contains static files (images, stylesheets, etc.)
favicon.ico: The website's favicon.
l_heart_validator.py: Validation script for the app.
jasmine.png, sophie.png, sophia.png: Images of team members used in the website.
styles.css: CSS file for styling the pages.
templates/: Contains the HTML templates used for rendering web pages.
home.html: The home page of the app.
journal.html: The page for users to write in their journal.
layout.html: Base template with common layout and structure.
login.html, register.html: User authentication pages for login and registration.
aboutus.html, apology.html, changepassword.html: Additional user-facing pages.
app.py: The main Python script for running the Flask web application.
helpers.py: Contains helper functions for app functionality (e.g., database operations, form validation).
journal_1.db, journal.db: SQLite databases storing user information, journal entries, and other app data.
requirements.txt: A file listing the dependencies required to run the app (e.g., Flask, SQLite).

Installation and setup
Prerequisites: before you begin, ensure that you have the following installed on your system:
Python 3.x
pip (Python package installer)

Step 1: Clone repository to local machine
Unzip the file, upload it to VSCode
Cd cs50

Step 2: Install dependencies
Install the required dependencies listed in requirements.txt:
pip install -r requirements.txt

Step 3: Run the application
Start the flask application 
export FLASK_APP=app.py 
python app.py
Your app should now be accessible at http://127.0.0.1:5000/.




Step 4: Accessing database
The app uses SQLite databases (journal_1.db and journal.db) to store user data and journal entries. You can interact with these databases directly through SQLite tools or use Flask's built-in functionality.
Features
Journal Tracking: Users can write and save their thoughts, feelings, and wellness progress.
User Authentication: The app supports login and registration for users.
Personalized Experience: Users can change their password and view personalized journal entries.


Usage

The home page (home.html) displays an overview of your wellness progress and quick access to various features like journal entries, mood tracking, and playlists.

The journal page (journal.html) allows users to write new entries and view previous ones. This page uses the journal.db to store the text of each entry along with a timestamp.

In the resources.html, you'll find Spotify playlists that match various moods (e.g., for relaxation, focus, or energy). The embedded iframes make it easy to listen to the playlists directly within the app.

License: This project is open-source and available under the MIT License.
