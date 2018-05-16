import json
import logging
import time

import requests


def _get_task_result(task_url):
    logging.debug("task result url: %s" % (task_url + "/runs/first"))

    while True:
        rsp = requests.get(
            task_url + "/runs/first",
            verify=False,
            headers={"Accept": "application/json"})

        assert rsp.status_code == 200
        result = rsp.json()
        logging.debug("task state: %s" % result["state"])
        if result["state"] == "finished":
            return result
        time.sleep(5)


def get_raw(source, destination):

    mp_hostname = source

    test_spec = {
        "source": SOURCE, 
        "dest": DESTINATION,
#        "packet-count": 10,
        "output-raw": True,
        "schema": 1
    }

    test_data = {
        "schema": 1,
        "schedule": {"slip": "PT5M"},
        "test": {
            "spec": test_spec,
            "type": "latency"
        }
    }

    mp_url = 'https://%s/pscheduler/tasks' % mp_hostname
    logging.debug("mp url: '%s'" % mp_url)

    logging.debug("request data: %s" % json.dumps(test_data))

    rsp = requests.post(
        mp_url,
        verify=False,
        json=test_data)
    
    assert rsp.status_code == 200

    logging.debug("task created: %s" % rsp.text)
    task_result = _get_task_result(rsp.text.rstrip().replace('"', ''))
    return task_result["result-merged"]["raw-packets"]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    SOURCE = "perfsonar-nas.asnet.am"
    DESTINATION = "perfsonar-probe.ripe.net"
    result = get_raw(source=SOURCE, destination=DESTINATION)
    logging.debug(result)
