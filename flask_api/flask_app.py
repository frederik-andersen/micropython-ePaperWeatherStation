# Simple API for fetching binary images to pico ePaper weather station.
# By Frederik Andersen

from flask import Flask, redirect, request, send_file

app = Flask(__name__)

@app.route('/')
def human_interaction():
    return redirect("https://github.com/frederik-andersen")

@app.route('/api/')
def get_file():
    requested_icon = request.args.get('requested-icon')

    return send_file(f'weather_binaries/{requested_icon}.bin')
