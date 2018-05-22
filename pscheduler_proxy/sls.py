import json
import logging
import random
import requests
from requests_futures.sessions import FuturesSession

logging.basicConfig(level=logging.DEBUG)

SLS_BOOTSTRAP_URL = "http://ps-west.es.net:8096/lookup/activehosts.json"
CACHED_SERVICE_LIST_FILENAME = "/tmp/sls-cache.json"


def load_sls_hosts(bootstrap_url):
    rsp = requests.get(
        bootstrap_url,
        headers={"Accept": "application/json"})
    assert rsp.status_code == 200

    return [
        h["locator"] for h in rsp.json()["hosts"]
        if h["status"] == "alive"
    ]

def load_services(bootstrap_url):

    session = FuturesSession(max_workers=10)

    jobs = {url: session.get(
                url,
                headers={"Accept": "application/json"},
                params={"type": "service"})
            for url in load_sls_hosts(bootstrap_url)}

    all_responses = {}
    for url, job in jobs.items():
        rsp = job.result()
        if rsp.status_code == 200:
            all_responses[url] = rsp.json()
        else:
            logging.error("'%s' returned status code %d" % (url, rsp.status_code))
            all_responses[url] = []
    return all_responses


def update_cached_mps(bootstrap_url=SLS_BOOTSTRAP_URL, cache_filename=CACHED_SERVICE_LIST_FILENAME):
    with open(cache_filename, "w") as f:
        f.write(json.dumps(load_services(bootstrap_url)))


def load_mps(tool, cache_filename=CACHED_SERVICE_LIST_FILENAME):
    with open(cache_filename) as f:
        sls_cache = json.loads(f.read())
    for url in sls_cache.keys():
        for s in sls_cache[url]:
            #logging.debug("s['service-type'] : %s" % s["service-type"])
            if "pscheduler" not in s["service-type"]:
                continue
            if "pscheduler-tools" not in s:
                logging.debug("'pscheduler-tools' not in s: " + json.dumps(s))
                continue
            if tool not in s["pscheduler-tools"]:
                continue
            for l in s["service-locator"]:
              yield l


if __name__ == "__main__":
    update_cached_mps()
    print(list(load_mps("owping")))
    
