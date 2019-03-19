import json

from jsonschema import validate
import pytest
import responses

from perfsonar_data_helper.long_polling import STATUS_RESPONSE_SCHEMA
from perfsonar_data_helper.latency import LATENCY_RESPONSE_SCHEMA
from perfsonar_data_helper.throughput import THROUGHPUT_RESPONSE_SCHEMA

test_data = [
    # bad destination type
    dict(type="aaa", params=dict(source="sfsfda", destination=1)),
    # bad source type
    dict(type="aaa", params=dict(source=234, destination="aaa")),
    # bad 'type' type
    dict(type=123, params=dict(source="sfsfda", destination="aaa")),
    # missing type
    {"params": dict(source="sfsfda", destination="aaa")},
    # missing source
    dict(type="sfsfda", params=dict(destination="aaa")),
    # missing destination
    dict(type="aaa", params=dict(source="sfsfda")),
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


def _poll(client, test_data):
    rv = client.post(
        "/pscheduler/measurement",
        data=json.dumps(test_data),
        headers={
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
            assert "message" in response_payload
            continue

        assert "data" in response_payload
        return response_payload["data"]

    assert False, "too polling iterations"


@responses.activate
def test_latency_polling_happy_flow(client, mocked_latency_test_data):
    test_data = dict(
        type="latency",
        params=dict(
            source=mocked_latency_test_data["source"],
            destination=mocked_latency_test_data["destination"],
            duration="1",
            interval="1",
            tos="1",
            protocol="udp",
            address_type="ipv6",
            tcp_window="1",
            udp_buffer="1",
            max_bandwidth="1"))

    test_schema = {"minItems": 1}
    test_schema.update(LATENCY_RESPONSE_SCHEMA)

    latency_measurement_result = _poll(client, test_data)
    validate(latency_measurement_result, test_schema)


@responses.activate
def test_throughput_polling_happy_flow(client, mocked_throughput_test_data):
    test_data = dict(
        type="throughput",
        params=dict(
            source=mocked_throughput_test_data["source"],
            destination=mocked_throughput_test_data["destination"],
            wait="1",
            timeout="1",
            padding="1",
            delay="1",
            dscp="1",
            bucket="1"))

    test_schema = {"minItems": 1}
    test_schema.update(THROUGHPUT_RESPONSE_SCHEMA)

    throughput_measurement_result = _poll(client, test_data)
    validate(throughput_measurement_result, test_schema)
