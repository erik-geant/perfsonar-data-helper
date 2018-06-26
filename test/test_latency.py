import json

import responses
from jsonschema import validate

from perfsonar_data_helper.latency import LATENCY_RESPONSE_SCHEMA


@responses.activate
def test_latency_delays_http(client, mocked_latency_test_data):

    rv = client.get(
        "/latency/%s/%s" % (
            mocked_latency_test_data["source"],
            mocked_latency_test_data["destination"]),
        # headers=api_request_headers
    )
    assert rv.status_code == 200
    validate(json.loads(rv.data.decode("utf-8")), LATENCY_RESPONSE_SCHEMA)
