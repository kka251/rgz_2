from flask import Blueprint, request, render_template, redirect, url_for, abort, jsonify, session
import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash
from psycopg2 import extras


rgz = Blueprint ("rgz", __name__)

def dbConnect():
    conn = psycopg2.connect(
        host="127.0.0.1", 
        database="rgz_web",
        user="kristina_knowledge_base",
        password="123")
    
    return conn

def dbClose(cur,conn):
    cur.close()
    conn.close()



@rgz.route("/rgz")
def main():
    conn = dbConnect()
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    
    # Получить все товары
    cur.execute("SELECT * FROM product")
    products = cur.fetchall()
    
    username = session.get("username")
    if not username:
        visibleUser = "Anon"
        return render_template('rgz.html', username=visibleUser, products=products)
    return render_template('rgz.html', username=username, products=products)


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

@rgz.route('/rgz/log', methods=["GET","POST"])
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
        return redirect("/rgz")
    else:
        errors = ["Неправильный логин или пароль"]
        return render_template("log.html", errors=errors)
    
@rgz.route('/rgz/logout')
def logout():
    session.clear()  # Удаление всех полей из сессии
    return redirect('/rgz/log')

@rgz.route('/rgz/add_to_cart', methods=["POST"])
def add_to_cart():
    if not session.get("username"):
        abort(403)  
    product_ids = request.form.getlist("product_id")  # Get a list of product IDs
    kolvo = request.form.getlist("kolvo")     # Get a list of kolvo

    if not product_ids or not kolvo:
        abort(400)

    # Add the products and kolvo to the cart
    # cart_items = []
    # for product_id, kolvo in zip(product_ids, kolvo):
    #     cart_items.append({"product_id": product_id, "kolvo": kolvo})

    # return render_template("korzina.html", cart_items=cart_items)
    conn = dbConnect()
    cur = conn.cursor(cursor_factory=extras.DictCursor)

    cart_items = []
    for product_id, kolvo in zip(product_ids, kolvo):
        cur.execute("SELECT name_, price FROM product WHERE id = %s", (product_id,))
        product = cur.fetchone()
        if product:
            cart_items.append({"name": product["name_"], "price": product["price"], "kolvo": kolvo})

    conn.close()
    cur.close()
    session["cart_items"] = cart_items

    return render_template("korzina.html", cart_items=cart_items)
@rgz.route('/rgz/korzina')
def cart():
    if not session.get("username"):
        return redirect('/rgz/login')  # Перенаправление на страницу входа

    # cart_items = request.form.get("product_id")

    # return render_template("korzina.html", cart_items=cart_items)
    cart_items = session.get("cart_items", [])

    return render_template("korzina.html", cart_items=cart_items)

