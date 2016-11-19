
import flask
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_nav import Nav

import os

from frontend import frontend

if __name__ == "__main__":
    app = Flask (__name__)

    app.register_blueprint(frontend)

    AppConfig (app)

    Bootstrap (app)

    Nav (app)

    port = os.getenv ("VCAP_APP_PORT", default=8000)
    app.run(host="0.0.0.0", port=int(port))

