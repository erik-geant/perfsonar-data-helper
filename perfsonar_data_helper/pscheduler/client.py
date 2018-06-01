import logging
import time
import requests


def get_task_result(task_url, polling_interval):
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
        if polling_interval > 0:
            time.sleep(polling_interval)


def create_task(mp_hostname, task_data):
    mp_url = 'https://%s/pscheduler/tasks' % mp_hostname
    logging.debug("mp url: '%s'" % mp_url)

    logging.debug("request data: %r" % task_data)

    rsp = requests.post(
        mp_url,
        verify=False,
        json=task_data)

    assert rsp.status_code == 200

    logging.debug("task created: %s" % rsp.text)

    return rsp.text.rstrip().replace('"', '')


