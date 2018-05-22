import json
import logging
import random
import requests

logging.basicConfig(level=logging.DEBUG)

SLS_BOOTSTRAP_URL = "http://ps-west.es.net:8096/lookup/activehosts.json"
CACHED_SERVICE_LIST_FILENAME = "/tmp/sls-cache.json"

def load_sls_mirrors(bootstrap_url):
    rsp = requests.get(
        bootstrap_url,
        headers={"Accept": "application/json"})
    assert rsp.status_code == 200

    return [
        h["locator"] for h in rsp.json()["hosts"]
        if h["status"] == "alive"
    ]

def load_services(bootstrap_url):

    sls_mirror = random.choice(load_sls_mirrors(bootstrap_url))

    rsp = requests.get(
        sls_mirror,
        headers={"Accept": "application/json"},
        params={"type": "service"})

    assert rsp.status_code == 200
    return rsp.json() 

def update_cached_mps(bootstrap_url=SLS_BOOTSTRAP_URL, cache_filename=CACHED_SERVICE_LIST_FILENAME):
    with open(cache_filename, "w") as f:
        f.write(json.dumps(load_services(bootstrap_url)))

def load_mps(tool, cache_filename=CACHED_SERVICE_LIST_FILENAME):
    with open(cache_filename) as f:
        sls_cache = json.loads(f.read())
    for s in sls_cache:
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
    
