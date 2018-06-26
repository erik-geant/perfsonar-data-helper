import json
import logging

from jsonschema import validate
import pytest
import responses

STATUS_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "enum": ["status", "complete"]
        },
        "message": {
            "type": "string",
            "enum": ["scheduled", "pending", "on-deck", "running"]
        },
        "time": {
            "type": "string",
            "format": "date-time"
        },
        "data": {}
    },
    "required": ["type", "time"]
}

logging.basicConfig(level=logging.DEBUG)
test_data = [
    # bad destination type
    dict(type="aaa", source="sfsfda", destination=1),
    # bad source type
    dict(type="aaa", source=234, destination="aaa"),
    # bad 'type' type
    dict(type=123, source="sfsfda", destination="aaa"),
    # missing type
    dict(source="sfsfda", destination="aaa"),
    # missing type
    dict(source="sfsfda", destination="aaa"),
    # missing source
    dict(type="sfsfda", destination="aaa"),
    # missing source
    dict(source="sfsfda", type="aaa"),
]


@pytest.mark.parametrize("payload", test_data)
def test_bad_request_payload(payload, client):
    rv = client.post(
        "/pscheduler/measurement",
        data=json.dumps(payload),
        headers={'content-type': 'application/json'}
    )
    assert rv.status_code == 400


def test_bad_request_content_type(client):
    rv = client.post(
        "/pscheduler/measurement",
        data=json.dumps(dict(type="aaa", source="sfsfda", destination="xyz")),
        headers={'content-type': 'test/html'}
    )
    assert rv.status_code == 415


@responses.activate
def test_latency_happy_flow(client, mocked_latency_test_data):
    rv = client.post(
        "/pscheduler/measurement",
        data=json.dumps({
            "type": "latency",
            "source": mocked_latency_test_data["source"],
            "destination": mocked_latency_test_data["destination"]
        }),
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    assert rv.status_code == 200
    response_payload = json.loads(rv.data.decode("utf-8"))
    validate(response_payload, STATUS_RESPONSE_SCHEMA)
    assert response_payload["type"] == "status"
    assert "message" in response_payload \
           and response_payload["message"] == "scheduled"

    for _ in range(20):  # test data ends in fewer than 20 iterations
        rv = client.get("/pscheduler/status")
        assert rv.status_code == 200
        response_payload = json.loads(rv.data.decode("utf-8"))
        validate(response_payload, STATUS_RESPONSE_SCHEMA)

        if response_payload["type"] != "complete":
            assert "message" in response_payload;
            continue

        break

    assert False, "too many test iterations"
