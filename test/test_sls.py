import logging
import os
import tempfile
import responses
from jsonschema import validate
from perfsonar_data_helper import sls

logging.basicConfig(level=logging.DEBUG)

MP_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "array",
    "minItems": 1,
    "items": {"type": "string"},
}

BOOTSTRAP_URL = "http://ps-west.es.net:8096/lookup/activehosts.json"

# test data
# data files are in the test/sls directory
RESPONSE_DATA = {
    BOOTSTRAP_URL: 'activehosts.json',
    'http://ps-west.es.net:8090/lookup/records': 'ps-west.es.net.json',
    'http://ps-east.es.net:8090/lookup/records': 'ps-east.es.net.json',
    'http://monipe-ls.rnp.br:8090/lookup/records': 'monipe-ls.rnp.br.json',
    'http://ps-sls.sanren.ac.za:8090/lookup/records': 'ps-sls.sanren.ac.za.json',
    'http://nsw-brwy-sls1.aarnet.net.au:8090/lookup/records': 'nsw-brwy-sls1.aarnet.net.au.json'
}


def mock_sls_responses():

    data_path = os.path.join(os.path.dirname(__file__), "sls")
    for url, filename in RESPONSE_DATA.items():

        with open(os.path.join(data_path, filename)) as f:
            body = f.read()

        responses.add(
            responses.GET,
            url,
            body=body,
            content_type="application/json",
            match_querystring=False)

        responses.add(
            responses.GET,
            url + "/",
            body=body,
            content_type="application/json",
            match_querystring=False)


def get_settings(dirname):
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
    settings["SLS_BOOTSTRAP_URL"] = BOOTSTRAP_URL
    return settings


@responses.activate
def test_sls_mps():

    mock_sls_responses()
 
    with tempfile.TemporaryDirectory() as tmpdir:

        settings = get_settings(tmpdir)

        sls.update_cached_mps(
            settings["SLS_BOOTSTRAP_URL"],
            settings["SLS_CACHE_FILENAME"])

        mps = sls.load_mps("owping", settings["SLS_CACHE_FILENAME"])
        validate(list(mps), MP_RESPONSE_SCHEMA)


if __name__ == "__main__":
    # this is only for profiling
    test_sls_mps()
