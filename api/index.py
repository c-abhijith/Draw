from run import app
from flask import Flask, send_from_directory
import os

@app.route('/static/<path:path>')
def static_file(path):
    return send_from_directory('static', path)

app.static_folder = 'static'

def handler(request):
    return app(request) 