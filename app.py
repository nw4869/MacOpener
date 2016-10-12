from flask import Flask
from flask import request
from MacOpener import MacOpener
import re
from MacStore import MacStoreByCsv
from MacsOpener import MacsOpener
from RepeatTimer import RepeatTimer
import argparse

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    html = '''<form action="/" method="post">
                    <label>mac</label>
                    <input name="mac" id="mac"/>
                    <select name="isp">
                        <option value="1">联通</option>
                        <option value="2">电信</option>
                        <option value="3">移动</option>
                    </select>
                    <input type="checkbox" id="save" name="save" value="save"/>
                    <label>save</label>
                    <button type="submit">ok</button>
                </form>'''
    if request.method == 'GET':
        return html
    elif request.method == 'POST':
        mac = request.form['mac']
        isp = request.form['sp']
        save = 'save' in request.form

        if mac is None or isp is None:
            return html + '<label>error: not none</label>'

        if not isp.isalnum() or int(isp) > 3:
            return html + '<label>error: sp</label>'

        mac = mac.replace('-', ':').strip()
        if not re.match('^([0-9a-fA-F]{2})(([:][0-9a-fA-F]{2}){5})$', mac):
            return html + '<label>mac error</label>'

        mac_opener.open(mac.upper(), int(isp))
        print(mac, isp)
        if save:
            mac_store.add_mac(mac, isp)
        return html + 'ok!'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MAC opener for GUET by nightwind')

    parser.add_argument('-l', '--listen', default='0.0.0.0')
    parser.add_argument('-p', '--port', default=5000)
    parser.add_argument('-s', '--server', default='172.16.1.1')
    parser.add_argument('-sp', '--server port', dest='server_port', default=20015)
    parser.add_argument('-i', '--ip')
    parser.add_argument('-t', '--interval', default=5 * 60)
    parser.add_argument('-d', '--delay', default=0)
    args = parser.parse_args()

    mac_store = MacStoreByCsv()
    mac_opener = MacOpener(server=args.server, port=args.server_port, local_ip=args.ip)
    action = MacsOpener(mac_store, mac_opener)
    timer = RepeatTimer(args.interval, action.do, args.delay)
    timer.setDaemon(True)
    timer.start()
    app.run()
