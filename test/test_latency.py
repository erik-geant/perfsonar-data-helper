import json
import logging
import os
import responses
from jsonschema import validate
from perfsonar_data_helper import latency

logging.basicConfig(level=logging.DEBUG)

DELAY_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "array",
    "minItems": 1,
    "minimum": 0.0,
    "items": {"type": "number"},
}


@responses.activate
def test_latency_delays_http(client, mocked_latency_test_data):

    rv = client.get(
        "/latency/%s/%s" % (
            mocked_latency_test_data["source"],
            mocked_latency_test_data["destination"]),
        # headers=api_request_headers
    )
    assert rv.status_code == 200
    validate(json.loads(rv.data.decode("utf-8")), DELAY_RESPONSE_SCHEMA)
