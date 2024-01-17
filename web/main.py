#FOK COOKIN'
from flask import Flask, request, render_template, redirect, session
from databases.handler import Handler
from helpers import apology, login_required

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


@app.route("/browse") # BROWSE METHOD. LOOK FOR NOT OWNED GAMES.
def browse():
  if request.method=="POST":

    quota = request.form.get("quote")

    games = dbs.execute(f"SELECT * FROM games WHERE name LIKE '%{quota}%'")

    return games

  else:
    return render_template("browse.html")
@app.route("/db") # ADMIN DIR. JUST FOR DB CONF
def db():
  q = request.args.get("q")
  return dbs.execute(q)

app.run(port=2137)
