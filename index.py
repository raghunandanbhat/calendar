from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


app = Flask(__name__)

mongo = MongoClient("mongodb://raghu:raghu123@ds257981.mlab.com:57981/cal_db")
db = mongo['cal_db']
logged_in = False
SCOPES = 'https://www.googleapis.com/auth/calendar'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))


def isLoggedIn():
    global logged_in
    return logged_in


@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/userlogin', methods=['POST', 'GET'])
def userlogin():
    users = db.users.find()
    global logged_in
    list_of_users = []
    for i in users:
        list_of_users.append(i)

    if request.method == 'POST':
        for i in list_of_users:
            if i['email'] == request.form['email']:
                if i['password'] == request.form['psw']:
                    session['email'] = i['email']
                    session['password'] = i['password']
                    logged_in = True
                    return redirect(url_for('success'))
                else:
                    return redirect(url_for('index'))
            else:
                return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/userregistration', methods=['POST', 'GET'])
def userregistration():
    users = db.users.find()
    global logged_in

    list_of_users = []
    for i in users:
        list_of_users.append(i)

    if request.method == 'POST':
        for i in list_of_users:
            if i['email'] == request.form['email']:
                return redirect(url_for('index'))
        email_id = request.form['email']
        password = request.form['psw']
        post = {'email': email_id, 'password': password}
        session['email'] = email_id
        session['password'] = password

        db.users.insert(post)
        logged_in = True
        return redirect(url_for('success'))
    else:
        return redirect(url_for('index'))


@app.route('/success')
def success():
    if not isLoggedIn():
        return redirect(url_for('index'))
    return render_template('test.html')


@app.route('/createEvent', methods=['POST'])
def createEvent():
    summary = request.form['summary']
    stime1 = request.form['stime']
    etime1 = request.form['etime']
    attendees = request.form['aemail']
    stime = stime1+":00+05:30"
    etime = etime1+":00+05:30"
    print(stime)
    print(etime)
    event = {
        'summary': summary,
        'start': {
            'dateTime': stime,
            'timeZoneName': 'Greenwich Mean Time'
        },
        'end': {
            'dateTime': etime,
            'timeZoneName': 'Greenwich Mean Time'
        },

        'attendees': [
            {'email': 'rbhat456@gmail.com'}, {'email': attendees}
        ]
    }
    event = service.events().insert(calendarId='primary', body=event, sendNotifications=True).execute()
    print('Event created : %s' % (event.get('htmlLink')))
    return render_template('test.html')


if __name__ == "__main__":
    app.run(port=8000, debug=True)
