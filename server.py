
# coding=utf-8

import flask
from flask import Flask
from flask_bootstrap import Bootstrap
import flask_bootstrap
from flask_appconfig import AppConfig
from flask_nav import Nav
import flask_nav.elements

import os

from frontend import frontend

from read_courses import CourseCache

app = Flask (__name__)
nav = Nav (app)

@nav.navigation()
def navigate():
    return flask_nav.elements.Navbar(u"Schedülr",
            flask_nav.elements.View("Home",'frontend.get_index'),
            flask_nav.elements.View(u"Schedüle",'frontend.make_schedule'),
            )

if __name__ == "__main__":

    CourseCache.setup()
    CourseCache.example_query('COM', '21700')

    app.debug = True
    app.secret_key = 'super secret key'
    app.config.from_object('config')
    #app.config['SESSION_TYPE'] = 'filesystem'

    Bootstrap (app)

    app.register_blueprint(frontend)

    AppConfig (app)

    nav.init_app(app)
    nav.renderer(navigate())

    port = os.getenv ("VCAP_APP_PORT", default=8000)
    app.run(host="0.0.0.0", port=int(port))

