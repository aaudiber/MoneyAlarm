from flask import Flask
from sqlite3 import dbapi2 as sqlite3

app = Flask(__name__)

app.config.update(dict(
        DATABASE = '/tmp/getrich.db'
))

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    return rv

# Creates the database tables
def init_db():
    with app.app_contex():
        db = get_db()
        with app.open_resource('schema.sql',mode = 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Opens a new database connection if none exists
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def get_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = [dict(title = row[0], text = row[1]) for row in cur.fetchall()]
    return entries

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/wakeuptime", methods=['POST'])
def update_wakeuptime():
    lateness = request.lateness
    name = request.username
    user_groups = get_entries
    app.groups = dict()
    app.groups[


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080)
