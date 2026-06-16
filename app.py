from flask import Flask, render_template, request, redirect, session
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "secure_key"

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password BLOB
)
""")

conn.commit()
conn.close()

@app.route("/")
def home():
    return redirect("/login")


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        )

        conn = sqlite3.connect("users.db")

        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed)
            )

            conn.commit()

            return redirect("/login")

        except:
            return "User exists"

    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        conn = sqlite3.connect("users.db")

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        if user:

            if bcrypt.checkpw(
                password.encode(),
                user[2]
            ):

                session["user"] = username

                return redirect("/dashboard")

        return "Invalid Login"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["user"]
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


app.run(debug=True)
