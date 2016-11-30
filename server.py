
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

from read_courses import CourseCache


def query_test(dept, number):
    CourseCache.wait_for_access()
    meetings = CourseCache.query(dept, number)
    logging.info('{} Meetings found for {}{}'
                 .format(len(meetings), dept, number))
    for meeting in meetings:
        logging.debug(meeting)


app = Flask(__name__)
nav = Nav(app)


@nav.navigation()
def navigate():
    return flask_nav.elements.Navbar(u"Schedülr",
            flask_nav.elements.View("Home", 'frontend.get_index'),
            flask_nav.elements.View(u"Schedüle", 'frontend.make_schedule'),
            )


def flask_startup():
    # app.debug = True
    # app.use_reloader = False
    app.secret_key = 'super secret key'
    app.config.from_object('config')

    Bootstrap(app)

    app.register_blueprint(frontend)

    AppConfig(app)

    nav.init_app(app)
    nav.renderer(navigate())

    port = os.getenv("VCAP_APP_PORT", default=8000)
    app.run(host="0.0.0.0", port=int(port))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    flask_thread = threading.Thread(target=flask_startup)
    flask_thread.start()

    query_thread = threading.Thread(target=query_test, args=('CS', '35200'))
    query_thread.start()

    cache_setup_thread = threading.Thread(target=CourseCache.setup())
    cache_setup_thread.start()

    query_thread.join()
    cache_setup_thread.join()

    some_lock = threading.Event()
    some_lock.wait()
