from MacOpener import MacOpener
from MacStore import *
from datetime import datetime


class MacsOpener:
    def __init__(self, mac_store, mac_opener=None):
        self.macStore = mac_store
        self.macOpener = mac_opener or MacOpener()

    def do(self):
        print('---opening', len(self.macStore.get_macs()), 'macs at', datetime.now())
        for mac_isp in self.macStore.get_macs():
            print('opening mac:', mac_isp[0], mac_isp[1])
            self.macOpener.open(mac_isp[0], mac_isp[1])

    def set_mac_opener(self, mac_opener):
        self.macOpener = mac_opener

    def get_mac_opener(self):
        return self.macOpener

if __name__ == '__main__':
    action = MacsOpener(MacStoreByCsv(), MacOpener(local_ip='10.21.124.111'))
    action.do()