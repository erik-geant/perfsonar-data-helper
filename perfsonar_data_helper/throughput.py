from perfsonar_data_helper.pscheduler import client


def format_result(task_result):
    if "intervals" not in task_result:
        raise client.PSchedulerError(
            "can't find intervals in rsp" + str(task_result.keys()))

    def _rspelem(x):
        return {
            "start": x["summary"]["start"],
            "end": x["summary"]["end"],
            "bytes": x["summary"]["throughput-bytes"]
        }
    return [_rspelem(x) for x in task_result["intervals"]]


def make_test_data(source, destination):

    test_spec = {
        "source": source, 
        "dest": destination,
        "duration": "PT30S",
        "interval": "PT6S",
        # "output-raw": True,
        "schema": 1
    }

    return {
        "schema": 1,
        "schedule": {"slip": "PT1M"},
        "test": {
            "spec": test_spec,
            "type": "throughput"
        }
    }
