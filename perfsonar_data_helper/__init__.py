"""
automatically invoved app factory
"""
import logging
import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app():
    """
    overrides settings from the filename defined in env var
    SETTINGS_FILENAME
    :return: a new flask app instance
    """

    from perfsonar_data_helper import sls
    from perfsonar_data_helper import routes

    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(routes.server)

    app.config.from_object("perfsonar_data_helper.default_settings")
    if "SETTINGS_FILENAME" in os.environ:
        app.config.from_envvar("SETTINGS_FILENAME")
    else:
        logging.debug(
            "SETTINGS_FILENAME environment variable"
            " not set, using default config")

    logging.debug(app.config)

    if app.config["STARTUP_REFRESH_SLS_CACHE"]:
        sls.update_cached_mps(
            bootstrap_url=app.config["SLS_BOOTSTRAP_URL"],
            cache_filename=app.config["SLS_CACHE_FILENAME"])

    socketio.init_app(app)

    return app
