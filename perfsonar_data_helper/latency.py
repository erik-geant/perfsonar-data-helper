from perfsonar_data_helper.pscheduler import client

LATENCY_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "array",
#    "minItems": 1,
    "minimum": 0.0,
    "items": {"type": "number"},
}


def format_result(task_result):
    if "raw-packets" not in task_result:
        raise client.PSchedulerError(
            "can't find raw-packets in rsp" + str(task_result.keys()))

    # reformat the result as a list of delays, in seconds
    exp = float(0x100000000)

    def _delta(x):
        rcv = float(x["dst-ts"])/exp
        snd = float(x["src-ts"])/exp
        return rcv-snd

    return [_delta(x) for x in task_result["raw-packets"]]


def make_test_data(source, destination):
    test_spec = {
        "source": source,
        "dest": destination,
        #        "packet-count": 10,
        "output-raw": True,
        "schema": 1
    }

    return {
        "schema": 1,
        "schedule": {"slip": "PT5M"},
        "test": {
            "spec": test_spec,
            "type": "latency"
        }
    }
