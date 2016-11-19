
from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import flask

frontend = Blueprint('frontend', __name__)

class MyForm (FlaskForm):
    name = StringField('name', [DataRequired()])

@frontend.route('/')
def get_index():
    return flask.send_file("static/index.html", mimetype="text/html")

@frontend.route('/<filename>')
def get_file(filename):
    form = MyForm()
    return flask.render_template(filename, form=form)

@frontend.route('/images/<filename>')
def get_image(filename):
    return flask.send_from_directory('static/images', filename)

@frontend.route('/stylesheets/<filename>')
def get_stylesheets(filename):
    return flask.send_from_directory('static/stylesheets', filename)


