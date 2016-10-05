from flask import Flask
from flask import request
from MacOpener import MacOpener
import re
import theadingTest

app = Flask(__name__)
macOpener = MacOpener(local_ip='10.21.124.107')


@app.route('/', methods=['GET', 'POST'])
def home():
    html = '''<form action="/" method="post">
                    <label>mac</label>
                    <input name="mac" id="mac"/>
                    <select name="sp">
                        <option value="1">联通</option>
                        <option value="2">电信</option>
                        <option value="3">移动</option>
                    </select>
                    <button type="submit">ok</button>
                </form>'''
    if request.method == 'GET':
        return html
    elif request.method == 'POST':
        mac = request.form['mac']
        sp = request.form['sp']

        if mac is None or sp is None:
            return html + '<label>error: not none</label>'

        if not sp.isalnum() or int(sp) > 3:
            return html + '<label>error: sp</label>'

        mac = mac.replace('-', ':')
        if not re.match('^([0-9a-fA-F]{2})(([:][0-9a-fA-F]{2}){5})$', mac):
            return html + '<label>mac error</label>'

        macOpener.open(mac.upper(), int(sp))
        print(mac, sp)
        return html + 'good luck!'

if __name__ == '__main__':
    theadingTest.go()
    app.run()
