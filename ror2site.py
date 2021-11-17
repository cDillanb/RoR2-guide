from flask import Flask, render_template, redirect, flash, session, request, g
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = "!#tgq325#Q$%JUq3FAQGtjnrdaj$Umfmu"

@app.route("/")
def index():
    """Returns the homepage"""

    return render_template("homepage.html")


@app.route("/main")
def main():
    """Returns main navigation page"""

    return render_template("main.html")


@app.route("/items")
def list_items():
    conn = get_db()
    c = conn.cursor()

    result = c.execute("""SELECT id, name, description, rarity FROM Items 
    ORDER BY CASE rarity when 'Common' then 1 when 'Uncommon' then 2 when 'Legendary' then 3 when 'Equipment' then 4 when 'Boss/Planet' then 5 else 6 end""")

    items = []
    for row in result:
        item = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "rarity": row[3],
        }
        items.append(item)


    conn.commit()
    return render_template("items.html", items=items)


@app.route("/item/<item_id>")
def show_item(item_id):
    conn = get_db()
    c = conn.cursor()

    result1 = c.execute(f"""SELECT name, description, rarity, challenge_id FROM Items
    WHERE id = {item_id}""")
    
    for row in result1:
        item = {
            "name": row[0],
            "description": row[1],
            "rarity": row[2],
            "challenge_id": row[3]
        }

    result2 = c.execute(f"""
    SELECT id, name FROM Challenges
    ORDER BY id""")


    challenges = []
    for row in result2:
        challenge = {
            "id": row[0],
            "name": row[1]
        }
        challenges.append(challenge)

    conn.commit()
    return render_template("item_details.html", item=item, challenges=challenges)


@app.route("/login", methods=["GET"])
def show_login():
    return render_template("login.html")



@app.route("/login", methods=["POST"])
def process_login():
    conn = get_db()
    c = conn.cursor()

    username = request.form.get('username')
    password = request.form.get('password')

    try: 
        users = c.execute(f"""SELECT id, username, password FROM Users
                    WHERE username = '{username.lower()}'""")

    except:
        flash("No such username exists")
        return redirect('/login')

    try:
        if users:
            results = users.fetchall()[0]
    except:
        flash("No such username exists")
        return redirect('/login')

    try:
        user = {
            "id": results[0],
            "username": results[1],
            "password": results[2]
        }
    
    except:
        flash("Something went wrong")
        return redirect("/login")


    if not check_password_hash(user["password"], password) :
        flash("Incorrect password")
        return redirect('/login')

    conn.commit()
    session["logged_in_username"] = user["username"]
    session["logged_in_id"] = user["id"]

    flash(f"Successfully logged in as {user['username']}")
    return redirect("/main")


@app.route("/logout")
def process_logout():

    del session["logged_in_username"]
    del session["logged_in_id"]
    flash("Logged Out")
    return redirect("/main")


@app.route("/signup", methods=["GET"])
def show_signup():
    return render_template("signup.html")


@app.route("/signup", methods=["POST"])
def process_signup():
    conn = get_db()
    c = conn.cursor()

    new_username = request.form.get('username')
    new_password = request.form.get('password')

    if not new_username or not new_password:
        return redirect("/signup")

    if new_password != request.form.get('confirm_password'):
        flash("Passwords do not match")
        return redirect("/signup")
    
    try:
        c.execute(f"""INSERT INTO Users (username, password, date_account_created)
        VALUES (?,?,?)""",(new_username.lower(), generate_password_hash(new_password, method='sha256'), datetime.now()))
                    
    except:
        flash("Username already exists or something went wrong")
        return redirect("/signup")

    flash("Account created")
    conn.commit()
    return redirect("/signup")


@app.route("/characters")
def list_characters():
    conn = get_db()
    c = conn.cursor()

    result = c.execute("""SELECT id, name, description FROM Characters
    ORDER BY id""")

    characters = []
    for row in result:
        character = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
        }
        characters.append(character)


    conn.commit()
    return render_template("characters.html", characters=characters)


