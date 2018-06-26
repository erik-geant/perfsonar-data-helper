import json
import logging
import os
import responses
from jsonschema import validate
from perfsonar_data_helper import throughput

logging.basicConfig(level=logging.DEBUG)

THROUGHPUT_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "object",
        "properties": {
            "start": {"type": "number", "minimum": 0.0},
            "end": {"type": "number", "minimum": 0.0},
            "bytes": {"type": "integer", "minimum": 0},
        },
        "required": ["start", "end", "bytes"]
    }
}


@responses.activate
def test_throughput_http(client, mocked_throughput_test_data):

    rv = client.get(
        "/throughput/%s/%s" % (
            mocked_throughput_test_data["source"],
            mocked_throughput_test_data["destination"]),
        # headers=api_request_headers
    )
    assert rv.status_code == 200
    validate(json.loads(rv.data.decode("utf-8")), THROUGHPUT_RESPONSE_SCHEMA)
