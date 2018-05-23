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

RESPONSE_DATA = {
    "https://perfsonar-nas.asnet.am/pscheduler/tasks": [
        "task-init-response.txt"
    ],
    "https://perfsonar-nas.asnet.am/pscheduler/tasks/6f86acbf-ee3b-497d-857b-6c7975f1ac00/runs/first": [
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


def mock_latency_responses():

    data_path = os.path.join(os.path.dirname(__file__), "latency")
    for url, filenames in RESPONSE_DATA.items():

        for fn in filenames:
            with open(os.path.join(data_path, fn)) as f:
                body = f.read()

            responses.add(
                responses.GET,
                url,
                body=body,
                match_querystring=False)

            responses.add(
                responses.POST,
                url,
                body=body,
                match_querystring=False)


@responses.activate
def test_latency_delays():
    mock_latency_responses()
    delays = latency.get_delays(SOURCE, DESTINATION, delay_seconds=-1)
    validate(delays, DELAY_RESPONSE_SCHEMA)
