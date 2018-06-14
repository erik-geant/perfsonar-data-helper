import os
import tempfile
import pytest
import perfsonar_data_helper


@pytest.fixture
def app_config():
    with tempfile.TemporaryDirectory() as dir_name:
        settings_filename = os.path.join(dir_name, "settings.config")
        with open(settings_filename, "w") as f:
            f.write("SLS_BOOTSTRAP_URL = 'http://ps-west.es.net:8096/lookup/activehosts.json'\n")
            f.write("SLS_CACHE_FILENAME = '%s'\n" %
                    os.path.join(dir_name, "test-sls-cache.json"))

            # f.write("STARTUP_REFRESH_SLS_CACHE = True\n")
            f.write("STARTUP_REFRESH_SLS_CACHE = False\n")
            f.write("PSCHEDULER_TASK_POLLING_INTERVAL_SECONDS = 0\n")
        yield settings_filename

@pytest.fixture
def client(app_config):
    os.environ["SETTINGS_FILENAME"] = app_config
    return perfsonar_data_helper.create_app().test_client()

