import datetime
import subprocess
from shared.logging import logger
from time import sleep

class TimeFaker:
    def __init__(self, start_point: datetime.datetime):
        # subprocess.run(['sudo', 'timedatectl', 'set-ntp', '0'])
        self.start_point = start_point
        self.sys_password = None

    def move_time_till(self, delta: datetime.timedelta):
        next_time = self.start_point + delta
        formatted_time = next_time.strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"Moving time to {formatted_time}")
        subprocess.run(f"sudo -k date -s '{formatted_time}'", shell=True)
        # self._set_time(next_time)

    # @classmethod
    # def _set_time(cls, t: datetime):
    #     formatted_time = t.strftime('%Y-%m-%d %H:%M:%S')
    #     ps = subprocess.Popen(('echo', "YOUR_PASSWORD"), stdout=subprocess.PIPE)
    #     subprocess.run(['sudo', '-S', 'date', '-s', formatted_time], stdin=ps.stdout)

    def reset_time(self):
        subprocess.run(f"sudo -k systemctl restart ntp", shell=True)
        sleep(1)
