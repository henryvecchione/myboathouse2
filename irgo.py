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
import xlsxMethods
from io import StringIO
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMPLATE_DIR = './templates'
STATIC_DIR = './static'


if 'secret_key' not in os.environ:
    from dotenv import load_dotenv
    load_dotenv()
    secret_key = os.environ.get('secret_key')
else:
    secret_key = os.environ['secret_key']

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

app.secret_key = secret_key
app.config['SECRET_KEY'] = app.secret_key

login_manager = flask_login.LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

#-----------------------------------------------------------------------
""" flask_login methods """
#-----------------------------------------------------------------------

""" loads a user from the database, using their email as the key """
@login_manager.user_loader
def user_loader(email):
    creds = db.getCredentials(email)
    if not creds:
        return

    user = User()
    user.id = creds['_id']

    return user

""" loads the user using the 'email' cookie set during login"""
@login_manager.request_loader
def request_loader(request):
    print(request.headers)
    email = request.cookies.get('email')
    if not email:
        return

    creds = db.getCredentials(email)
    user = User()
    user.id = creds['_id']
    
    return user


#-----------------------------------------------------------------------
""" Static page rendering """
#-----------------------------------------------------------------------

""" renders the index page """
@app.route('/', methods=['GET'])
def index():
    html = render_template('index.html')
    return make_response(html)

""" renders the home page """
@flask_login.login_required
@app.route('/home', methods=['GET'])
def home():
    email = request.cookies.get('email')
    user = user_loader(email)
    athlete = db.queryAthlete(user.id)
    html = render_template('home.html', perms=athlete['permissions'])
    return make_response(html)


#-----------------------------------------------------------------------
""" File upload and download methods """
#-----------------------------------------------------------------------

""" download a blank .xlsx file for recording a workout """
@app.route('/download')
def download():
    try:
        blankOutput = xlsxMethods.xlsxBlank()
        response = Response()
        response.data = blankOutput.read()
        response.status_code = 200
        filename = 'workout_{}.xlsx'.format(datetime.now().strftime('%d/%m/%Y'))
        mimetype_tuple = mimetypes.guess_type(file_name)
        response_headers = Headers({
            'Pragma': "public",  # required,
            'Expires': '0',
            'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
            'Cache-Control': 'private',  # required for certain browsers,
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': 'attachment; filename=\"%s\";' % file_name,
            'Content-Transfer-Encoding': 'binary',
            'Content-Length': len(response.data)
        })

        if not mimetype_tuple[1] is None:
            response.update({
                'Content-Encoding': mimetype_tuple[1]
            })
        response.headers = response_headers
        response.set_cookie('fileDownload', 'true', path='/')
        return response
    except Exception as e:
        print(e)

""" upload a .xlsx file for processing and storing in database """
@app.route('/upload')
def upload():
    return NotImplemented

#-----------------------------------------------------------------------
""" Authentication methods """
#-----------------------------------------------------------------------

""" renders the login page and processes user logins"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    error=''

    # if the user has already logged in (and has not logged out)
    # sign them in
    email = request.cookies.get('email')
    if email:
        user = user_loader(email)
        athlete = db.queryAthlete(user.id)
        return redirect('/home')

    # on form submission (POST request)
    if request.method == 'POST':

        # get email and password from form
        email = request.form['username']
        password = bytes(request.form['password'],'utf-8')
        # get the credentials 
        creds = db.getCredentials(email)

        session.clear()

        # getCredentials returns none if email not found in DB
        if not creds:
            error = 'Missing Credentials. Please try again.'
        # else check password hash
        else:

            email = creds['email']
            pwHash = creds['pwHash']
            salt = creds['salt']
            # check the entered password against that in database
            verified = bcrypt.checkpw(password, pwHash)
            if verified:
                user = user_loader(email)
                flask_login.login_user(user)
                session.permanent = False
                res = redirect('/home')
                res.set_cookie('email', email)
                return res
            else:
                error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)

""" log out the user """
@flask_login.login_required
@app.route('/logout')
def logout():
    flask_login.logout_user()
    res = redirect('/')
    # set the email cookie to empty, make it expire 
    res.set_cookie('email', '', expires=0)
    return res


""" sign up a new user """
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    error = ''
    # on form submission
    if request.method =='POST':
        # get form inputs 
        first = request.form['first']
        last = request.form['last']
        email = request.form['username']
        password = bytes(request.form['password'], 'utf-8')
        classYr = request.form['class']
        side = request.form['side']

        salt = bcrypt.gensalt()
        pwhash = bcrypt.hashpw(password, salt)

        # check if this email is already in database
        checkIfNew = db.getCredentials(email)
        if checkIfNew:
            error = 'Account already exists with this email'
        else:
            # TODO: ensure noncollision in assigning IDs
            newId = random.randint(10, 100000)
            # add the login credentials to credentials DB
            add = db.addCredentials(newId, email, pwhash, salt)
            if not add:
                error = 'failed to add user'

            # create athlete document from entered info
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
            # add athlete document to athlete db
            add = db.addAthlete(athlete)
            if not add:
                error = "failed to add user"

            html = render_template('home.html')
            return make_response(html)


    html = render_template('signup.html', error=error)
    return make_response(html)

#-----------------------------------------------------------------------
""" data-based page rendering """
#-----------------------------------------------------------------------

""" display all workouts """
@flask_login.login_required
@app.route('/workouts', methods=['GET'])
def workouts():
    # load the user
    email = request.cookies.get('email')
    user = user_loader(email)

    workouts = db.getAllWorkouts()

    html = render_template('workouts.html' ,workouts=workouts)
    return make_response(html)

""" display a single workout """
@flask_login.login_required
@app.route('/workout', methods=['GET'])
def workout():
    # load the user 
    email = request.cookies.get('email')
    user = user_loader(email)

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
""" other and testing """
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
