import dataclasses
import os.path
import shutil
import datetime

from datetime import datetime, timedelta

from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome, ChromeOptions

from load_testing.time_faker import TimeFaker
from shared.logging import logger
import logging

_logger = logging.getLogger('seleniumwire')
_logger.setLevel(logging.FATAL)

@dataclasses.dataclass
class NetworkCondition:
    latency: int
    download: int
    upload: int

    def __str__(self):
        return f"(latency: {self.latency}, download: {self.download}, upload: {self.upload})"

    def name(self):
        return str(self)


class RequestInterceptor:
    def __init__(self, max_age_mapping):
        self.max_age_mapping = max_age_mapping

    def __call__(self, request, *args, **kwargs):
        pass


def get_request_interceptor():
    def intercept_request(req):
        if 'localhost' not in req.url:
            req.create_response(status_code=200)

    return intercept_request


def get_cache_v2_enable_request_interceptor():
    def intercept_request(req):
        req.headers['X-CacheV2-Extension-Enabled'] = 'true'

    return intercept_request


def chain_request_interceptors(interceptors):
    def chain(req):
        for interceptor in interceptors:
            interceptor(req)

    return chain


class LoadTester:
    PROFILE_PATH = "./profile1"

    @classmethod
    def _get_driver(cls, chrome_path):
        options = ChromeOptions()
        options.add_argument(f"user-data-dir={cls.PROFILE_PATH}")
        options.binary_location = chrome_path
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = Chrome(options=options, seleniumwire_options={"request_storage": "memory"})

        WebDriverWait(driver, 60).until(
            lambda dr: dr.execute_script('return document.readyState') == 'complete')

        return driver

    def __init__(self, network_condition: NetworkCondition, **kwargs):
        self.network_condition = network_condition
        if os.path.exists(self.PROFILE_PATH):
            shutil.rmtree(self.PROFILE_PATH)

    def calculate_load_time(self, chrome, website):
        raise NotImplementedError

    @classmethod
    def name(cls):
        raise NotImplementedError

    def _set_network_condition(self, driver):
        driver.set_network_conditions(
            latency=self.network_condition.latency,
            download_throughput=self.network_condition.download,
            upload_throughput=self.network_condition.upload,
        )

    @classmethod
    def visit_site_and_get_stats(cls, driver, website):
        before = datetime.now()
        driver.get(website)
        after = datetime.now()

        return int((after - before).total_seconds() * 1000)  # mili

    @classmethod
    def _get_time_deltas(cls):
        return [
            timedelta(minutes=1),
            timedelta(hours=1),
            timedelta(hours=6),
            timedelta(days=1),
            timedelta(days=7),
            timedelta(days=366),
        ]


class ClassicLoadTester(LoadTester):
    @classmethod
    def name(cls):
        return "ClassicLoadTester"

    def calculate_load_time(self, chrome, website):
        output = {}

        driver = self._get_driver(chrome)

        self._set_network_condition(driver)
        driver.request_interceptor = get_request_interceptor()

        stat = self.visit_site_and_get_stats(driver, website)
        time_faker = TimeFaker(datetime.now())

        driver.quit()

        for delta in self._get_time_deltas():
            driver = self._get_driver(chrome)
            self._set_network_condition(driver)
            driver.request_interceptor = get_request_interceptor()

            time_faker.move_time_till(delta)
            logger.error("now is: " + str(datetime.now()))
            stat = self.visit_site_and_get_stats(driver, website)
            output[str(int(delta.total_seconds()))] = stat

            driver.quit()

        time_faker.reset_time()
        return output


class CacheV2LoadTester(LoadTester):
    @classmethod
    def name(cls):
        return "CacheV2LoadTester"

    def calculate_load_time(self, chrome, website):
        output = {}

        interceptor = chain_request_interceptors([
            get_cache_v2_enable_request_interceptor(),
            get_request_interceptor(),
        ])

        driver = self._get_driver(chrome)
        self._set_network_condition(driver)

        driver.request_interceptor = interceptor

        stat = self.visit_site_and_get_stats(driver, website)

        time_faker = TimeFaker(datetime.now())

        driver.quit()

        for delta in self._get_time_deltas():
            driver = self._get_driver(chrome)
            self._set_network_condition(driver)
            driver.request_interceptor = interceptor

            time_faker.move_time_till(delta)
            logger.info("now is: " + str(datetime.now()))
            stat = self.visit_site_and_get_stats(driver, website)
            output[str(int(delta.total_seconds()))] = stat

            driver.quit()

        time_faker.reset_time()
        return output
