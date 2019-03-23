import logging
import time

from flask import Blueprint, request, Response, current_app, jsonify
import jsonschema
import requests

from perfsonar_data_helper.pscheduler import client

api = Blueprint("json-proxy", __name__)

logger = logging.getLogger(__name__)


@api.errorhandler(client.PSchedulerError)
def handle_pscheduler_error(error):
    return Response(
        response=error.message,
        status=error.status_code)


@api.route("/connection-test", methods=['GET', 'POST'])
def connection_test():
    return 'test'


@api.route("/run-measurement", methods=['POST'])
def run_measurement():
    schema = {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'type': 'object',
        'properties': {
            'mp-hostname': {'type': 'string'},
            'task-data': {'type': 'object'}
        },
        'required': ['mp-hostname', 'task-data'],
        'additionalProperties': False
    }

    request_payload = request.get_json()
    jsonschema.validate(request_payload, schema)

    task_url = client.create_task(
        request_payload['mp-hostname'],
        request_payload['task-data'])

    while True:
        state, result = client.get_task_status(task_url)
        logger.debug("task state: %r" % state)

        if result:
            logger.debug("task complete")
            return jsonify(result)

        if state not in ["pending", "on-deck", "running"]:
            logger.error(
                "unknown state: %r ... ending measurement")
            raise client.PSchedulerError(
                "received an unknown task state: %r" % state)

        time.sleep(current_app.config[
            "PSCHEDULER_TASK_POLLING_INTERVAL_SECONDS"])


@api.route("/post", methods=['POST'])
def post():

    schema = {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'type': 'object',
        'properties': {
            'url': {'type': 'string'},
            'parameters': {'type': 'object'}
        },
        'required': ['url'],
        'additionalProperties': False
    }

    request_payload = request.get_json()
    jsonschema.validate(request_payload, schema)

    logger.debug('url: %r' % request_payload['url'])
    if 'parameters' in request_payload:
        rsp = requests.post(
            request_payload['url'],
            verify=False,
            json=request_payload['parameters'])
    else:
        rsp = requests.post(
            request_payload['url'],
            verify=False)

    return Response(
        response=rsp.text,
        status=rsp.status_code,
        headers=dict(rsp.headers)
    )


@api.route("/get", methods=['POST'])
def get():

    schema = {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'type': 'object',
        'properties': {
            'url': {'type': 'string'}
        },
        'required': ['url'],
        'additionalProperties': False
    }

    request_payload = request.get_json()
    jsonschema.validate(request_payload, schema)

    logger.debug('url: %r' % request_payload['url'])
    rsp = requests.get(
        request_payload['url'],
        verify=False)

    return Response(
        response=rsp.text,
        status=rsp.status_code,
        headers=dict(rsp.headers)
    )
