from MacOpener import MacOpener
from MacStore import *
from datetime import datetime


class MacsOpener:
    def __init__(self, mac_store, mac_opener=None):
        self.macStore = mac_store
        self.macOpener = mac_opener or MacOpener()

    def do(self):
        print('---opening', len(self.macStore.get_macs()), 'macs at', datetime.now())
        print('servers:', [(server['host'], server['ready']) for server in self.macOpener.get_servers()])
        for mac_isp in self.macStore.get_macs():
            # print('opening mac:', mac_isp[0], mac_isp[1])
            self.macOpener.open(mac_isp[0], mac_isp[1])

    def set_mac_opener(self, mac_opener):
        self.macOpener = mac_opener

    def get_mac_opener(self):
        return self.macOpener

    def get_mac_store(self):
        return self.macStore


class MacsOpenerWithChecker:
    def __init__(self, macs_opener, status_checker):
        self.status_checker = status_checker
        self.macs_opener = macs_opener

    def do(self):
        if self.status_checker.is_alive():
            self.macs_opener.do()
        else:
            print('---skipped macs opening: server disconnected')


class MacsOpenerWithDeduplicate:
    def __init__(self, macs_opener):
        self.macs_opener = macs_opener

    def do(self):
        if isinstance(self.macs_opener.get_mac_store(), Deduplicatable):
            self.macs_opener.get_mac_store().deduplicate()
        self.macs_opener.do()


if __name__ == '__main__':
    action = MacsOpener(MacStoreByCsv(), MacOpener(local_ip='10.21.124.111'))
    action.do()