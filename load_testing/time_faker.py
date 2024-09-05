import datetime
import os


class TimeFaker:
    def __init__(self, start_point: datetime.datetime):
        self.start_point = start_point

    def move_time_till(self, delta: datetime.timedelta):
        self._set_relative_time(f"+{int(delta.total_seconds())}s")

    @classmethod
    def _set_relative_time(cls, rel_str: str):
        os.environ["FAKETIME"] = rel_str


    @classmethod
    def reset_time(cls):
        # subprocess.run(['timedatectl', 'set-ntp', '1'])
        pass
