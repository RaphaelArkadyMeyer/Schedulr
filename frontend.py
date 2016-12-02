
# coding=utf-8

from flask import Blueprint
from flask_wtf import FlaskForm
import flask_nav.elements
import wtforms
import wtforms.validators
import flask

from read_courses import CourseCache

import re

from django import template
register = template.Library()

frontend = Blueprint('frontend', __name__)

css_defs = {
        'color': {
            'courses': ['#B57EDC', '#DB7DD3 ', '#DB7DA4', '#DB857D', '#DBB47D', '#D3DB7D', '#A4DB7D', '#7DDB85'],
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


def navigation_header():
    return flask_nav.elements.Navbar(
            flask_nav.elements.View(u"Schedülr", 'frontend.make_schedule'),
            flask_nav.elements.View(u"Schedüle", 'frontend.make_schedule'),
            )


# Modify CourseList dynamically
# Pretend this is CourseList's constructor
for i in range(CourseList.max_courses):
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

days_of_the_week_offset = [
        ('Monday',    '16.666%'),
        ('Tuesday',   '33.333%'),
        ('Wednesday', '50%'),
        ('Thursday',  '66.666%'),
        ('Friday',    '83.333%')]
hours_of_the_day = [str(t)+":00AM" for t in range(7,12+1)] + [str(t)+":00PM" for t in range(1,7+1)]

def day_of_week_to_offset(day):
    x =  {
            'Monday'    : '16.666%',
            'Tuesday'   : '33.333%',
            'Wednesday' : '50%',
            'Thursday'  : '66.666%',
            'Friday'    : '83.333%'
    }.get(day, 0)
    return x

"""
Generates a schedule page
@gen an iterable of course strings (i.e. "CS252" or "CS25200")
"""
def generate_schedule(gen):
    def schedule_styler():
        i = -1
        for [dept,num] in gen:
            meetings = CourseCache.query_meeting_times(dept,num)
            for meeting in meetings:
                i            += 1
                start_time   =  CourseCache.parse_meeting_time(meeting['StartTime'])
                days_of_week =  map(day_of_week_to_offset, meeting['DaysOfWeek'].split(', '))
                duration     =  50
                description  =  dept+num+' '+meeting['Type']
                color        =  css_defs['color']['courses'][i % len(css_defs['color']['courses'])]
                top          =  str((start_time.hour-7)*60 + start_time.minute - 2.5) + 'px'
                height       =  str(duration-5) + 'px'
                for left in days_of_week:
                    yield {
                            'description': description,
                            'color':       color,
                            'left':        left,
                            'top':         top,
                            'height':      height,
                        }
    return flask.render_template(
            'schedule.html',
            fields=schedule_styler(),
            days_of_the_week_offset=days_of_the_week_offset,
            hours_of_the_day=hours_of_the_day)


@frontend.route('/select', methods=['GET','POST'])
def make_schedule():
    form = CourseList()
    if form.validate_on_submit():
        def preprocess_courses():
            for key in form.course_keys:
                course = form[key].data
                if course:
                    [name,number] = re.findall(r'[a-zA-Z]+|[0-9]+', course)
                    name = name.upper()
                    number = '{:<05d}'.format( int(number) )
                    yield [name,number]
        return generate_schedule(preprocess_courses())
    return flask.render_template('select.html', form=form, renderer='bootstrap')

@frontend.route('/scripts/<filename>')
def get_script(filename):
    return flask.send_from_directory('static/scripts', filename)

@frontend.route('/images/<filename>')
def get_image(filename):
    return flask.send_from_directory('static/images', filename)

@frontend.route('/stylesheets/<filename>')
def get_stylesheets(filename):
    print ("stylesheet "+filename)
    return flask.send_from_directory('static/stylesheets', filename)

