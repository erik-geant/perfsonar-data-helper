import os
from flask import Blueprint, current_app, send_from_directory


examples = Blueprint("sample-client-routes", __name__)

sample_base_path = os.path.join(
        os.path.dirname(__file__),
        "client-samples")


@examples.route("/sample/<path:path>")
def send_sample(path):
    return send_from_directory(sample_base_path, path)

