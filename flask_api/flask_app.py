# Simple API for fetching binary images to pico ePaper weather station.
# By Frederik Andersen

import re
from flask import Flask, abort, redirect, request, send_from_directory

app = Flask(__name__)

@app.route('/')
def human_interaction():
    return redirect("https://github.com/frederik-andersen")

@app.route('/api/')
def get_file():
    requested_icon = request.args.get('requested-icon', '')
    if not re.fullmatch(r'[a-z_]+', requested_icon): # Only icon names, no paths.
        abort(404)

    return send_from_directory('weather_binaries', f'{requested_icon}.bin')
