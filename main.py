from flask import Flask, request, render_template, session, redirect
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random
from string import ascii_letters, digits

conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
c = conn.cursor()

# Authentication
app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"

def random_str(n=7):
    string = ""
    for i in range(n):
        string += random.choice(ascii_letters + digits)
    return string

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not request.form.get("url"):
            return "Please fill out all required fields", 400

        url = request.form.get("url")
        code = random_str()

        while True:
            _ = c.execute("SELECT * FROM urls WHERE code=:code", {"code": code}).fetchall()
            if len(_) == 0:
                break
            code = random_str()
        
        c.execute("INSERT INTO urls (code, url) VALUES (:code, :url)", {"code": code, "url": url})
        conn.commit()

        return f"/{code}", 200

    else:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        print(request.form.get("username"), request.form.get("password"), request.form.get("confirmation"))
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return "Please fill out all fields", 400
        if request.form.get("password") != request.form.get("confirmation"):
            return "Password confirmation doesn't match", 400
        if len(c.execute("SELECT * FROM users WHERE username=:username", {"username": request.form.get("username")}).fetchall()) != 0:
            return "User already exist", 400
        pw_hash = generate_password_hash(request.form.get("password"), method="pbkdf2:sha256", salt_length=8)
        c.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": request.form.get("username"), "password": pw_hash})
        conn.commit()
        session["username"] = request.form.get("username")
        return "success", 200
    else:
        print(session)
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password"):
            return "Please fill out all required fields", 400

        user = c.execute("SELECT * FROM users WHERE username=:username", {"username": request.form.get("username")}).fetchall()

        if len(user) == 0:
            return "User doesn't exist", 400

        password = user[0][1]
        if not check_password_hash(user[0][1], request.form.get("password")):
            return "Password Incorrect", 400

        session["username"] = request.form.get("username")

        return "success", 200

    else:
        return render_template("login.html")


@app.route("/<code>")
def url(code):
    url = c.execute("SELECT * FROM urls WHERE code=:code", {"code": code}).fetchall()
    if len(url) == 0:
        return "404", 404

    return redirect(url[0][1])

if __name__ == "__main__":
    app.run("0.0.0.0", 3000, True, )