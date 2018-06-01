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

SOURCE = "perfsonar-nas.asnet.am"
DESTINATION = "perfsonar-probe.ripe.net"

RESPONSE_DATA = [
    {
        "url": "https://perfsonar-nas.asnet.am/pscheduler/tasks",
        "method": responses.POST,
        "data_filenames": ["task-init-response.txt"]
    },
    {
        "url": "https://perfsonar-nas.asnet.am/pscheduler/tasks/6f86acbf-ee3b-497d-857b-6c7975f1ac00/runs/first",
        "method": responses.GET,
        "data_filenames": [
            "task-0.json",
            "task-1.json",
            "task-2.json",
            "task-3.json",
            "task-4.json",
            "task-5.json",
            "task-6.json",
            "task-7.json",
            "task-8.json",
            "task-9.json",
            "task-10.json",
            "task-11.json",
            "task-12.json",
            "task-13.json",
            "task-14.json"
        ]
    }
]


def mock_latency_responses():

    data_path = os.path.join(os.path.dirname(__file__), "latency")
    for rsp in RESPONSE_DATA:

        for fn in rsp["data_filenames"]:
            with open(os.path.join(data_path, fn)) as f:
                body = f.read()

            responses.add(
                rsp["method"],
                rsp["url"],
                body=body,
                match_querystring=False)


@responses.activate
def test_latency_delays():
    mock_latency_responses()
    delays = latency.get_delays(SOURCE, DESTINATION, polling_interval=-1)
    validate(delays, DELAY_RESPONSE_SCHEMA)


@responses.activate
def test_latency_delays_http(client):
    mock_latency_responses()
    rv = client.get(
        "/latency/%s/%s" % (SOURCE, DESTINATION),
        # headers=api_request_headers
    )
    assert rv.status_code == 200
    validate(json.loads(rv.data.decode("utf-8")), DELAY_RESPONSE_SCHEMA)
