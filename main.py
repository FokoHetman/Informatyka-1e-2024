#FOK COOKIN'
from flask import Flask, request, render_template, redirect, session, url_for, send_from_directory
from databases.handler import Handler
from helpers import apology, login_required
import os, json
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session





'''LANGAUGES'''
langs = ["en_US", "pl_PL"]
translate = {}

for i in langs:
  with open("static/lang/"+i+".json", "r+") as f:
    translate[i] = json.load(f)



def getLang():
  translate = {}

  for i in langs:
    with open("static/lang/"+i+".json", "r+") as f:
      translate[i] = json.load(f)
  if "user_id" in session:
    return translate[dbs.execute("SELECT lang FROM users WHERE id="+str(session["user_id"]))[0][0]]
  else:
    return translate["en_US"]





''' DATABASES'''
dbs = Handler("databases/main.db")


'''APP - FLASK INTEGRATION'''
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'
app.config["UPLOAD_FOLDER"] = "static/images/profiles"
Session(app)


'''YES'''
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/', 'favicon.ico', mimetype='image/vnd.microsoft.icon') # WINDOWS EVERYWWHERE RAAAAAAAAAAAAAAAAAAAAA



'''ROUTES'''


'''GAME HANDLER'''

@app.route("/chlang")
@login_required
def chlang():
  lang = request.args["lang"]
  dbs.execute("UPDATE users SET lang='"+lang+"' WHERE id="+str(session['user_id']))

  return redirect("/profile")



@app.route("/play")
@login_required
def play():
  id = request.args["id"]
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  if id:
    gamedata = dbs.execute("SELECT * FROM gamedata WHERE id="+str(id))[0]

    return render_template("games/"+gamedata[1], dbs=dbs, str=str, website_name=name, library=False, game=dbs.execute("SELECT * FROM games WHERE id="+str(id))[0], lang=getLang(), name=name)
  return apology("id not found..")






@app.route("/wallet", methods=["GET", "POST"])
@login_required
def wallet():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  if request.method=="POST":

    new_amount = request.values["money"]

    old_amount = dbs.execute("SELECT balance FROM users WHERE id="+str(session["user_id"]))[0][0]
    dbs.execute("UPDATE users SET balance="+str(int(old_amount)+int(new_amount))+" WHERE id="+str(session["user_id"]))

    return render_template("transsuccess.html", dbs=dbs, str=str, library=True, website_name=name, item=str(new_amount)+"$", lang=getLang(), name=name)
  else:
    return render_template("wallet.html", dbs=dbs, str=str, library=True, website_name=name, lang=getLang(), name=name)








@app.route("/about", methods=["GET"])
def about():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  return render_template("about.html", website_name=name, dbs=dbs, str=str, library=True, lang=getLang(), name=name)


@app.route("/") # INDEX OF THE PROJECT. SHOW OWNED GAMES & STUFF
def main():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  return render_template("index.html", website_name=name, str=str, library=True, dbs=dbs, lang=getLang(), name=name)


@app.route("/library", methods=["GET", "POST"])
@login_required
def library():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  '''owneds = dbs.execute(f"SELECT games FROM users WHERE id={session['user_id']}")
  games = []
  for i in list(owneds):
    games.append(dbs.execute(f"SELECT * FROM games WHERE id={i}"))

  if request.method=="POST":
    query = request.form.get("gquery")
    qgames = []
    for i in games:
      if query in i[0][1]:
        qgames.append(i)
'''
  #return render_template("library.html", games=qgames, str=str, dbs=dbs, website_name=name)
  return render_template("library.html", str=str, dbs=dbs, website_name=name, lang=getLang(), name=name)


@app.route("/browse", methods=["GET", "POST"]) # BROWSE METHOD. LOOK FOR NOT OWNED GAMES.
def browse():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]

  if request.method=="POST":

    quota = request.form.get("quote")

    games = dbs.execute(f"SELECT * FROM games WHERE name LIKE '%{quota}%'")

    return games

  else:
    return render_template("browse.html", website_name=name, str=str, library=True, dbs=dbs, lang=getLang(), name=name)


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
      return apology(getLang()['error.inclogin'], dbs=dbs, lang=getLang(), name=name) # apology mmot implemented yet


    session["user_id"] = puser[0]

    return redirect("/")

  else:
    return render_template("login.html", website_name=name, str=str, dbs=dbs, lang=getLang(), name=name)

