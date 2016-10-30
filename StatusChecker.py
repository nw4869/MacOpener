import datetime


class StatusChecker:
    def __init__(self, mac_opener, timeout):
        self.mac_opener = mac_opener
        self.timeout = timeout
        self.alive = False
        self.last_hour = -1

    def do(self):
        self.alive = self.mac_opener.check_server_status(self.timeout)
        # log every 30 minutes
        if self.last_hour != -1 or self.last_hour != datetime.datetime.now().hour and datetime.datetime.now().minute % 30 == 0:
            self.last_hour = datetime.datetime.now().hour
            print(datetime.datetime.now(), 'alive:', self.alive)
        return self.alive

    def is_alive(self):
        return self.alive

    def set_alive(self, alive):
        self.alive = alive
