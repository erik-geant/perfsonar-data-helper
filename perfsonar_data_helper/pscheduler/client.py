import logging
import time
import requests


logger = logging.getLogger(__name__)


class PSchedulerError(Exception):
    status_code = 503

    def __init__(self, message):
        self.message = message


def get_task_status(task_url):
    rsp = requests.get(
        task_url + "/runs/first",
        verify=False,
        headers={"Accept": "application/json"})

    if rsp.status_code != 200:
        raise PSchedulerError(
            "error retrieving task status, code: %d" % rsp.status_code)

    task_status = rsp.json()
    logger.debug("task state: %s" % task_status["state"])
    if task_status["state"] not in {
            "pending", "on-deck", "running", "finished"}:
        logger.warning("unusual task state: " + task_status["state"])

    result_data = None
    if task_status["state"] == "finished":
        if "result" in task_status:
            result_data = task_status["result"]
        elif "result-merged" in task_status:
            result_data = task_status["result-merged"]
        else:
            raise PSchedulerError(
                "can't find result key in response: "
                + str(task_status.keys()))

    return task_status["state"], result_data


def get_task_result(task_url, polling_interval):
    logger.debug("task result url: %s" % (task_url + "/runs/first"))
    while True:
        _, data = get_task_status(task_url)
        if data:
            # logger.debug("task result: " + json.dumps(status))
            return data
        if polling_interval > 0:
            time.sleep(polling_interval)


def create_task(mp_hostname, task_data):
    mp_url = 'https://%s/pscheduler/tasks' % mp_hostname
    logger.debug("mp url: '%s'" % mp_url)
    logger.debug("request data: %r" % task_data)
    rsp = requests.post(
        mp_url,
        verify=False,
        json=task_data)

    if rsp.status_code != 200:
        raise PSchedulerError(
            "error submitting task, code: %d" % rsp.status_code)

    logger.debug("task created: %s" % rsp.text)
    return rsp.text.rstrip().replace('"', '')
