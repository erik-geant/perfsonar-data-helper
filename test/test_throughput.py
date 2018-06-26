import json

import responses
from jsonschema import validate

from perfsonar_data_helper.throughput import THROUGHPUT_RESPONSE_SCHEMA


@responses.activate
def test_throughput_http(client, mocked_throughput_test_data):

    rv = client.get(
        "/throughput/%s/%s" % (
            mocked_throughput_test_data["source"],
            mocked_throughput_test_data["destination"]),
        # headers=api_request_headers
    )
    assert rv.status_code == 200

    test_schema = {"minItems": 1}
    test_schema.update(THROUGHPUT_RESPONSE_SCHEMA)
    validate(json.loads(rv.data.decode("utf-8")), test_schema)
