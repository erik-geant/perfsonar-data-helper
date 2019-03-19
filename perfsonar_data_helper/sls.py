import json
import logging
import re
import requests
from requests_futures.sessions import FuturesSession


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

        try:
            rsp = job.result()
        except requests.ConnectionError as e:
            logging.error(str(e))
            continue

        if rsp.status_code == 200:
            all_responses[url] = rsp.json()
        else:
            logging.error(
                "'%s' returned status code %d" % (url, rsp.status_code))
            all_responses[url] = []
    return all_responses


# def hostname_from_url(url):
#     m = re.match("http.://(\[.*\]).*", url)
#     if m is not None:
#         return m.group(1)
#     m = re.match(".*//([^:/]+).*", url)
#     if m is not None:
#         return m.group(1)
#     return "???"


def update_cached_mps(bootstrap_url, cache_filename):
    with open(cache_filename, "w") as f:
        f.write(json.dumps(load_services(bootstrap_url)))


def hostname_from_url(url):
    m = re.match(r'^(?P<scheme>http|https|tcp)://(?P<hostname>[^/]+).*', url)
    if m is None:
        return url
    m1 = re.match(r'^(.*):[^\[\]:]+$', m.group("hostname"))
    if m1:
        return m1.group(1)
    return m.group("hostname")


def load_mps(tool, cache_filename):

    _tool_name_equivalencies = {
        "owping": {"owping", "owamp"},
        "owamp": {"owping", "owamp"},
    }

    def _has_tool(tool_name, service):
        eqtools = _tool_name_equivalencies.get(tool_name, {tool_name})
        service_type = service.get("service-type", [])
        if "pscheduler" in service_type:
            pscheduler_tools = service.get("pscheduler-tools", [])
            if eqtools & set(pscheduler_tools):
                return True
            return False
        if eqtools & set(service_type):
            return True
        return False

    with open(cache_filename) as f:
        sls_cache = json.loads(f.read())
    for url in sls_cache.keys():
        for s in sls_cache[url]:
            if _has_tool(tool, s):

                service_locators = s.get("service-locator", [])
                service_names = s.get("service-name", [])
                if len(service_names) == 0:
                    service_name = "???"
                else:
                    service_name = service_names[0]
                communities = s.get("group-communities", [])
                for l in service_locators:
                    yield {
                        "name": service_name,
                        "hostname": hostname_from_url(l),
                        "communities": communities
                    }


if __name__ == "__main__":
    from perfsonar_data_helper import default_settings

    logging.basicConfig(level=logging.DEBUG)

    update_cached_mps(
        default_settings.SLS_BOOTSTRAP_URL,
        default_settings.SLS_CACHE_FILENAME)
    mps = load_mps(
        "owping",
        default_settings.SLS_CACHE_FILENAME)

    logging.info(list(mps))
