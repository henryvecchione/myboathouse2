from flask import Flask, request, make_response, redirect, url_for
from flask import render_template, Markup, flash, session, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash, gen_salt
import flask_login
import requests
import os
import urllib3
import database as db
import random
import bcrypt
import secret

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMPLATE_DIR = './templates'
STATIC_DIR = './static'

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

app.secret_key = secret.secret_key
app.config['SECRET_KEY'] = app.secret_key

login_manager = flask_login.LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass


@app.route('/', methods=['GET'])
def index():
    html = render_template('index.html')
    return make_response(html)
# ---------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    error=''
    if request.method == 'POST':

        email = request.form['username']
        password = bytes(request.form['password'],'utf-8')

        creds = db.getCredentials(email)


        session.clear()

        # getCredentials returns none if email not found in DB
        if not creds:
            error = 'Missing Credentials. Please try again.'
        # else check password hash
        else:
            user = user_loader(email)   
            email = creds['email']
            pwHash = creds['pwHash']
            salt = creds['salt']

            verified = bcrypt.checkpw(password, pwHash)
            if verified:
                flask_login.login_user(user)
                session.permanent = False
                return redirect('/workouts')
            else:
                error = 'Invalid Credentials. Please try again.'
            


    return render_template('login.html', error=error)


@login_manager.user_loader
def user_loader(email):
    creds = db.getCredentials(email)
    if not creds:
        return

    user = User()
    user.id = creds['_id']
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if not email:
        return

    creds = db.getCredentials(email)

    user = User()
    user.id = creds['_id']
    
    password = bytes(request.form['password'], 'utf-8')
    user.is_authenticated = bcrypt.checkpw(password, creds['pwhash'])

    return user
#-----------------------------------------------------------------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    error =''

    if request.method =='POST':
        for k in request.form.keys():
            print(k)
        first = request.form['first']
        last = request.form['last']
        email = request.form['username']
        password = bytes(request.form['password'], 'utf-8')
        classYr = request.form['class']
        side = request.form['side']

        
        salt = bcrypt.gensalt()
        pwhash = bcrypt.hashpw(password, salt)

        checkIfNew = db.getCredentials(email)
        if checkIfNew:
            error = 'Account already exists with this email'
        else:
            newId = random.randint(10, 100000)
            add = db.addCredentials(newId, email, pwhash, salt)
            if not add:
                error = 'failed to add user'

            athlete = {
                "_id" : newId,
                "first" : first,
                "last" : last,
                "permissions" : [],
                "prs" : {
                    "2000m" : '-1',
                    "6000m" : '-1'
                },
                "workouts" : [],
                "side" : side,
                "class" : classYr,
                "active" : True,
                "awards" : {
                    "earc" : [],
                    "ira" : [],
                    "shirts" : []
                },
                "teamId" : 1
            }

            add = db.addAthlete(athlete)
            if not add:
                error = "failed to add user"

            return()



    html = render_template('signup.html', error=error)
    return make_response(html)



#-----------------------------------------------------------------------
@app.route('/workouts', methods=['GET'])
@flask_login.login_required
def workouts():

    workouts = db.getAllWorkouts()

    html = render_template('workouts.html' ,workouts=workouts)
    return make_response(html)

@app.route('/workout', methods=['GET'])
@flask_login.login_required
def workout():
    workoutId = request.args.get('w')
    workout = db.queryWorkout(workoutId)

    scores = workout['scores']
    print(scores)
    athleteIds = scores.keys()
    athletes = {}
    for athleteId in athleteIds:
        ath = db.queryAthlete(athleteId)
        athletes[athleteId] = {
            'first' : ath['first'],
            'last' : ath['last'],
            'side' : ath['side']
        }

    html = render_template('workout_dropdown.html' , workout=workout, scores=scores, athletes=athletes)
    return make_response(html)





#-----------------------------------------------------------------------


@app.route('/allWorkouts', methods=['GET'])
def allWorkouts():
    wo = db.getAllWorkouts()
    html = ''
    for w in wo:
        html += str(w) +"\n"
    return make_response(html)

@app.route('/allAthletes', methods=['GET'])
def allAthletes():
    ath = db.getAllAthletes()
    html = ''
    for a in ath:
        html += str(a) + '\n'
    return make_response(html)