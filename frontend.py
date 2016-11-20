
# coding=utf-8

from flask import Blueprint
from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired
import flask

frontend = Blueprint('frontend', __name__)

css_defs = {
        'color': {
            'link':           '#0044ee',
            'header':         '#800080',
            'headerSelected': '#a020a0',
            'background':     '#aa44aa',
            'neutral':        '#eeeeee',
            },
        }


class CourseList (FlaskForm):
    max_courses = 15
    course_keys = []
    submit_button = wtforms.SubmitField(u"Schedüle")

# Modify CourseList dynamically
# Pretend this is CourseList's constructor
for i in xrange(CourseList.max_courses):
    course_name = 'Course '+str(i)
    course_key = 'course'+str(i)
    sf = wtforms.StringField(course_name)
    setattr(CourseList, course_key, sf)
    CourseList.course_keys.append(course_key)

@frontend.route('/')
def get_index():
    return flask.render_template("base.html", mimetype="text/html")

@frontend.route('/style.css')
def get_main_stylesheet():
    css_file = flask.render_template('/style.css', renderer='bootstrap', **css_defs)
    #print(type(css_file))
    css_file = flask.make_response(css_file)
    css_file.mimetype = "text/css"
    return css_file


@frontend.route('/select', methods=['GET','POST'])
def make_schedule():
    form = CourseList()
    if form.validate_on_submit():
        return get_index()
    return flask.render_template('select.html', form=form, renderer='bootstrap')

@frontend.route('/images/<filename>')
def get_image(filename):
    return flask.send_from_directory('static/images', filename)

@frontend.route('/stylesheets/<filename>')
def get_stylesheets(filename):
    print ("stylesheet "+filename)
    return flask.send_from_directory('static/stylesheets', filename)


