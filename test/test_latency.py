import logging
import os
import tempfile
import responses
from perfsonar_data_helper import latency


logging.basicConfig(level=logging.DEBUG)

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


# def get_settings(dirname):
#     import perfsonar_data_helper
#     default_settings_filename = os.path.join(
#         perfsonar_data_helper.__path__[0],
#         "default_settings.py")
#     with open(default_settings_filename) as f:
#         contents = f.read()
#     g = {}
#     settings = {}
#     exec(contents, g, settings)
# 
#     settings["SLS_CACHE_FILENAME"] = os.path.join(dirname, "sls-cache.json")
#     settings["SLS_BOOTSTRAP_URL"] = BOOTSTRAP_URL
#     return settings


@responses.activate
def test_latency_delays():
    mock_latency_responses()
 
    with tempfile.TemporaryDirectory() as tmpdir:

#        settings = get_settings(tmpdir)

        logging.info(latency.get_delays(SOURCE, DESTINATION, delay_seconds=-1))


if __name__ == "__main__":
    # this is only for profiling
    test_latency_delays()
