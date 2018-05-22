from flask import Blueprint, current_app, jsonify

from pscheduler_proxy import latency
from pscheduler_proxy import sls

server = Blueprint("measurement-routes", __name__)


@server.route("/latency/<string:source>/<string:destination>")
def latency(source, destination):
#    return jsonify(latency.get_raw(source=source, destination=destination))
    return jsonify(latency.get_delays(source=source, destination=destination))
#    return jsonify(latency.get_delays_debug(source=source, destination=destination))


@server.route("/mplist/<string:tool>")
def mplist(tool):
    if tool == "refresh":
        sls.update_cached_mps(
            current_app.config["SLS_BOOTSTRAP_URL"],
            current_app.config["SLS_CACHE_FILENAME"])
        result = {"result": True}
    else:
        result = sls.load_mps(tool, current_app.config["SLS_CACHE_FILENAME"])
        result = list(result)

    return jsonify(result)

