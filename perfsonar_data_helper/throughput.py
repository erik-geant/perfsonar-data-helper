import json
import logging
import time

import requests


def _get_task_result(task_url, delay_seconds):
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
        if delay_seconds > 0:
            time.sleep(delay_seconds)


def get_raw(source, destination, delay_seconds):

    mp_hostname = source

    test_spec = {
        "source": source, 
        "dest": destination,
        "duration": "PT30S",
        "interval": "PT6S",
#        "output-raw": True,
        "schema": 1
    }

    test_data = {
        "schema": 1,
        "schedule": {"slip": "PT1M"},
        "test": {
            "spec": test_spec,
            "type": "throughput"
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
    task_result = _get_task_result(
        rsp.text.rstrip().replace('"', ''),
        delay_seconds)
    return task_result
    if "result" in task_result:
        return task_result["result"]["raw-packets"]
    elif "result-merged" in task_result:
        return task_result["result-merged"]["raw-packets"]
    else:
        assert False, "can't find result key in rsp" + str(task_result.keys())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    SOURCE = "psmall-b-3.basnet.by"
    DESTINATION = "psmall-b-2.basnet.by"
    result = get_raw(source=SOURCE, destination=DESTINATION, delay_seconds=5)
    logging.debug(result)
