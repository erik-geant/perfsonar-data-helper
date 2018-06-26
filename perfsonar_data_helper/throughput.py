from perfsonar_data_helper.pscheduler import client

THROUGHPUT_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "array",
#    "minItems": 1,
    "items": {
        "type": "object",
        "properties": {
            "start": {"type": "number", "minimum": 0.0},
            "end": {"type": "number", "minimum": 0.0},
            "bytes": {"type": "integer", "minimum": 0},
        },
        "required": ["start", "end", "bytes"]
    }
}


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
