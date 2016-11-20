
import flask
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_nav import Nav

import os

from frontend import frontend

from read_courses import CourseCache

if __name__ == "__main__":
    app = Flask (__name__)

    CourseCache.setup()
    CourseCache.example_query('COM', '21700')

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    Bootstrap (app)

    app.register_blueprint(frontend)

    AppConfig (app)

    Nav (app)

    port = os.getenv ("VCAP_APP_PORT", default=8000)
    app.run(host="0.0.0.0", port=int(port))

