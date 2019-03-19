import logging

from flask import Blueprint, request, Response
import jsonschema
import requests

api = Blueprint("json-proxy", __name__)


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

    logging.debug('url: %r' % request_payload['url'])
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
