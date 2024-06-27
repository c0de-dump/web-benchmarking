import datetime
import subprocess
import os


class TimeFaker:
    def __init__(self, start_point: datetime.datetime):
        subprocess.run(['timedatectl', 'set-ntp', '0'])
        self.start_point = start_point
        self.sys_password = None

    def move_time_till(self, delta: datetime.timedelta):
        next_time = self.start_point + delta
        self._set_time(next_time)

    @classmethod
    def _set_time(cls, t: datetime):
        formatted_time = t.strftime('%Y-%m-%d %H:%M:%S')
        ps = subprocess.Popen(('echo', os.environ['CHANGE_TIME_PASSWORD']), stdout=subprocess.PIPE)
        subprocess.run(['sudo', '-S', 'date', '-s', formatted_time], stdin=ps.stdout)

    @classmethod
    def reset_time(cls):
        subprocess.run(['timedatectl', 'set-ntp', '1'])
