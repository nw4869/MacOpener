import datetime


class StatusChecker:
    def __init__(self, mac_opener, timeout):
        self.mac_opener = mac_opener
        self.timeout = timeout
        self.alive = False
        self.first = True

    def do(self):
        self.alive = self.mac_opener.check_server_status(self.timeout)
        if self.first or datetime.datetime.now().minute % 30 == 0:
            self.first = False
            print(datetime.datetime.now(), 'alive:', self.alive)

    def is_alive(self):
        return self.alive
