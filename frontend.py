
# coding=utf-8

from flask import Blueprint
from flask_wtf import FlaskForm
import wtforms
import wtforms.validators
import flask

import re

frontend = Blueprint('frontend', __name__)

css_defs = {
        'color': {
            'courses': ['#f00', '#0f0', '#00f', '#ff0', '#0ff', '#f0f'],
            'link':           '#0044ee',
            'header':         '#20083c',
            'headerSelected': '#431e6c',
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
    sf = wtforms.StringField(course_name,validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Regexp(r'[a-zA-Z]+[0-9]+')
            ])
    setattr(CourseList, course_key, sf)
    CourseList.course_keys.append(course_key)

@frontend.route('/')
def get_index():
    return flask.render_template("base.html", mimetype="text/html")

@frontend.route('/stylesheets/style.css')
def get_main_stylesheet():
    css_file = flask.render_template('/style.css', renderer='bootstrap', **css_defs)
    css_file = flask.make_response(css_file)
    css_file.mimetype = "text/css"
    return css_file

def safe_cast(from_object, to_type, default=None):
    try:
        return to_type(from_object)
    except (ValueError, TypeError):
        return default
"""
Generates a schedule page
@gen an iterable of strings
"""
def generate_schedule(gen):
    def schedule_styler():
        i = 0
        for [dept,num] in gen:
            start_time   = safe_cast(num,int,0) % 1000
            days_of_week = [safe_cast(num,int,0) % 7]
            duration = 50
            color = css_defs['color']['courses'][i % len(css_defs['color']['courses'])]
            i+=1
            top = str(start_time - 0*7*60)+'px'
            size = str(duration) + 'px'
            for day in days_of_week:
                left = '0'
                if day == 2:
                    left = '20%'
                elif day == 3:
                    left = '40%'
                elif day == 4:
                    left = '60%'
                elif day == 5:
                    left = '80%'
                yield {
                        'color': color,
                        'left':  left,
                        'top':   top,
                        'size':  size,
                    }
    return flask.render_template('schedule.html', fields=schedule_styler())


@frontend.route('/select', methods=['GET','POST'])
def make_schedule():
    form = CourseList()
    if form.validate_on_submit():
        def preprocess_courses():
            for key in form.course_keys:
                course = form[key].data
                if course:
                    [name,number] = re.findall(r'[a-zA-Z]+|[0-9]+', course)
                    number = '{:<05d}'.format( int(number) )
                    yield [name,number]
        return generate_schedule(preprocess_courses())
    return flask.render_template('select.html', form=form, renderer='bootstrap')

@frontend.route('/images/<filename>')
def get_image(filename):
    return flask.send_from_directory('static/images', filename)

@frontend.route('/stylesheets/<filename>')
def get_stylesheets(filename):
    print ("stylesheet "+filename)
    return flask.send_from_directory('static/stylesheets', filename)