@app.route("/character/<character_id>")
def char_details(character_id):
    conn = get_db()
    c = conn.cursor()

    result1 = c.execute(f"""SELECT id, name, description, health, health_regen, damage, speed, armor, challenge_id FROM Characters
    WHERE id = {character_id}""")
    
    for row in result1:
        character = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "health": row[3],
            "health_regen": row[4],
            "damage": row[5],
            "speed": row[6],
            "armor": row[7],
            "challenge_id": row[8]
        }

    result2 = c.execute(f"""
    SELECT id, name FROM Challenges
    ORDER BY id""")


    challenges = []
    for row in result2:
        challenge = {
            "id": row[0],
            "name": row[1]
        }
        challenges.append(challenge)

    result3 = c.execute(f"""SELECT name, description, type FROM Abilities
    WHERE character_id = {character_id}""")

    abilities = []
    for row in result3:
        ability = {
            "name": row[0],
            "description": row[1],
            "type": row[2]
        }
        abilities.append(ability)

    conn.commit()
    return render_template("char_details.html", character=character, challenges=challenges, abilities=abilities)


@app.route("/challenges")
def list_challenges():
    conn = get_db()
    c = conn.cursor()

    result = c.execute("""SELECT id, name, description FROM Challenges
    ORDER BY id""")

    challenges = []
    for row in result:
        challenge = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
        }
        challenges.append(challenge)

    if session.get("logged_in_id"):

        conn = get_db()
        c = conn.cursor()
        result = c.execute(f"""SELECT COUNT(challenge_id) FROM Challenges_completed
        WHERE user_id = {session.get("logged_in_id")}""")
        
        var = result.fetchall()

        challenge_count = var[0][0]

        result2 = c.execute(f"""SELECT challenge_id FROM Challenges_completed
        WHERE user_id = {session.get("logged_in_id")}""")

        challenges_completed = []

        for row in result2:
            challenges_completed.append(row[0])
        conn.commit()
        return render_template("challenges.html", challenges=challenges, challenges_completed=challenges_completed, challenge_count=challenge_count)

    conn.commit()
    return render_template("challenges.html", challenges=challenges)


@app.route("/challenge/<challenge_id>", methods=["GET"])
def challenge_details(challenge_id):
    conn = get_db()
    c = conn.cursor()

    result1 = c.execute(f"""SELECT id, name, description FROM Challenges
    WHERE id = {challenge_id}""")
    
    for row in result1:
        challenge = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
        }
    try:
        result2 = c.execute(f"""SELECT challenge_id FROM Challenges_completed
        WHERE user_id = '{session.get("logged_in_id")}' AND challenge_id = {challenge_id}""")
        challenge_completed = result2.fetchall()[0]

    except:
        conn.commit()
        return render_template("challenge_details.html", challenge=challenge)


    completed_challenge_id = challenge_completed[0]

    conn.commit()
    return render_template("challenge_details.html", challenge=challenge, completed_challenge_id=completed_challenge_id)


@app.route("/challenge/<challenge_id>", methods=["POST"])
def process_challenge(challenge_id):
    conn = get_db()
    c = conn.cursor()

    if not session.get("logged_in_id"):
            flash("Log in to use this feature")
            return redirect(f"/challenge/{challenge_id}")

    elif request.form.get("submit-btn") == 'Undo':

        c.execute(f"""DELETE FROM Challenges_completed
        WHERE user_id = {session.get("logged_in_id")} AND challenge_id = {challenge_id}""")

    elif request.form.get("submit-btn") == 'Apply':

        c.execute("""INSERT INTO Challenges_completed (user_id, challenge_id)
        VALUES (?,?)""", (session.get("logged_in_id"), challenge_id))

    conn.commit()
    return redirect(f"/challenge/{challenge_id}")


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        g._database = sqlite3.connect("db/RoR2-Data.db")
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run()