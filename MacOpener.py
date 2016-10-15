# coding: utf-8
import argparse
import socket
import struct
import re
import select
import IpFinder


class MacOpener:
    ISP_CHINA_UNICOM = 1
    ISP_CHINA_TELECOM = 2
    ISP_CHINA_MOBILE = 3

    def __init__(self, server='172.16.1.1', port=20015, local_ip=None, debug=False):
        self.server = server
        self.port = port
        self.uid = b'test'
        self.ip = None
        self.debug = debug
        if local_ip is not None:
            self.ip = socket.inet_aton(local_ip)
        else:
            # only available for dormitory subnet
            self.ip = socket.inet_aton(IpFinder.get_ip_startswith('10.21.'))
        assert self.ip is not None, 'Can not find a correct local ip address. \
Please specify the IP address thought command-line argument using --ip'

    @staticmethod
    def _checksum(data):
        cs = 0x4e67c6a7
        for b in data:
            cs &= 0xffffffff
            if cs < 0x80000000:
                cs ^= ((cs >> 2) + (cs << 5) + b) & 0xffffffff
            else:
                cs ^= (((cs >> 2) | 0xC0000000) + (cs << 5) + b) & 0xffffffff
                # print(cs.to_bytes(4, 'big').hex().upper())
        return cs & 0x7fffffff

    def _make_packet(self, mac, isp, op=0, uid=None, ip=None):
        packet = struct.pack('!30s 4s 17s 3x B B',
                             uid or self.uid, ip or self.ip, mac, isp, op)
        return struct.pack('<56s I', packet, self._checksum(packet))

    def do(self, mac, isp, op):
        mac = mac.replace('-', ':').upper().strip()
        data = self._make_packet(mac.encode(), isp, op)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(data, (self.server, self.port))
        if self.debug:
            print(data.hex())
            print(self.ip, ":", s.recv(1024).hex())
        s.close()

    def open(self, mac, isp):
        self.do(mac, isp, 0)

    def close(self, mac, isp):
        self.do(mac, isp, 1)

    def check_server_status(self, timeout):
        mac = 'AA:BB:CC:DD:EE:FF'
        isp = 1
        op = 0
        data = self._make_packet(mac.encode(), isp, op)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(data, (self.server, self.port))

        success = False
        s.setblocking(False)
        ready = select.select([s], [], [], timeout)
        if ready[0]:
            success = True
        return success


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MAC opener for GUET by nightwind')
    parser.add_argument('-s', '--server', default='172.16.1.1')
    parser.add_argument('-sp', '--server port', dest='server_port', type=int, default=20015)
    parser.add_argument('-i', '--ip')
    parser.add_argument('-o', '--op', type=int, default=0)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('mac')
    parser.add_argument('isp', type=int, choices=[1, 2, 3])
    args = parser.parse_args()

    mac = args.mac.replace('-', ':').upper().strip()
    if not re.match('^([0-9a-fA-F]{2})(([:][0-9a-fA-F]{2}){5})$', mac):
        print('MAC address is incorrect. (XX:XX:XX:XX:XX:XX)')
        exit(1)

    try:
        opener = MacOpener(server=args.server, port=args.server_port, local_ip=args.ip, debug=args.debug)
        opener.do(args.mac, args.isp, args.op)
    except AssertionError as e:
        print(e)
        exit(1)
