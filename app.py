from flask import Flask, render_template
from flask import request, jsonify
from MacOpener import MacOpener
import re
from MacStore import MacStoreByCsv
from MacsOpener import MacsOpener, MacsOpenerWithChecker, MacsOpenerWithDeduplicate
from RepeatTimer import RepeatTimer
import argparse
from StatusChecker import StatusChecker
from threading import Thread

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', mac=request.args.get('mac'), isp=request.args.get('isp'),
                           interval=args.interval, alive=status_checker.is_alive())


@app.route('/', methods=['POST'])
def submit():
    mac = request.form.get('mac')
    isp = request.form.get('isp')
    save = 'save' in request.form

    error = ''
    if mac is None or len(mac) == 0 or isp is None:
        error = 'MAC or isp is None'

    if not error and not isp.isalnum() or int(isp) > 3:
        error = 'isp is incorrect'

    if not error:
        mac = mac.replace('-', ':').upper().strip()
        if not re.match('^([0-9a-fA-F]{2})(([:][0-9a-fA-F]{2}){5})$', mac):
            error = 'wrong format of MAC (should be HH:HH:HH:HH:HH:HH or HH-HH-HH-HH-HH-HH)'

    if error:
        return render_template('index.html', error=error, mac=mac, isp=isp, interval=args.interval,
                               alive=status_checker.is_alive())

    mac_opener.open(mac, int(isp))
    print(mac, isp)
    if save:
        mac_store.add_mac(mac, isp)
    return render_template('index.html', success=True, mac=mac, isp=isp, interval=args.interval,
                           alive=status_checker.is_alive())


@app.route('/update_server')
def show_update_server():
    return render_template('update_server.html')


def validate_key(key):
    return key == args.key


@app.route('/api/server', methods=['GET', 'POST'])
def update_server():
    if request.method == 'GET':
        ip, port = mac_opener.get_server()
        return jsonify({'ip': ip, 'port': port})
    key = request.form.get('key')
    ip = request.form.get('ip')
    port = request.form.get('port', str(MacOpener.DEFAULT_PORT))
    blocking = request.form.get('blocking', 'False')
    blocking = blocking.upper() == 'TRUE'
    ip_forward = request.form.get('ip_forward', 'TRUE')
    ip_forward = ip_forward.upper() == 'TRUE'

    error = ''
    if ip is None:
        error = 'ip is required'
    if not re.match(r'^((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)(\.((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)){3}$', ip):
        error = 'wrong format of ip address'

    if port and not port.isdigit():
        error = 'wrong format of port'
    port = int(port)

    if not error and key is None:
        error = 'key is required'

    def result(reason, code):
        return jsonify({'success': 200 <= code < 300, 'reason': reason}), code

    if error:
        return result(error, 400)

    if not validate_key(key):
        return result('key is incorrect', 401)

    try:
        opener = MacOpener(server=ip, port=port, local_ip=mac_opener.get_local_ip(), ip_forward=ip_forward)
    except AssertionError as e:
        return result(e, 400)
    checker = StatusChecker(opener, args.timeout)
    if blocking:
        if not checker.do():
            return result('server timeout', 400)
        else:
            return result('success', 201)
    else:
        def check_and_update():
            if checker.do():
                mac_opener.set_server(ip, port, ip_forward)
        Thread(target=check_and_update).start()
        return result('accepted', 202)


def simple(env, resp):
    resp('302 Found', [('Location', app.config["APPLICATION_ROOT"]), ('Content-Type', 'text/plain')])
    return [b'Hello WSGI World']


def parse_args():
    parser = argparse.ArgumentParser(description='MAC opener for GUET by nightwind')
    parser.add_argument('-l', '--listen', default='0.0.0.0')
    parser.add_argument('-p', '--port', type=int, default=5000)
    parser.add_argument('-s', '--server', default='172.16.1.1')
    parser.add_argument('-sp', '--server port', type=int, dest='server_port', default=20015)
    parser.add_argument('-i', '--ip')
    parser.add_argument('-t', '--interval', type=int, default=5 * 60)
    parser.add_argument('-d', '--delay', type=int, default=1)
    parser.add_argument('-r', '--root', default=None)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--timeout', type=int, default=3, help='status checker timeout seconds')
    parser.add_argument('--checker_interval', type=int, default=10, help='status checker interval seconds')
    parser.add_argument('--ip_forward', action='store_true')
    parser.add_argument('-k', '--key', help='the password for update server (default:I_am_the_key)',
                        default='I_am_the_key')
    args = parser.parse_args()
    if args.ip_forward and args.server == MacOpener.DEFAULT_SERVER:
        print('--ip_ward reply on --server')
        exit(1)
    return args


def start_timer(action, interval, delay):
    RepeatTimer(interval, action.do, delay, daemon=True).start()


def start_app():
    app.config['DEBUG'] = args.debug
    app.config['args'] = args
    if args.root and args.root != '/':
        if not args.root.startswith('/'):
            args.root = '/' + args.root
        from werkzeug.serving import run_simple
        from werkzeug.wsgi import DispatcherMiddleware
        app.config["APPLICATION_ROOT"] = args.root
        application = DispatcherMiddleware(simple, {
            app.config['APPLICATION_ROOT']: app,
        })
        run_simple(args.listen, args.port, application, use_reloader=args.debug)
    else:
        app.run(args.listen, args.port, debug=args.debug)


if __name__ == '__main__':
    args = parse_args()

    try:
        mac_store = MacStoreByCsv()
        mac_opener = MacOpener(server=args.server, port=args.server_port, local_ip=args.ip, ip_forward=args.ip_forward)

        status_checker = StatusChecker(mac_opener, args.timeout)
        start_timer(status_checker, args.checker_interval, 0)

        macs_opener = MacsOpener(mac_store, mac_opener)
        macs_opener = MacsOpenerWithDeduplicate(macs_opener)
        macs_opener = MacsOpenerWithChecker(macs_opener, status_checker)

        start_timer(macs_opener, args.interval, args.delay)

        start_app()
    except AssertionError as e:
        print(e)
        exit(1)
