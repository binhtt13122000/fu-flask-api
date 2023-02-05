import os
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
cred = credentials.Certificate('firebase_admin_sdk.json')
default_app = initialize_app(cred)

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, Flask!"
