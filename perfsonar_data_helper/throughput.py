import json
import logging

from perfsonar_data_helper.pscheduler import client


def get_raw(source, destination, polling_interval):

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

    task_url = client.create_task(source, test_data)
    task_result = client.get_task_result(
        task_url,
        polling_interval)

    if "result" in task_result:
        return task_result["result"]["intervals"]
    elif "result-merged" in task_result:
        return task_result["result-merged"]["intervals"]
    else:
        assert False, "can't find result key in rsp" + str(task_result.keys())


def get_throughput(source, destination, polling_interval):
    def _rspelem(x):
        return {
            "start": x["summary"]["start"],
            "end": x["summary"]["end"],
            "bytes": x["summary"]["throughput-bytes"]
        }
    return [_rspelem(x) for x in get_raw(source, destination, polling_interval)]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    SOURCE = "psmall-b-3.basnet.by"
    DESTINATION = "psmall-b-2.basnet.by"
    result = get_raw(
        source=SOURCE,
        destination=DESTINATION,
        polling_interval=5)
    logging.debug(result)
