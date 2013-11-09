from flask import g, request, session, redirect, flash, Flask

app = Flask(__name__)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    return app.groups

@app.route('/addgroup')
def add_group():
    app.groups[request.groupname] = []

@app.route('/addtogroup')
def add_to_group():
    app.groups[request.groupname].append(request.username)

@app.route('/adduser')
def add_user():
    app.users[request.username] = []

@app.route("/wakeuptime", methods=['POST'])
def update_wakeuptime():
    app.users[request.username].append(request.delay)

@app.route("/getresults")
def send_results():
    results = calculate_results(app.users, app.groups)
    return results[request.username]

if __name__ == "__main__":
    app.groups = {}
    app.users = {} # map from username to (group, list of delays)
    app.run(debug=False, host='0.0.0.0', port=8080)
