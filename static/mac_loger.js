/**
 * Created by nightwind on 16/10/19.
 */


    function to_index(href) {
        if (href == null){
            href = home
        }
        window.location.href = href
    }
    function set_isp(isp) {
        document.getElementById('isp')[isp - 1].selected = true;
    }
    function get_isp() {
        return document.getElementById('isp').selectedIndex + 1;
    }
    function set_mac(mac) {
        document.getElementById('mac').value = mac;
    }
    function get_mac() {
        return document.getElementById('mac').value;
    }
    function get_latest_mac_isp() {
        return get_macs().split('|')[0]
    }
    function get_macs() {
        if (document.cookie.length > 0) {
            var c_name = 'macs';
            var c_start = document.cookie.indexOf(c_name + "=");
            if (c_start != -1) {
                c_start = c_start + c_name.length + 1;
                var c_end = document.cookie.indexOf(";", c_start);
                if (c_end == -1) c_end = document.cookie.length;
                return document.cookie.substring(c_start, c_end)
            }
        }
        return ""
    }
    function push_cookie(mac, isp) {
        var _date = new Date();
        _date.setDate(_date.getDate() + 30);
        var macs = get_macs();
        if (macs.length == 0) {
            macs = mac + ',' + isp;
        } else {
            macs += '|' + mac + ',' + isp;
        }
        document.cookie = 'macs=' + macs + ';expires=' + _date.toGMTString();
    }
    function clear_macs() {
        document.cookie = 'macs=';
    }
    function submit(href) {
        document.getElementById('form').action = href;
        document.getElementById('form').submit();
    }
    function handle_success() {
        if (document.getElementById('success')) {
            push_cookie(get_mac(), get_isp());
            insert_history_item(get_mac(), get_isp());
            document.getElementById('history').style.display = ''
        }
    }
    function fill_mac_to_input(mac_isp) {
        mac_isp = mac_isp.split(',');
        if (mac_isp.length == 2) {
            set_mac(mac_isp[0].trim());
            set_isp(mac_isp[1].trim());
        }
    }
    function onclick_history_item(e) {
        fill_mac_to_input(e.innerText)
    }
    function insert_history_item(mac, isp) {
        var e = document.createElement('span');
        e.setAttribute('class', 'history_item');
        e.setAttribute('onclick', 'onclick_history_item(this)');
        e.appendChild(document.createTextNode(mac + ', ' + isp));
        var history_div = document.getElementById('history');
        var firstChild = history_div.firstElementChild;
        if (firstChild.nextElementSibling == null) {
            history_div.appendChild(e);
            e = document.createElement('span');
            e.setAttribute('class', 'history_item');
            e.setAttribute('style', 'border-style: none');
            var ec = document.createElement('button');
            ec.setAttribute('onclick', 'clear_macs(); to_index();');
            ec.appendChild(document.createTextNode('clear'));
            e.appendChild(ec);
            history_div.appendChild(e);
        } else {
            history_div.insertBefore(e, firstChild.nextElementSibling);
        }
    }
    function show_history() {
        var macs = get_macs().split('|');
        if (macs[0].length == 0) {
            // hide History
            document.getElementById('history').style.display = 'none';
            return;
        }
        document.getElementById('history').style.display = '';
        for (var i = 0; i < macs.length; i++) {
            var mac = macs[i].split(',')[0].trim();
            var isp = macs[i].split(',')[1].trim();
            insert_history_item(mac, isp);
        }
    }
