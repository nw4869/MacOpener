import os
import threading


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


class Deduplicatable:
    def deduplicate(self):
        raise NotImplementedError


# @singleton
class MacStoreByCsv(MacStore, Deduplicatable):
    def __init__(self, path=None):
        file_path = os.path.dirname(os.path.abspath(__file__))
        self.path = path or os.path.join(file_path, 'macs.csv')
        self.file_lock = threading.Lock()

    def get_macs(self):
        if not os.path.exists(self.path):
            return []
        macs = []
        self.file_lock.acquire()
        file = open(self.path)
        for line in file.readlines():
            mac, isp = line.split(',')
            mac = mac.replace('-', ':').upper().strip()
            isp = int(isp)
            macs.append((mac, isp))
        file.close()
        self.file_lock.release()
        return macs

    def add_mac(self, mac, isp):
        if not os.path.exists(self.path):
            return
        self.file_lock.acquire()
        with open(self.path, 'a') as f:
            mac = mac.replace('-', ':').upper().strip()
            mac_isp = mac + ', ' + str(isp)
            f.write(mac_isp + '\n')
            print(mac_isp, 'saved')
        self.file_lock.release()

    def set_macs(self, macs):
        self.file_lock.acquire()
        with open(self.path, 'w') as f:
            for mac, isp in macs:
                mac = mac.replace('-', ':').upper().strip()
                mac_isp = mac + ', ' + str(isp)
                f.write(mac_isp + '\n')
        self.file_lock.release()

    def deduplicate(self):
        mac_set = set()
        mac_list = []
        for mac, isp in self.get_macs()[::-1]:
            if mac in mac_set:
                continue
            mac_set.add(mac)
            mac_list.append((mac, isp))
        self.set_macs(mac_list)


class MacStoreMemProxy(MacStore, Deduplicatable):
    def __init__(self, mac_store):
        self.mac_store = mac_store
        self.cache = None
        self.cache_is_dirty = False
        self.loaded = False

    def get_macs(self):
        if self.loaded and self.cache is not None and not self.cache_is_dirty:
            return list(self.cache.items())

        self.cache = dict(self.get_macs())
        self.cache_is_dirty = False
        self.loaded = True
        return self.cache

    def add_mac(self, mac, isp):
        self.mac_store.add_mac(mac, isp)

        if self.cache is None:
            self.cache = {}
        self.cache[mac] = isp

    def set_macs(self, macs):
        self.mac_store.set_macs(macs)

        self.cache = dict(macs)
        self.cache_is_dirty = False

    def deduplicate(self):
        if isinstance(self.mac_store, Deduplicatable):
            self.mac_store.deduplicate()
        # dict is not duplicate

    def refresh_macs(self):
        self.cache_is_dirty = True
