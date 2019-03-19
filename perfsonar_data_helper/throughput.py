import jsonschema
from perfsonar_data_helper.pscheduler import client


THROUGHPUT_TEST_PARAMS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "object",
    "properties": {
        "source": {"type": "string"},
        "destination": {"type": "string"},
        "duration": {"type": "string"},
        "interval": {"type": "string"},
        "tos": {"type": "string"},
        "protocol": {"type": "string", "enum": ["udp", "tcp"]},
        "address_type": {"type": "string", "enum": ["ipv4", "ipv6"]},
        "tcp_window": {"type": "string"},
        "udp_buffer": {"type": "string"},
        "max_bandwidth": {"type": "string"},
    },
    "required": ["source", "destination"]
}

THROUGHPUT_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "array",
    # "minItems": 1,
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


def make_test_data(test_params):

    jsonschema.validate(test_params, THROUGHPUT_TEST_PARAMS_SCHEMA)

    test_spec = {
        "schema": 1,
        "source": test_params["source"],
        "dest": test_params["destination"],
        "duration": "PT%sS" % test_params.get("duration", "30"),
        "interval": "PT%sS" % test_params.get("interval", "6")
    }

    if "tcp_window" in test_params:
        test_spec["window-size"] = test_params["tcp_window"]

    # if "address_type" in test_params:
    #     if test_params["address_type"] == "ipv4":
    #         test_spec["ipv4_only"] = 1
    #     elif test_params["address_type"] == "ipv6":
    #         test_spec["ipv6_only"] = 1

    # if "protocol" in test_params:
    #     test_spec["protocol"] = test_params["protocol"]

    # if "max_bandwidth" in test_params:
    #     test_spec["bandwidth"] = test_params["max_bandwidth"]

    return {
        "schema": 1,
        "schedule": {"slip": "PT1M"},
        "test": {
            "spec": test_spec,
            "type": "throughput"
        }
    }
