import os


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


# @singleton
class MacStore:
    def get_macs(self):
        raise NotImplementedError

    def set_macs(self, macs):
        raise NotImplementedError

    def add_mac(self, mac, isp):
        raise NotImplementedError

    def remove_mac(self, mac):
        raise NotImplementedError

    def contains(self, mac):
        raise NotImplementedError

    def find(self, mac, isp):
        pass


@singleton
class MacStoreByCsv(MacStore):
    def __init__(self, path=None):
        file_path = os.path.dirname(os.path.abspath(__file__))
        self.path = path or os.path.join(file_path, 'macs.csv')

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

    def add_mac(self, mac, isp):
        if not os.path.exists(self.path):
            return
        with open(self.path, 'a') as f:
            mac = mac.replace('-', ':').upper().strip()
            mac_isp = mac + ', ' + isp + '\n'
            f.write(mac_isp)
            print(mac_isp, 'saved')
