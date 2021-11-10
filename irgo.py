from flask import Flask, request, make_response, redirect, url_for
from flask import render_template, Markup, flash, session, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash, gen_salt
import flask_login
import requests
import os
import urllib3
import database as db
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMPLATE_DIR = './templates'
STATIC_DIR = './static'

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


@app.route('/', methods=['GET'])
def index():
    html = render_template('index.html')
    return make_response(html)

#-----------------------------------------------------------------------
@app.route('/workouts', methods=['GET'])
def workouts():

    workouts = db.getAllWorkouts()

    html = render_template('workouts.html' ,workouts=workouts)
    return make_response(html)

@app.route('/workout', methods=['GET'])
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

    html = render_template('workout.html' , workout=workout, scores=scores, athletes=athletes)
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