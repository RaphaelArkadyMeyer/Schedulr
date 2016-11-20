
from flask import Blueprint
from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired
import flask

frontend = Blueprint('frontend', __name__)

class CourseList (FlaskForm):
    max_courses = 15
    courses = []
for i in xrange(CourseList.max_courses):
    sf = wtforms.StringField('Course '+str(i))
    CourseList.courses.append(sf)
    setattr(CourseList, 'course'+str(i), sf)
    #courses = [wtforms.StringField('Course '+str(n)) for n in xrange(max_courses)]
    #course1 = wtforms.StringField("course 1")
# class UserForm (FlaskForm):
#     username = wtforms.StringField('username', [DataRequired()])
#     password = wtforms.StringField('password', [DataRequired()])
#     submitMe = wtforms.SubmitField('Submit')

@frontend.route('/')
def get_index():
    return flask.send_file("static/index.html", mimetype="text/html")

@frontend.route('/select', methods=['GET','POST'])
def get_file():
    form = CourseList()
    if form.validate_on_submit():
        return schedule([course.data for course in form.courses])
    keys = ['course'+str(i) for i in xrange(form.max_courses)]
    return flask.render_template('select.html', form=form, keys=keys)

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


