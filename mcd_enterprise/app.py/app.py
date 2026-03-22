from flask import Flask, render_template, request, redirect, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

# ---------------- DATABASE ----------------
def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        banner TEXT
    )
    """)

    # default users
    cur.execute("SELECT * FROM users")
    if not cur.fetchall():
        cur.execute("INSERT INTO users VALUES (NULL,'admin','1234','admin')")
        cur.execute("INSERT INTO users VALUES (NULL,'store','1234','store')")
        cur.execute("INSERT INTO users VALUES (NULL,'user','1234','user')")
    
    con.commit()
    con.close()

def db():
    return sqlite3.connect(DB)

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    con = db()
    pages = con.execute("SELECT * FROM pages").fetchall()
    con.close()
    return render_template("index.html", pages=pages)

# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = db()
        user = con.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p)).fetchone()
        con.close()

        if user:
            session["role"] = user[3]
            if user[3]=="admin": return redirect("/admin")
            if user[3]=="store": return redirect("/store")
            if user[3]=="user": return redirect("/user")

    return render_template("login.html")

# ADMIN
@app.route("/admin", methods=["GET","POST"])
def admin():
    if session.get("role")!="admin":
        return redirect("/login")

    con = db()

    if request.method=="POST":
        title = request.form["title"]
        content = request.form["content"]
        file = request.files["banner"]

        banner = ""
        if file and file.filename != "":
            path = "static/uploads/" + file.filename
            file.save(path)
            banner = path

        con.execute("INSERT INTO pages (title,content,banner) VALUES (?,?,?)",
                    (title,content,banner))
        con.commit()

    pages = con.execute("SELECT * FROM pages").fetchall()
    con.close()

    return render_template("admin.html", pages=pages)

# STORE
@app.route("/store")
def store():
    if session.get("role")!="store":
        return redirect("/login")
    return render_template("store.html")

# USER
@app.route("/user")
def user():
    if session.get("role")!="user":
        return redirect("/login")
    return render_template("user.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# RUN
if __name__ == "__main__":
    init_db()
    app.run(debug=True)