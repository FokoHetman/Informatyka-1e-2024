#FOK COOKIN'
from flask import Flask, request, render_template, redirect, session
from databases.handler import Handler
#from helpers import apology, login_required
import os
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session


''' DATABASES'''
dbs = Handler("databases/main.db")


'''APP - FLASK INTEGRATION'''
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'
app.config["UPLOAD_FOLDER"] = "static/images/profiles"
Session(app)




'''ROUTES'''

@app.route("/about", methods=["GET"])
def about():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  return render_template("about.html", website_name=name, dbs=dbs, str=str, library=True)


@app.route("/") # INDEX OF THE PROJECT. SHOW OWNED GAMES & STUFF
def main():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  return render_template("index.html", website_name=name, str=str, library=True, dbs=dbs)


@app.route("/browse", methods=["GET", "POST"]) # BROWSE METHOD. LOOK FOR NOT OWNED GAMES.
def browse():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]

  if request.method=="POST":

    quota = request.form.get("quote")

    games = dbs.execute(f"SELECT * FROM games WHERE name LIKE '%{quota}%'")

    return games

  else:
    return render_template("browse.html", website_name=name, str=str, library=True, dbs=dbs)


@app.route("/login", methods=["GET", "POST"])
def login():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  session.clear()
  if request.method=="POST":
    username = request.form.get("username")
    passwd = request.form.get("password")

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
    return render_template("login.html", website_name=name, str=str, dbs=dbs)

@app.route("/register", methods=["GET", "POST"])
def register():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  session.clear()
  if request.method=="POST":
    username = request.form.get("username")
    passwd = request.form.get("password")
    passwd_conf = request.form.get("password-confirm")


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
    return render_template("register.html", website_name=name, str=str,dbs=dbs)

@app.route("/logout")
def logout():
  session.clear()
  return redirect("/login")


'''USER CUSTOMISATION'''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "png"




@app.route("/profile", methods=["GET", "POST"])
def profile():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  if request.method=="POST":
    new_user = request.form.get("nusername")
    new_passwd = request.form.get("npassword")
    new_passwd_conf = request.form.get("npassword-conf")
    old_passwd = request.form.get("opassword")


    cur_passwd = dbs.execute(f"SELECT password FROM users WHERE id={session['user_id']}")[0][0]


    if not check_password_hash(cur_passwd, old_passwd):
      return "apology('incorrect password')"

    if new_passwd:
      if new_passwd != new_passwd_conf:
        return "apology('passwords dont match')"
      dbs.execute(f"UPDATE users SET password='{generate_password_hash(new_passwd)}' WHERE id={session['user_id']}")


    if new_user:
      dbs.execute(f"UPDATE users SET name='{new_user}' WHERE id={session['user_id']}")


    if 'file' in request.files:
      file = request.files['file']

      if not file.filename=='':
        print(file, allowed_file(file.filename))
        if file and allowed_file(file.filename):
          fname=str(session["user_id"]) + "." + file.filename.rsplit(".", 1)[1].lower()
          file.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
          dbs.execute(f"UPDATE users SET profile='{os.path.join(app.config['UPLOAD_FOLDER'], fname)}' WHERE id={session['user_id']}")

    return redirect("/")
  else:
    return render_template("profile.html", website_name=name, str=str,dbs=dbs)




'''DEV STUFF'''
@app.route("/db", methods=["GET", "POST"]) # DEV DIR. JUST FOR DB CONF
def db():
  q = request.args.get("q")
  return dbs.execute(q)

@app.route("/gdb", methods=["GET", "POST"]) # GRAPHICAL DB CONF
def gdb():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  if request.method=="POST":
    q=request.form.get("query")
    return dbs.execute(q)
  else:
    return render_template("query.html", website_name=name, str=str,dbs=dbs)


app.run(port=2137, host='0.0.0.0')
