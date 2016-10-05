import os


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


@singleton
class MacStore:
    def get_macs(self):
        raise NotImplementedError

    def set_macs(self, macs):
        raise NotImplementedError

    def add_mac(self, mac):
        raise NotImplementedError

    def remove_mac(self, mac):
        raise NotImplementedError

    def contains(self, mac):
        raise NotImplementedError


@singleton
class MacStoreByCsv:
    def __init__(self, path='macs.csv'):
        self.path = path

    def get_macs(self):
        if not os.path.exists(self.path):
            return []
        macs = []
        file = open(self.path)
        for line in file.readlines():
            mac, isp = line.split(',')
            mac = mac.replace('-', ':').upper().strip()
            isp = int(isp)
            macs.append((mac, isp))
        file.close()
        return macs
