"""
factory for use with tests
"""
import logging
import os
from flask import Flask
from flask_cors import CORS
import sls

def create_app():
    """
    overrides settings from the filename defined in env var
    SETTINGS_FILENAME
    :return: a new flask app instance
    """
    app = Flask(__name__)
    CORS(app)

    app.config.from_object("pscheduler_proxy.default_settings")
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

    return app
