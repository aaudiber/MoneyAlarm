import os, time
from flask import g, request, session, redirect, flash, Flask
from collections import defaultdict
# users: map from username to list of [delays list, group name]

app = Flask(__name__)

def clear_old_delays():
    for k, v in app.users.iteritems():
        app.users[k][0] = []

@app.route('/')
def show_entries():
    return str(app.groups) + "\n" + str(app.users)

@app.route('/addgroup', methods=['POST'])
def add_group():
    app.groups[request.form['groupname']] = []
    return "success\n"

@app.route('/addtogroup', methods=['POST'])
def add_to_group():
    app.users[request.form['username']][1] = request.form['groupname']
    app.groups[request.form['groupname']].append(request.form['username'])
    return "success\n"

@app.route('/adduser', methods=['POST'])
def add_user():
    app.users[request.form['username']] = [[],""]
    app.ledger[request.form['username']] = []
    return "success\n"

@app.route("/wakeuptime", methods=['POST'])
def update_wakeuptime():
    t = time.localtime()
    ts = str(t.tm_year) + str(t.tm_yday)
    delay = int(request.form['delay'])
    app.users[request.form['username']][0].append((delay, ts))
    return "success\n"


def calculate_results(users, group, cost):

    if app.day == str(t.tm_year) + str(t.tm_yday):
        return {}
    total_owed = 0
    num_oweds = 0
    balances = {} # people to (how much they owe, how much they are owed)
    for username in group:
        usersum = 0
        user_oweds = 0
        for delay in users[username][0]:
            if delay[0] > 15:
                usersum += delay[0]
            else:
                user_oweds += 1
        total_owed += usersum
        num_oweds += user_oweds
        balances[username] = (usersum, user_oweds)

   # Take our cut of $$$$
    our_cut = 0.9*total_owed
    remainder_owed = total_owed - our_cut

    if num_oweds == 0:
        avg_payout = 0
    else:
        avg_payout = float(remainder_owed) / num_oweds

    positive = []
    negative = []
    for user, balance in balances.items():
        owes, oweds = balance
        profit = oweds * avg_payout - owes
        if profit > 0:
            positive.append((user, profit))
        if profit < 0:
            negative.append((user, -profit))

    if num_oweds == 0:
        positive.append(("Andrew",total_owed))
    else:
        positive.append(("Andrew",our_cut))

    payments = defaultdict(list) # map users to (who they owe, how much)
    for p in positive:
        owed = p[1]
        while owed > 0.000001:
            if not negative:
                print "OH FUCK"
            neg = negative.pop()
            if neg[1] > owed:
                payments[neg[0]].append((p[0], owed))
                negative.append((neg[0], neg[1] - owed))
                owed = 0;
            else:
                payments[neg[0]].append((p[0], neg[1]))
                owed -= neg[1]

    clear_old_delays()
    app.day = str(t.tm_year) + str(t.tm_yday)
    return payments

@app.route("/getresults", methods=['POST'])
def send_results():
    user = request.form['username']
    results = calculate_results(app.users, app.groups[app.users[user][1]], 10)
    for ower, payment in results.items():
        app.ledger[ower].append(payment)
    return (str(app.ledger[user]) if app.ledger[user] else "you get paid") + "\n"

if __name__ == "__main__":
    os.environ['TZ'] = 'US/Eastern'
    app.groups = {}
    app.users = {} # map from username to (list of delays)
    app.ledger = {}
    t = time.localtime()
    app.day = str(t.tm_year) + str(t.tm_yday - 1)
    app.run(debug=False, host='0.0.0.0', port=8080)
