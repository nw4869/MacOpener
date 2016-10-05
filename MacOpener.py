# coding: utf-8
import socket
import struct
import IpFinder


class MacOpener:

    ISP_CHINA_UNICOM = 1
    ISP_CHINA_TELECOM = 2
    ISP_CHINA_MOBILE = 3

    def __init__(self, server='172.16.1.1', port=20015, local_ip=None):
        self.server = server
        self.port = port
        self.uid = b'test'
        if local_ip is not None:
            self.ip = socket.inet_aton(local_ip)
        else:
            # only available for dormitory subnet
            IpFinder.get_ip_startswith('10.21.')
        assert self.ip is not None, 'Can not find a correct local ip address.'

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

    def open(self, mac, isp):
        mac = mac.replace('-', ':').upper().strip()
        data = self._make_packet(mac.encode(), isp)
        print(data.hex())
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(data, (self.server, self.port))
        # print(self.ip, ":", s.recv(1024).hex())
        s.close()


if __name__ == '__main__':
    opener = MacOpener(local_ip='10.21.124.10')
    opener.open('74:D0:2B:4B:8E:00', MacOpener.ISP_CHINA_MOBILE)
