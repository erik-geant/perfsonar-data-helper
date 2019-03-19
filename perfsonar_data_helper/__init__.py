"""
automatically invoved app factory
"""
import logging
import os
from flask import Flask
from flask_cors import CORS
# from flask_session import Session

# SECRET_KEY = '123456789012345678901234'
# SESSION_TYPE = 'filesystem'


def create_app():
    """
    overrides settings from the filename defined in env var
    SETTINGS_FILENAME
    :return: a new flask app instance
    """

    app = Flask(__name__)
    app.secret_key = "super secret session key"

    CORS(app)

    from perfsonar_data_helper import sls
    from perfsonar_data_helper import simple
    from perfsonar_data_helper import long_polling
    from perfsonar_data_helper import json_proxy
    from perfsonar_data_helper import example_routes

    app.register_blueprint(simple.api)
    app.register_blueprint(long_polling.api)
    app.register_blueprint(example_routes.examples)
    app.register_blueprint(json_proxy.api, url_prefix='/json-proxy')

    # SESSION_TYPE = "filesystem"

    app.config.from_object("perfsonar_data_helper.default_settings")
    if "SETTINGS_FILENAME" in os.environ:
        app.config.from_envvar("SETTINGS_FILENAME")
    else:
        logging.debug(
            "SETTINGS_FILENAME environment variable"
            " not set, using default config")

    # app.config["SESSION_TYPE"] = "filesystem"

    logging.debug(app.config)

    # Session(app)
    # sess.init_app(app)

    if app.config["STARTUP_REFRESH_SLS_CACHE"]:
        sls.update_cached_mps(
            bootstrap_url=app.config["SLS_BOOTSTRAP_URL"],
            cache_filename=app.config["SLS_CACHE_FILENAME"])

    return app
