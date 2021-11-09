from flask import Flask, request, make_response, redirect, url_for
from flask import render_template, Markup, flash, session, jsonify, abort
import requests
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMPLATE_DIR = './templates'
STATIC_DIR = './static'

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
# app.secret_key = os.environ['secret_key']
# app.config['SECRET_KEY'] = app.secret_key


@app.route('/', methods=['GET'])
def index():
    html = 'Hello world'
    return make_response(html)