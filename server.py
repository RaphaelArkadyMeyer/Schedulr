
# coding=utf-8

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_nav import Nav
import flask_nav.elements

import os
import threading
import logging
from frontend import frontend
from frontend import navigation_header

from read_courses import CourseCache

import config as config


def query_test(dept, number):
    CourseCache.wait_for_access()
    meetings = [CourseCache.query_meeting_times(dept, number)]
    logging.info('{} Meetings found for {}{}'
                 .format(len(meetings), dept, number))
    for meeting in meetings:
        logging.debug(meeting)



def flask_startup():
    app = Flask(__name__)
    nav = Nav(app)

    @nav.navigation()
    def navigate(): return navigation_header()
    nav.navigation(navigate())

    app.secret_key = 'super duper secret key'
    app.config.from_object('config.FlaskConfig')

    Bootstrap(app)

    app.register_blueprint(frontend)

    AppConfig(app)

    nav.init_app(app)
    nav.renderer(navigation_header())

    port = os.getenv("VCAP_APP_PORT", default=8000)

    CourseCache.wait_for_access()
    app.run(host="0.0.0.0", port=int(port))


if __name__ == "__main__":
    logging.basicConfig(level=config.LOGGING_MODE)

    if config.DO_SAMPLE_QUERY:
        query_thread = threading.Thread(target=query_test, args=('CS', '35200'))
        query_thread.start()

    cache_setup_thread = threading.Thread(target=CourseCache.setup)
    cache_setup_thread.start()

    flask_startup()
