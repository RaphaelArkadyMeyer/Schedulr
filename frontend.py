
from flask import Blueprint
from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired
import flask

frontend = Blueprint('frontend', __name__)

class CourseList (FlaskForm):
    max_courses = 15
    course_keys = []
    submit_button = wtforms.SubmitField("Schedüle")

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
    return flask.send_file("static/index.html", mimetype="text/html")

@frontend.route('/select', methods=['GET','POST'])
def get_file():
    form = CourseList()
    if form.validate_on_submit():
        return schedule([course.data for course in form.courses])
    return flask.render_template('select.html', form=form)

# @frontend.route('/form.html', methods=['POST'])
def handle_login(args):
    print(args)
    return get_index()

@frontend.route('/images/<filename>')
def get_image(filename):
    return flask.send_from_directory('static/images', filename)

@frontend.route('/stylesheets/<filename>')
def get_stylesheets(filename):
    return flask.send_from_directory('static/stylesheets', filename)


