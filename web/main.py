#FOK COOKIN'
from flask import Flask, request, render_template, redirect, session
from databases.handler import Handler
#from helpers import apology, login_required

from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session


''' DATABASES'''
dbs = Handler("databases/main.db")


'''APP - FLASK INTEGRATION'''
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'
Session(app)




'''ROUTES'''
@app.route("/") # INDEX OF THE PROJECT. SHOW OWNED GAMES & STUFF
def main():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  print(name)
  return render_template("index.html", website_name=name)


@app.route("/browse", methods=["GET", "POST"]) # BROWSE METHOD. LOOK FOR NOT OWNED GAMES.
def browse():
  if request.method=="POST":

    quota = request.form.get("quote")

    games = dbs.execute(f"SELECT * FROM games WHERE name LIKE '%{quota}%'")

    return games

  else:
    return render_template("browse.html")


@app.route("/login", methods=["GET", "POST"])
def login():
  session.clear()
  if request.method=="POST":
    username = request.form.get("username")
    passwd = request.form.get("passwd")

    users = dbs.execute("SELECT * FROM users")
    puser = []
    for i in users:
      if i[1]==username:
        if check_password_hash(i[2], passwd):
          puser = i

    if len(puser)==0:
      return "apology('Username or password is incorrect!')" # apology mmot implemented yet


    session["user_id"] = puser[0]

    return redirect("/")

  else:
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
  session.clear()
  if request.method=="POST":
    username = request.form.get("username")
    passwd = request.form.get("passwd")
    passwd_conf = request.form.get("passwd-confirm")


    if passwd!=passwd_conf:
      return "apology('Passwords don't match', 101)" # apology not implemented yet!
    users = dbs.execute("select name FROM users")

    for i in users:
      if username==i[0]:
        return "apology('Username already taken', 102)"


    hashd = generate_password_hash(passwd)
    starters = dbs.execute("SELECT val FROM dynamic WHERE var='start_budget'")[0][0]


    dbs.execute(f"INSERT INTO users (id, name, password, balance) VALUES ({len(users)+1}, '{username}', '{hashd}', {starters})")
    session["user_id"] = int(len(users)+1)


    return redirect("/")
  else:
    return render_template("register.html")

@app.route("/logout")
def logout():
  session.clear()
  return redirect("/login")


'''DEV STUFF'''
@app.route("/db", methods=["GET", "POST"]) # DEV DIR. JUST FOR DB CONF
def db():
  q = request.args.get("q")
  return dbs.execute(q)

@app.route("/gdb", methods=["GET", "POST"]) # GRAPHICAL DB CONF
def gdb():
  if request.method=="POST":
    q=request.form.get("query")
    return dbs.execute(q)
  else:
    return render_template("query.html")

app.run(port=2137)
