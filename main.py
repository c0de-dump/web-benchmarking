import time
from datetime import datetime

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome, ChromeOptions

from load_testing.controller import LoadTesterController
from load_testing.load_tester import LoadTester, ClassicLoadTester, CacheV2LoadTester


def main():
    options = ChromeOptions()

    options.add_argument("user-data-dir=./profile1")
    driver = Chrome(options=options)

    # Enable Network and set up interception
    driver.execute_cdp_cmd('Network.enable', {})

    def intercept_request(req):
        if 'localhost' not in req.url:
            req.create_response(status_code=200)

    def intercept_response(req, res):
        cache_control = res.headers['cache-control']
        if not cache_control:
            return
        for cache_control_val in cache_control.replace(" ", "").split(","):
            if 'max-age' not in cache_control_val:
                continue
            _, max_age = cache_control_val.split('=')
            max_age = int(max_age)
            if 'close-icon' in req.url:
                del res.headers['cache-control']
                res.headers['cache-control'] = 'no-cache'
                print(req.url, "changed header")

    # Set the request interception patterns
    # driver.execute_cdp_cmd('Network.setRequestInterception', {
    #     'patterns': [
    #         {'urlPattern': '*'}
    #     ]
    # })

    # Set the interception handler
    driver.request_interceptor = intercept_request
    driver.response_interceptor = intercept_response

    # First request to load the page and cache resources
    time.sleep(10)
    before = datetime.now()
    driver.get('http://localhost/varzesh3/')
    WebDriverWait(driver, 30).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    after = datetime.now()
    print("First load time:", after - before)

    # Wait for a while to simulate some delay
    time.sleep(1)

    # Second request to load the page again
    before = datetime.now()
    driver.get('http://localhost/varzesh3/')
    after = datetime.now()
    print("Second load time:", after - before)

    time.sleep(100)

    driver.quit()


if __name__ == "__main__":
    controller = LoadTesterController(["http://localhost/varzesh3/"], '/usr/bin/google-chrome', 1)
    print(controller.calculate_and_plot())
