import os, time, requests, json, calendar, datetime, sys
from threading import Timer
from flask import g, request, session, redirect, flash, Flask, url_for
from collections import defaultdict
# users: map from username to list of [delays list, group name]
from constants import *
from twilio.rest import TwilioRestClient

app = Flask(__name__)

def clear_old_delays():
    for k, v in app.users.iteritems():
        app.users[k][0] = []

@app.route('/')
def index():
    if session.get('venmo_token'):
        return redirect(url_for('static', filename='alrms.html'))
        # return 'Your Venmo token is %s' % session.get('venmo_token')
    else:
        return redirect('https://api.venmo.com/oauth/authorize?client_id=%s&scope=make_payments,access_phone,access_profile&response_type=code' % CONSUMER_ID)

@app.route('/redirect', methods = ['GET'])
def authorized():
    AUTHORIZATION_CODE = request.args.get('code')
    data = {
        "client_id":CONSUMER_ID,
        "client_secret":CONSUMER_SECRET,
        "code":AUTHORIZATION_CODE
        }
    url = "https://api.venmo.com/oauth/access_token"
    response = requests.post(url, data)

    response_dict = response.json()
    access_token = response_dict.get('access_token')
    user = response_dict.get('user')

    session['venmo_token'] = access_token
    session['venmo_username'] = user['username']
    return redirect(url_for('static', filename='alrms.html'))


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

@app.route('/alarms',methods = ['POST'])
def add_alarm():
    def totime(s):
        print s
        [h,m] = map(int, s.split(':'))
        h += 5

        t = time.gmtime()
        diff = 60 * 60 * (h - t.tm_hour) + 60 * (m - t.tm_min)
        if diff < 0:
            diff += 24 * 60 * 60

        return (time.time() + diff, diff)
    number = get_number()
    alarmTime, diff = totime(request.form['time'])
    app.alarms[number].append(alarmTime)

    def do_motherfucker():
        with app.test_request_context():
            call_num(number)
    Timer(diff, do_motherfucker, ()).start()
    return redirect(url_for('static', filename='alrms.html'))

@app.route('/alarms', methods = ['GET'])
def get_alarms():
    username = get_number()
    return json.dumps(app.alarms[username])

def get_number():
    if 'number' not in session:
        resp = requests.get("https://api.venmo.com/me?access_token=%s" %
                            session.get('venmo_token'))
        response_dict = resp.json()
        session['number'] = int(response_dict.get(u'data').get(u'phone'))
    return session['number']

def call_num(number):
    # TODO do twilio magic?
    account_sid = "ACf39739d311791f705a5b144bb028bcd4"
    auth_token  = "27976805fa4cd95997e55dbfc05bc16c"
    client = TwilioRestClient(account_sid, auth_token)
    message = client.messages.create(body="Wake up, motherfucker",
    to="+" + str(number),
    from_="+16094540383")
    print message.sid

def calculate_results(users, group, cost):
    t = time.localtime()
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

    print positive
    print negative

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
    app.alarms = defaultdict(list) # map from username to alarms for the user
    t = time.localtime()
    app.day = str(t.tm_year) + str(t.tm_yday - 1)

    if len(sys.argv) == 2:
        CONSUMER_ID = ANDREW_CONSUMER_ID
        CONSUMER_SECRET = ANDREW_CONSUMER_SECRET
        APP_SECRET = ANDREW_APP_SECRET
        p = 8081
    else:
        p = 8080
    app.secret_key = APP_SECRET
    app.run(debug=True, host='0.0.0.0', port=p)
