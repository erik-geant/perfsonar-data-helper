import logging
import time

from flask import Blueprint, current_app, jsonify, Response

from perfsonar_data_helper import latency
from perfsonar_data_helper import throughput
from perfsonar_data_helper import sls
from perfsonar_data_helper.pscheduler import client as pscheduler_client


api = Blueprint("simple-routes", __name__)


class APIError(Exception):
    status_code = 415

    def __init__(self, message, status_code=None):
        super().__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


@api.errorhandler(APIError)
def handle_api_error(error):
    return Response(response=error.message, status=error.status_code)


@api.errorhandler(pscheduler_client.PSchedulerError)
def handle_pscheduler_error(error):
    return Response(response=error.message, status=error.status_code)


def _run_measurement(mp, test_data):
    logging.debug("creating task, mp: %r, test data: %r" % (mp, test_data))
    task_url = pscheduler_client.create_task(mp, test_data)
    while True:
        state, result = pscheduler_client.get_task_status(task_url)
        logging.debug("task state: %r" % state)

        if result:
            logging.debug("task complete")
            return result

        if state not in ["pending", "on-deck", "running"]:
            logging.error("unknown state: %r ... ending measurement")
            raise APIError("received an unknown task state: %r" % state)

        time.sleep(current_app.config[
                       "PSCHEDULER_TASK_POLLING_INTERVAL_SECONDS"])


@api.route("/latency/<string:source>/<string:destination>")
def latency_measurement(source, destination):
    test_data = latency.make_test_data(
        {"source": source, "destination": destination})
    result = _run_measurement(source, test_data)
    return jsonify(latency.format_result(result))


@api.route("/throughput/<string:source>/<string:destination>")
def throughput_measurement(source, destination):
    test_data = throughput.make_test_data(
        {"source": source, "destination": destination})
    result = _run_measurement(source, test_data)
    return jsonify(throughput.format_result(result))


@api.route("/mplist/<string:tool>")
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
