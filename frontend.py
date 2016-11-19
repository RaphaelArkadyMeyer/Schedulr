
from flask import Blueprint
import flask

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def get_index():
    return flask.send_file("static/index.html", mimetype="text/html")

@frontend.route('/images/<filename>')
def get_image(filename):
    return flask.send_from_directory('static/images', filename)

@frontend.route('/stylesheets/<filename>')
def get_stylesheets(filename):
    return flask.send_from_directory('static/stylesheets', filename)


