from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import random
from functools import wraps

app = Flask(__name__)
app.secret_key = 'awesrdgtfhAWSEDTRYUIxCVGBHJ5247896532'

# -----------------------------------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

# -----------------------------------------------------
def create_db():
    with sqlite3.connect("db.sqlite") as con:
        c = con.cursor()
        # جدول کاربران
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            pages INTEGER NOT NULL,
            genre TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """)
        con.commit()

# -----------------------------------------------------
@app.route('/')
def index():
    return redirect(url_for('login'))

# -----------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect("db.sqlite") as con:
            c = con.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            if user:
                session["username"] = username
                flash(f"Welcome {username}", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("نام کاربری یا رمز عبور اشتباه است!", "error")
    return render_template('login.html')

# -----------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("شما با موفقیت خارج شدید.", "success")
    return redirect(url_for('login'))

# -----------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect("db.sqlite") as con:
            c = con.cursor()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                con.commit()
                flash("ثبت‌نام موفقیت‌آمیز بود. حالا می‌توانید وارد شوید.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("این نام کاربری قبلا ثبت شده است!", "error")
    return render_template("register.html")

# -----------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    with sqlite3.connect("db.sqlite") as con:
        c = con.cursor()
        c.execute("SELECT * FROM books")
        books = c.fetchall()
    return render_template('dashboard.html', books=books)

# -----------------------------------------------------
@app.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        pages = request.form["pages"]
        genre = request.form["genre"]
        status = request.form["status"]

        with sqlite3.connect("db.sqlite") as con:
            c = con.cursor()
            c.execute("INSERT INTO books (title, author, pages, genre, status) VALUES (?, ?, ?, ?, ?)",
                      (title, author, pages, genre, status))
            con.commit()

        flash("کتاب با موفقیت اضافه شد.", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_book.html")

# -----------------------------------------------------
@app.route("/delete_book/<int:book_id>")
@login_required
def delete_book(book_id):
    with sqlite3.connect("db.sqlite") as con:
        c = con.cursor()
        c.execute("DELETE FROM books WHERE id=?", (book_id,))
        con.commit()
    flash("کتاب حذف شد.", "success")
    return redirect(url_for("dashboard"))

# -----------------------------------------------------
@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
@login_required
def edit_book(book_id):
    with sqlite3.connect("db.sqlite") as con:
        c = con.cursor()
        if request.method == "POST":
            title = request.form["title"]
            author = request.form["author"]
            pages = request.form["pages"]
            genre = request.form["genre"]
            status = request.form["status"]

            c.execute("""
            UPDATE books SET title=?, author=?, pages=?, genre=?, status=? WHERE id=?
            """, (title, author, pages, genre, status, book_id))
            con.commit()
            flash("کتاب ویرایش شد.", "success")
            return redirect(url_for("dashboard"))

        c.execute("SELECT * FROM books WHERE id=?", (book_id,))
        book = c.fetchone()
    return render_template("edit_book.html", book=book)

# -----------------------------------------------------
@app.route("/password_generator")
def password_generator():
    text = "123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM[]\';,./@#$%"
    password = ''.join(random.sample(text, 12))
    return jsonify({"password": password})

# -----------------------------------------------------
@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")

# -----------------------------------------------------
if __name__ == '__main__':
    create_db()
    app.run(debug=True)
