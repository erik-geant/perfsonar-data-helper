from flask import Blueprint, current_app, jsonify

from perfsonar_data_helper import latency
from perfsonar_data_helper import throughput
from perfsonar_data_helper import sls

server = Blueprint("measurement-routes", __name__)


@server.route("/latency/<string:source>/<string:destination>")
def latency_measurement(source, destination):
    return jsonify(latency.get_delays(
        source=source,
        destination=destination,
        polling_interval=current_app.config["PSCHEDULER_TASK_POLLING_INTERVAL_SECONDS"]))


@server.route("/throughput/<string:source>/<string:destination>")
def throughput_measurement(source, destination):
    return jsonify(throughput.get_throughput(
        source=source,
        destination=destination,
        polling_interval=current_app.config["PSCHEDULER_TASK_POLLING_INTERVAL_SECONDS"]))


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

