import json
import logging
import os
import tempfile
import responses
from jsonschema import validate
import pytest
from perfsonar_data_helper import sls

logging.basicConfig(level=logging.INFO)

MP_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "object",
        "properties": {
            "hostname": {"type": "string"},
            "name": {"type": "string"},
            "domains": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["hostname", "name", "communities"]
    },
}


# def mock_sls_responses():
#
#     data_path = os.path.join(os.path.dirname(__file__), "sls")
#     for url, filename in RESPONSE_DATA.items():
#
#         with open(os.path.join(data_path, filename)) as f:
#             body = f.read()
#
#         responses.add(
#             responses.GET,
#             url,
#             body=body,
#             content_type="application/json",
#             match_querystring=False)
#
#         responses.add(
#             responses.GET,
#             url + "/",
#             body=body,
#             content_type="application/json",
#             match_querystring=False)


def get_settings(dirname, bootstrap_url):
    import perfsonar_data_helper
    default_settings_filename = os.path.join(
        perfsonar_data_helper.__path__[0],
        "default_settings.py")
    with open(default_settings_filename) as f:
        contents = f.read()
    g = {}
    settings = {}
    exec(contents, g, settings)

    settings["SLS_CACHE_FILENAME"] = os.path.join(dirname, "sls-cache.json")
    settings["SLS_BOOTSTRAP_URL"] = bootstrap_url
    return settings


@responses.activate
def test_sls_mps(mocked_sls_test_data):

    # mock_sls_responses()
 
    with tempfile.TemporaryDirectory() as tmpdir:

        settings = get_settings(tmpdir, mocked_sls_test_data["bootstrap_url"])

        sls.update_cached_mps(
            settings["SLS_BOOTSTRAP_URL"],
            settings["SLS_CACHE_FILENAME"])

        mps = sls.load_mps("owping", settings["SLS_CACHE_FILENAME"])
        validate(list(mps), MP_RESPONSE_SCHEMA)


@responses.activate
def test_throughput_http(client, mocked_sls_test_data):
    # mock_sls_responses()
    rv = client.get(
        "/mplist/refresh",
        # headers=api_request_headers
    )
    assert rv.status_code == 200

    rv = client.get(
        "/mplist/owping",
        # headers=api_request_headers
    )

    validate(json.loads(rv.data.decode("utf-8")), MP_RESPONSE_SCHEMA)


test_data = [
    ["http://200.143.240.132/esmond/perfsonar/archive", "200.143.240.132"],
    ["https://200.143.240.132/esmond/perfsonar/archive", "200.143.240.132"],
    ["tcp://mp-pop-sj-remep.perf.pop-sc.rnp.br:861", "mp-pop-sj-remep.perf.pop-sc.rnp.br"],
    ["periboea.kenyon.edu", "periboea.kenyon.edu"],
    ["http://periboea.kenyon.edu/esmond/perfsonar/archive", "periboea.kenyon.edu"],
    ["https://periboea.kenyon.edu/esmond/perfsonar/archive", "periboea.kenyon.edu"],
    ["tcp://[2804:1454:1002:100::27]:4823", "[2804:1454:1002:100::27]"],
    ["tcp://191.36.79.27:4823", "191.36.79.27"],
    ["200.143.233.6", "200.143.233.6"],
    ["tcp://sampaps02.if.usp.br:861", "sampaps02.if.usp.br"],
    ["tcp://[2001:12d0:8120::136]:861", "[2001:12d0:8120::136]"],
    ["http://200.17.30.136/services/MP/BWCTL", "200.17.30.136"],
    ["http://[2001:12d0:8120::136]/services/MP/BWCTL", "[2001:12d0:8120::136]"],
    ["https://200.17.30.136/services/MP/BWCTL", "200.17.30.136"],
    ["https://[2001:12d0:8120::136]/services/MP/BWCTL", "[2001:12d0:8120::136]"],
    ["http://[2804:1f10:8000:801::141]/esmond/perfsonar/archive", "[2804:1f10:8000:801::141]"],
    ["http://152.84.101.141/esmond/perfsonar/archive", "152.84.101.141"],
    ["https://[2804:1f10:8000:801::141]/esmond/perfsonar/archive", "[2804:1f10:8000:801::141]"],
    ["https://152.84.101.141/esmond/perfsonar/archive", "152.84.101.141"],
    ["http://[2a00:139c:5:4102::6]/esmond/perfsonar/archive", "[2a00:139c:5:4102::6]"],
    ["https://[2a00:139c:5:4102::6]/esmond/perfsonar/archive", "[2a00:139c:5:4102::6]"],
    ["https://[2a00:139c:5:4102::6]/pscheduler", "[2a00:139c:5:4102::6]"],
    ["https://[2404:138:143:56::2]:7123", "[2404:138:143:56::2]"],
    ["https://[2404:138:143:52::2]/pscheduler", "[2404:138:143:52::2]"],
    ["tcp://[2001:254:8004:2::2]:861", "[2001:254:8004:2::2]"],
]


@pytest.mark.parametrize("url,expected_hostname", test_data)
def test_hostname_from_url(url, expected_hostname):
    assert sls.hostname_from_url(url) == expected_hostname


if __name__ == "__main__":
    # this is only for profiling
    test_sls_mps()
