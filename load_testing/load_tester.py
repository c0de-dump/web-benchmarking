import dataclasses
import os.path
import shutil
from datetime import datetime, timedelta

from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome, ChromeOptions


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


def get_response_interceptor(lower_bound):
    def intercept_response(req, res):
        cache_control = res.headers['cache-control']
        if not cache_control:
            return
        for cache_control_val in cache_control.replace(" ", "").split(","):
            if 'max-age' not in cache_control_val:
                continue
            try:
                _, max_age = cache_control_val.split('=')
            except Exception as e:
                print(e, req.url, cache_control_val)
                continue
            max_age = int(max_age)
            if max_age < lower_bound:
                del res.headers['cache-control']
                res.headers['cache-control'] = 'no-cache'

    return intercept_response


class LoadTester:
    PROFILE_PATH = "./profile1"

    @classmethod
    def _get_driver(cls):
        options = ChromeOptions()
        options.add_argument(f"user-data-dir={cls.PROFILE_PATH}")
        options.add_argument("--headless")

        driver = Chrome(options=options)

        WebDriverWait(driver, 60).until(
            lambda dr: dr.execute_script('return document.readyState') == 'complete')

        return driver

    def __init__(self, network_condition: NetworkCondition, **kwargs):
        self.network_condition = network_condition
        if os.path.exists(self.PROFILE_PATH):
            shutil.rmtree(self.PROFILE_PATH)

    def calculate_load_time(self, website):
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
    def _get_time_points(cls):
        return [366, 200, 93, 32, 15, 8, 5, 2, 1, 0]


class ClassicLoadTester(LoadTester):
    @classmethod
    def name(cls):
        return "ClassicLoadTester"

    def calculate_load_time(self, website):
        time_points_days = sorted(self._get_time_points(), reverse=True)
        output_keys = ["-1", *list(map(lambda p: str(p), self._get_time_points()))]
        print("All keys are ", output_keys)

        output = {}
        i = 0
        while i <= len(time_points_days):
            key = output_keys.pop(0)
            print(f"calculate {key} ...")

            driver = self._get_driver()
            self._set_network_condition(driver)
            driver.request_interceptor = get_request_interceptor()

            if i != len(time_points_days):
                next_days_passed = time_points_days[i]
                driver.response_interceptor = get_response_interceptor(next_days_passed * 24 * 60 * 60)

            stat = self.visit_site_and_get_stats(driver, website)

            output[key] = stat

            driver.quit()
            i += 1

        return output


class CacheV2LoadTester(LoadTester):
    @classmethod
    def name(cls):
        return "CacheV2LoadTester"

    def calculate_load_time(self, website):
        time_points_days = self._get_time_points()
        output_keys = ["-1", *reversed(list(map(lambda p: str(p), time_points_days)))]
        print("All keys are ", output_keys)

        output = {}
        for _ in range(len(time_points_days) + 1):
            key = output_keys.pop(0)
            print(f"calculate {key} ...")

            driver = self._get_driver()
            driver.request_interceptor = chain_request_interceptors([
                get_cache_v2_enable_request_interceptor(),
                get_request_interceptor(),
            ]
            )
            self._set_network_condition(driver)
            stat = self.visit_site_and_get_stats(driver, website)

            output[key] = stat

            driver.quit()

        return output