@app.route("/register", methods=["GET", "POST"])
def register():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  session.clear()
  if request.method=="POST":
    username = request.form.get("username")
    passwd = request.form.get("password")
    passwd_conf = request.form.get("password-confirm")


    if passwd!=passwd_conf:

      return apology(getLang()['error.passwdnomatch'], dbs=dbs, lang=getLang(), name=name)
    users = dbs.execute("select name FROM users")

    for i in users:
      if username==i[0]:
        return apology(getLang()['error.taken'], dbs=dbs, lang=getLang(), name=name)



    hashd = generate_password_hash(passwd)
    starters = dbs.execute("SELECT val FROM dynamic WHERE var='start_budget'")[0][0]


    dbs.execute(f"INSERT INTO users (id, name, password, balance, profile, theme, games, cart, lang) VALUES ({len(users)+1}, '{username}', '{hashd}', {starters}, 'images/profiles/default.svg', 0, '', '', 'en_US')")
    session["user_id"] = int(len(users)+1)


    return redirect("/")
  else:
    return render_template("register.html", website_name=name, str=str,dbs=dbs, lang=getLang(), name=name)

@app.route("/logout")
def logout():
  session.clear()
  return redirect("/login")

# Funny red dot in visual studio code on the left

'''CART AND GAME MANAGMENT'''
@app.route("/gameview")
def gameview():
  id = request.args['id']
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  game = dbs.execute(f"SELECT * FROM games WHERE id={id}")[0]
  print('hi')

  print(id)

  return render_template("gameview.html", game=game, dbs=dbs, website_name=name, str=str, lang=getLang(), name=name)

@app.route('/cart')
@login_required
def cart():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  game_sum = 0
  for i in dbs.execute("SELECT * FROM games"):
    if str(i[0]) in dbs.execute("SELECT cart FROM users WHERE id=" + str(session['user_id']))[0][0]:
      game_sum+=i[-1]
  return render_template("cart.html", dbs=dbs, website_name=name, str=str, game_sum=game_sum, lang=getLang(), name=name)


@app.route('/modcart')
@login_required
def modcart():
  id = request.args['id']
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]

  owned = dbs.execute("SELECT games FROM users WHERE id=" + str(session['user_id']))[0][0]

  if str(id) in owned:
    return apology(getLang()['error.owned'], dbs=dbs, lang=getLang())

  ncart = ""
  if dbs.execute("SELECT cart FROM users WHERE id=" + str(session["user_id"]))[0][0]:
    ncart+=str(dbs.execute("SELECT cart FROM users WHERE id=" + str(session["user_id"]))[0][0])

  if str(id) not in ncart:
    ncart+=str(id)
  dbs.execute(f"UPDATE users SET cart='{ncart}' WHERE id=" + str(session['user_id']))

  return redirect(url_for('cart'))

@app.route('/modcartdel')
@login_required
def modcartdel():
  id = request.args['id']
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]

  ncart = ""
  if dbs.execute("SELECT cart FROM users WHERE id=" + str(session["user_id"]))[0][0]:
    ncart+=str(dbs.execute("SELECT cart FROM users WHERE id=" + str(session["user_id"]))[0][0])

  if str(id) in ncart:
    ncart=ncart.replace(str(id), "", 1)
  dbs.execute(f"UPDATE users SET cart='{ncart}' WHERE id=" + str(session['user_id']))

  return redirect(url_for('cart'))


