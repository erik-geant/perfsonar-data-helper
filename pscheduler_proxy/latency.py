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
        assert result["state"] in {"pending", "on-deck", "running", "finished" }
        if result["state"] == "finished":
#            logging.debug("task result: " + json.dumps(result))
            return result
        time.sleep(5)


def get_raw(source, destination):

    mp_hostname = source

    test_spec = {
        "source": source, 
        "dest": destination,
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
    if "result" in task_result:
        return task_result["result"]["raw-packets"]
    elif "result-merged" in task_result:
        return task_result["result-merged"]["raw-packets"]
    else:
        assert False, "can't find result key in rsp" + str(task_result.keys())


def get_delays_debug(source, destination):
    import os
    filename = os.path.join(
        os.path.dirname(__file__),
        "..",
        "test",
        "owamp-deltas.json")
    with open(filename) as f:
        return json.loads(f.read())


def get_delays(source, destination):
    exp = float(0x100000000)
    def _delta(x):
        rcv = float(x["dst-ts"])/exp
        snd = float(x["src-ts"])/exp
        return rcv-snd
    return [_delta(x) for x in get_raw(source, destination)]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    SOURCE = "perfsonar-nas.asnet.am"
    DESTINATION = "perfsonar-probe.ripe.net"
    result = get_raw(source=SOURCE, destination=DESTINATION)
    logging.debug(result)
