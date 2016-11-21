
import flask
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_nav import Nav

import os
import threading
import logging
from frontend import frontend

from read_courses import CourseCache

def query_test(dept, number):
    CourseCache.wait_for_access()
    print('{} was found for {} {}'.format(CourseCache.query(dept, number), dept, number))

def flask_startup():
    app = Flask (__name__)

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    Bootstrap (app)

    app.register_blueprint(frontend)

    AppConfig (app)

    Nav (app)

    port = os.getenv ("VCAP_APP_PORT", default=8000)
    app.run(host="0.0.0.0", port=int(port))

if __name__ == "__main__":

    flask_thread = threading.Thread(target=flask_startup)
    flask_thread.start()

    query_thread = threading.Thread(target=query_test, args=('CS', '25200'))
    query_thread.start()

    cache_setup_thread = threading.Thread(target=CourseCache.setup())
    cache_setup_thread.start()

    some_lock = threading.Event()
    some_lock.wait()