@app.route("/buycart")
@login_required
def buyall():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]

  game_sum=0
  cart = dbs.execute("SELECT cart FROM users WHERE id=" + str(session['user_id']))[0][0]
  owned = dbs.execute("SELECT games FROM users WHERE id=" + str(session['user_id']))[0][0]
  print(owned)

  for i in dbs.execute("SELECT * FROM games"):
    if str(i[0]) in cart and str(i[0]) not in owned:
      game_sum+=i[-1]
  if game_sum>dbs.execute("SELECT balance FROM users WHERE id=" + str(session['user_id']))[0][0]:
    return apology(getLang()['error.lackcash'], dbs=dbs, name=name, lang=getLang())

  ngames = ""
  if owned:
    ngames+=owned
  for i in dbs.execute("SELECT * FROM games"):
    if str(i[0]) in cart:
      ngames+=str(i[0])
  nbal = dbs.execute("SELECT balance FROM users WHERE id="+str(session['user_id']))[0][0]-game_sum
  dbs.execute(f"UPDATE users SET games='{ngames}', cart='', balance={nbal} WHERE id="+str(session['user_id']))
  return render_template("transsuccess.html", dbs=dbs, str=str, item="gry z koszyka", lang=getLang(), website_name=name)



@app.route("/buy")
def buy():
  id = request.args["id"]
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]

  if str(id) in dbs.execute("SELECT games FROM users WHERE id=" + str(session['user_id']))[0][0]:
    return apology(getLang()['error.owned'], dbs=dbs, name=name, lang=getLang())

  if dbs.execute("SELECT price FROM games WHERE id="+str(id))[0][0]>dbs.execute("SELECT balance FROM users WHERE id=" + str(session['user_id']))[0][0]:
    return apology(getLang()['error.lackcash'], dbs=dbs, name=name, lang=getLang())
  new_bal = dbs.execute("SELECT balance FROM users WHERE id=" + str(session['user_id']))[0][0] - dbs.execute("SELECT price FROM games WHERE id="+str(id))[0][0]

  ngames = dbs.execute("SELECT games FROM users WHERE id="+str(session['user_id']))[0][0] + str(id)

  dbs.execute(f"UPDATE users SET balance={new_bal}, games='{ngames}' WHERE id="+str(session['user_id']))
  return render_template("transsuccess.html", dbs=dbs, str=str, item=dbs.execute("SELECT name FROM games WHERE id="+str(id))[0][0], lang=getLang(), website_name=name)

'''USER CUSTOMISATION'''

def allowed_file(filename):
    return '.' in filename




@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
  name = dbs.execute("SELECT val FROM dynamic WHERE var='site_name'")[0][0]
  if request.method=="POST":
    new_user = request.form.get("nusername")
    new_passwd = request.form.get("npassword")
    new_passwd_conf = request.form.get("npassword-conf")
    old_passwd = request.form.get("opassword")


    cur_passwd = dbs.execute(f"SELECT password FROM users WHERE id={session['user_id']}")[0][0]

    if new_passwd:
      if not check_password_hash(cur_passwd, old_passwd):
        return apology(getLang()['error.incpasswd'], dbs=dbs, name=name, lang=getLang())
      if new_passwd != new_passwd_conf:
         return apology(getLang()['error.passwwdnomatch'], dbs=dbs, name=name, lang=getLang())
      dbs.execute(f"UPDATE users SET password='{generate_password_hash(new_passwd)}' WHERE id={session['user_id']}")


    if new_user:
      dbs.execute(f"UPDATE users SET name='{new_user}' WHERE id={session['user_id']}")


    if 'file' in request.files:
      file = request.files['file']

      if not file.filename=='':

        if file and "." in file.filename:
          fname=str(session["user_id"]) + "." + file.filename.rsplit(".", 1)[1].lower()
          file.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
          dbs.execute(f"UPDATE users SET profile='images/profiles/{fname}' WHERE id={session['user_id']}")

    return redirect("/")
  else:
    return render_template("profile.html", website_name=name, str=str,dbs=dbs, lang=getLang(), name=name)


@app.route("/changetheme", methods=["POST"])
@login_required
def change_theme():
  theme_id = int(request.form['javascript_data'])
  dbs.execute(f"UPDATE users SET theme={theme_id} WHERE id={session['user_id']}")
  return ""


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
    return render_template("query.html", website_name=name, str=str,dbs=dbs, lang=getLang(), name=name)


app.run(port=2137, host='0.0.0.0')
