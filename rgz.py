from flask import Blueprint, request, render_template, redirect, url_for, abort, jsonify, session
import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash

rgz = Blueprint ("rgz", __name__)

@rgz.route('/rgz/')
def main():
    return render_template('rgz/catalog.html')

def dbConnect():
    conn = psycopg2.connect(
        host="127.0.0.1", 
        database="rgz_web",
        user= "kristina_knowledge_base",
        password="123")
    
    return conn

def dbClose(cur,conn):
    cur.close()
    conn.close()

@rgz.route("/rgz")
def main():
    username = session.get("username")
    if not username:
        visibleUser = "Anon"
        return render_template('rgz.html', username=visibleUser)
    return render_template('rgz.html', username=username)

@rgz.route('/rgz/register', methods=["GET","POST"])
def registerPage():
    errors = []

    if request.method == "GET":
        return render_template("register.html", errors=errors)
    
    username = request.form.get("username")
    password = request.form.get("password")

    if not (username or password):
        errors = ["Пожалуйста, заполните все поля"]
        return render_template("register.html", errors=errors)

    hashPassword = generate_password_hash(password)

    conn = dbConnect() 
    cur = conn.cursor()

    cur.execute("SELECT username FROM users WHERE username = %s", (username,))

    if cur.fetchone() is not None:
        errors = ["Пользователь с данным именем уже существует"]
        dbClose(cur,conn)
        return render_template("register.html", errors=errors)
    
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashPassword))

    conn.commit()
    conn.close()
    cur.close()

    return redirect("/rgz/log")

@rgz.route('/lab5/log', methods=["GET","POST"])
def loginPage():
    errors = []

    if request.method == "GET":
        return render_template("log.html", errors=errors)
    
    username = request.form.get("username")
    password = request.form.get("password")

    if not (username or password):
        errors = ["Пожалуйста, заполните все поля"]
        return render_template("log.html", errors=errors)

    conn = dbConnect() 
    cur = conn.cursor()

    cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))

    result = cur.fetchone()

    if result is None:
        errors = ["Неправильный логин или пароль"]
        dbClose(cur,conn)
        return render_template("log.html", errors=errors)
    
    userID, hashPassword = result

    if check_password_hash(hashPassword, password):
        session['id'] = userID
        session['username'] = username
        dbClose(cur,conn)
        return redirect("/lab5")
    else:
        errors = ["Неправильный логин или пароль"]
        return render_template("log.html", errors=errors)
    
@rgz.route('/catalog')
def catalog():
    userID = session.get("id")

    conn = dbConnect() 
    cur = conn.cursor()

    cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))

