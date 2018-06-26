import datetime
import json
import logging
import time

from flask import Blueprint, current_app, jsonify, session, request, Response
from jsonschema import validate, ValidationError

from perfsonar_data_helper import latency
from perfsonar_data_helper import throughput
from perfsonar_data_helper.pscheduler import client as pscheduler_client

api = Blueprint("long-polling-routes", __name__)

MEASUREMENT_REQUEST_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "object",
    "properties": {
        "type": {"type": "string"},
        "source": {"type": "string"},
        "destination": {"type": "string"}
    },
    "required": ["type", "source", "destination"]
}


class APIError(Exception):
    status_code = 415

    def __init__(self, message, status_code=None):
        super().__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


def _formatted_time():
    return datetime \
        .datetime \
        .utcfromtimestamp(time.time()) \
        .strftime('%Y-%m-%dT%H:%M:%SZ')


def status_response(message):
    return {
        "type": "status",
        "message": message,
        "time": _formatted_time()
    }


def result_response(data):
    return {
        "type": "complete",
        "data": data,
        "time": _formatted_time()
    }


@api.errorhandler(APIError)
def handle_api_error(error):
    return Response(response=error.message, status=error.status_code)


@api.errorhandler(pscheduler_client.PSchedulerError)
def handle_pscheduler_error(error):
    return Response(response=error.message, status=error.status_code)


@api.errorhandler(ValidationError)
def handle_json_validation_error(error):
    return Response(response=error.message, status=400)


@api.route("/pscheduler/measurement", methods=['POST'])
def pscheduler_measurement():

    payload = request.get_json()
    if payload is None:
        raise APIError("expected json payload")

    validate(payload, MEASUREMENT_REQUEST_SCHEMA)

    if not isinstance(payload, dict) \
        or not {"type", "source", "destination"}.issubset(set(payload.keys())):
        raise APIError("invalid payload format")

    if payload["type"] == "latency":
        test_data = latency.make_test_data(
            payload["source"],
            payload["destination"])
    elif payload["type"] == "throughput":
        test_data = throughput.make_test_data(
            payload["source"],
            payload["destination"])
    else:
        raise APIError("bad measurement type")

    logging.debug("creating task, test data: %r" % test_data)

    task_url = pscheduler_client.create_task(
        payload["source"],
        test_data)

    session["task_url"] = task_url
    session["type"] = payload["type"]

    return jsonify(status_response("scheduled"))


@api.route("/pscheduler/status", methods=['GET', 'POST'])
def pscheduler_status():
    if not {"task_url", "type"}.issubset(set(session.keys())):
        raise APIError("session not initialized", status_code=400)

    assert session["type"] in {"latency", "throughput"}  # sanity

    logging.debug("calling get_task_status, task_url: %r" % session["task_url"])
    state, result = pscheduler_client.get_task_status(session["task_url"])
    logging.debug("task state: %r" % state)

    if result is None:
        return jsonify(status_response(state))

    if session["type"] == "latency":
        data = latency.format_result(result)
    elif session["type"] == "throughput":
        data = throughput.format_result(result)
    else:
        assert False  # sanity (should have already been checked)

    logging.debug("task complete")

    return jsonify(result_response(data))
