# coding: utf-8
import argparse
import socket
import struct
import re
import select
import time


class MacOpener:
    ISP_CHINA_UNICOM = 1
    ISP_CHINA_TELECOM = 2
    ISP_CHINA_MOBILE = 3

    DEFAULT_SERVER = '172.16.1.1'
    DEFAULT_PORT = 20015

    def __init__(self, server=DEFAULT_SERVER, port=DEFAULT_PORT, local_ip=None, debug=False, ip_forward=False):
        self.server = server
        self.port = port
        self.uid = b'test'
        self.ip = None
        self.debug = debug
        if ip_forward:
            self.ip = self.server
        else:
            if local_ip is not None:
                self.ip = local_ip
            else:
                # only available for dormitory subnet
                import IpFinder
                self.ip = IpFinder.get_ip_startswith('10.21.') or IpFinder.get_ip_startswith('10.20.')
            assert ip_forward or self.ip is not None, 'Can not find a correct local ip address. \
    Please specify the IP address thought command-line argument using --ip'
        self.ip = socket.inet_aton(self.ip)

    def get_server(self):
        return self.server, self.port

    def set_server(self, server, port=DEFAULT_PORT, ip_forward=False):
        self.server = server
        self.port = port
        if ip_forward:
            self.ip = socket.inet_aton(server)

    def get_local_ip(self):
        return socket.inet_ntoa(self.ip)

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


class MacOpenerMultiServer:
    class Server:
        def __init__(self, host, port, ip_forward, mac_opener):
            self.host = host
            self.port = port
            self.ip_forward = ip_forward
            self.ready = False
            self.last_ready_time = time.time()
            self.mac_opener = mac_opener

    def __init__(self, servers, local_ip=None, debug=False):
        self.servers = []
        self.local_ip = local_ip
        self.debug = debug

        self.set_servers(servers)

    def add_server(self, host, port, ip_forward=False):
        for server in self.servers:
            if host == server.host and port == server.port and ip_forward == server.ip_forward:
                return
        mac_opener = MacOpener(host, port, self.local_ip, self.debug, ip_forward)
        self.servers.append(MacOpenerMultiServer.Server(host, port, ip_forward, mac_opener))

    def get_servers(self):
        def dict_without_opener(server):
            d = dict(server.__dict__)
            if 'mac_opener' in d:
                del d['mac_opener']
            return d
        return list(map(dict_without_opener, self.servers))

    def set_servers(self, servers):
        for server in servers:
            self.add_server(server[0], server[1], server[2])

    def get_local_ip(self):
        if self.local_ip is None:
            return None
        return socket.inet_ntoa(self.local_ip)

    def do(self, mac, isp, op):
        for i in range(len(self.servers)):
            self.debug and print('server:', self.servers[i].__dict__, end=' ')
            if self.servers[i].ready:
                self.servers[i].mac_opener.do(mac, isp, op)
                self.debug and print('send.')
            else:
                self.debug and print('pass.')

    def open(self, mac, isp):
        self.do(mac, isp, 0)

    def close(self, mac, isp):
        self.do(mac, isp, 1)

    def check_server_status(self, timeout):
        mac = 'AA:BB:CC:DD:EE:FF'
        isp = 1
        op = 0

        sockets = []
        sockets_server_dict = {}
        for i in range(len(self.servers)):
            mac_opener = self.servers[i].mac_opener
            data = mac_opener._make_packet(mac.encode(), isp, op)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setblocking(False)
            server, port = mac_opener.get_server()
            s.sendto(data, (server, port))
            sockets.append(s)
            sockets_server_dict[s] = self.servers[i]

        left_time = timeout
        while left_time > 0 and len(sockets_server_dict) > 0:
            start_time = time.time()
            ready = select.select(sockets, [], [], left_time)
            for s in ready[0]:
                if s in sockets_server_dict:
                    server = sockets_server_dict[s]
                    server.last_ready_time = time.time()
                    server.ready = True
                    del sockets_server_dict[s]
            left_time -= time.time() - start_time

        for timeout_server in sockets_server_dict.values():
            timeout_server.ready = False
            if time.time() - timeout_server.last_ready_time > 60 * 60 * 24:  # timeout a day
                # remove server
                self.servers.remove(timeout_server)

        return len(self.servers) > len(sockets_server_dict)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MAC opener for GUET by nightwind')
    parser.add_argument('-s', '--server', default='172.16.1.1')
    parser.add_argument('-sp', '--server port', dest='server_port', type=int, default=20015)
    parser.add_argument('-i', '--ip')
    parser.add_argument('-o', '--op', type=int, default=0)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('mac')
    parser.add_argument('isp', type=int, choices=[1, 2, 3])
    parser.add_argument('--ip_forward', action='store_true')
    args = parser.parse_args()

    if args.ip_forward and args.server == MacOpener.DEFAULT_SERVER:
        print('--ip_forward reply on --server')
        exit(1)

    mac = args.mac.replace('-', ':').upper().strip()
    if not re.match('^([0-9a-fA-F]{2})(([:][0-9a-fA-F]{2}){5})$', mac):
        print('MAC address is incorrect. (XX:XX:XX:XX:XX:XX)')
        exit(1)

    try:
        opener = MacOpener(server=args.server, port=args.server_port, local_ip=args.ip, debug=args.debug,
                           ip_forward=args.ip_forward)
        opener.do(args.mac, args.isp, args.op)
    except AssertionError as e:
        print(e)
        exit(1)
