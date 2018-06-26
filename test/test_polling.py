import json
import logging

import pytest

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
