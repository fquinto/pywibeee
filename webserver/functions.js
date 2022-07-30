var specialchars = /^[-_@.\/\\ \w\s]+$/;

function getStatus(e) {
    var t = 0,
        n = !1;
    return window.XMLHttpRequest ? n = new XMLHttpRequest : window.ActiveXObject && (n = new ActiveXObject('Microsoft.XMLHTTP')),
        n && (n.onreadystatechange = function() {
            4 == n.readyState && 200 == n.status && (t = 1)
        }, e = e + '&id=' + Math.random(), n.open('GET', e, !1), n.send(null)),
        t
}

function loadXML(e) {
    return window.XMLHttpRequest ? xhttp = new XMLHttpRequest : xhttp = new ActiveXObject('Microsoft.XMLHTTP'),
        xhttp.open('GET', e, !1),
        xhttp.send(),
        xhttp.responseXML
}

function loadWithCallback(e, t) {
    window.XMLHttpRequest ? xmlhttp = new XMLHttpRequest : xmlhttp = new ActiveXObject('Microsoft.XMLHTTP'),
        e = e + '&id=' + Math.random(),
        xmlhttp.onreadystatechange = t,
        xmlhttp.open('GET', e, !0),
        xmlhttp.send()
}

function canvi_idioma() {
    var e = document.getElementById('idioma').value,
        t = !1;
    window.XMLHttpRequest ? t = new XMLHttpRequest : window.ActiveXObject && (t = new ActiveXObject('Microsoft.XMLHTTP')),
        t && (t.open('GET', '/canvi_idioma?idioma=' + e + '&id=' + Math.random(), !0), t.send(null), setInterval(function() {
            window.location = '/index.htm'
        }, 1000))
}

function configure_server() {
    var e = document.getElementById('serverIp').value,
        t = document.getElementById('serverPort').value,
        n = '';
    return '' == e || 0 == specialchars.test(e) ? (window.alert('You must enter Server URL or replace invalid characters (only alphanumeric, space and \\/.-_@)'), void(document.getElementById('loading_gif').style.display = 'none')) : isNaN(t) ? (alert('Error, please check the data entered'), void(document.getElementById('loading_gif').style.display = 'none')) : (3 == (n = (t = parseInt(t)).toString(16)).length && (n = '0' + n), 2 == n.length && (n = '00' + n), 1 == n.length && (n = '000' + n), 1 != getStatus('/configura_server?URLServidor=' + encodeURIComponent(e) + '&portServidor=' + n) ? (alert('Error, please check the data entered'), void(document.getElementById('loading_gif').style.display = 'none')) : void setTimeout(function() {
        reset_button()
    }, 300))
}

function n(e) {
    return e > 9 ? '' + e : '0' + e
}

function changepwd() {
    var e = document.getElementById('pwd1').value,
        t = document.getElementById('pwd2').value;
    if ('' == e || e.length < 4) return window.alert('Error, Password is empty or too short (minimum size 4).'),
        void(document.getElementById('loading_gif').style.display = 'none');
    if (e == t) {
        var n = '/config_value?ChangePwd=1&nPwd=' + encodeURIComponent(e);
        cond = getStatus(n),
            1 == cond && alert('Password have been changed.')
    } else alert('Passwords must match.')
}

function boto3() {
    var e = 0,
        t = document.getElementById('web_refresh').value;
    if (isNaN(t)) alert('Time error. Please, enter a number.');
    else {
        if ('' == document.getElementById('web_refresh').value || document.getElementById('web_refresh').value < 1 || document.getElementById('web_refresh').value > 10080) return alert('Time error. Valid values are from 1 to 10080 seconds.'), !1;
        e = getStatus('/web_refresh_value?web_refresh=' + document.getElementById('web_refresh').value);
        var n = document.getElementById('application_refresh').value;
        if (isNaN(n)) alert('Time error. Please, enter a number.');
        else if (-1 == document.getElementById('application_refresh').value || document.getElementById('application_refresh').value >= 1 && document.getElementById('application_refresh').value <= 60) {
            e = getStatus('/app_refresh_value?app_refresh=' + document.getElementById('application_refresh').value);
            var a = document.getElementById('hdatasave_refresh').value;
            if (isNaN(a)) alert('Time error. Please, enter a number.');
            else if (-1 == document.getElementById('hdatasave_refresh').value || document.getElementById('hdatasave_refresh').value >= 1 && document.getElementById('hdatasave_refresh').value <= 60) {
                if (e = getStatus('/hdata_save_value?hdatasave_refresh=' + document.getElementById('hdatasave_refresh').value), 'WGD' == model) {
                    var l = document.getElementById('wave_frequency').value;
                    if (isNaN(l)) return void alert('Frequency error. Please, enter a number.');
                    if (!(-1 == document.getElementById('wave_frequency').value || document.getElementById('wave_frequency').value >= 40 && document.getElementById('wave_frequency').value < 65000)) return void alert('Frequency error. Valid values are from 40 to 65000 Hz  (or -1 to stop).');
                    e = getStatus('/hdata_save_value?wave_frequency=' + document.getElementById('wave_frequency').value)
                }
                1 != e ? 0 != e || alert('Error, please check the fields and try again.') : alert('Data has been saved correctly.')
            } else alert('Time error. Valid values are from 1 to 60 minutes (or -1 to stop saving).')
        } else alert('Time error. Valid values are from 1 to 60 minutes (or -1 to stop sending).')
    }
}

function botoResetEnergy() {
    var e = getStatus('/resetEnergy?resetEn=1');
    1 != e ? 0 != e || alert('Error, please try again later.') : alert('Reset done.')
}

function botoReboot() {
    var e = getStatus('/config_value?reboot=1');
    1 != e ? 0 != e || alert('Error, please try again later.') : alert('Device has been rebooted successfully.\n\r Please wait.')
}

function boto44(e) {
    var t,
        n = /^[0-9.]*$/,
        a = document.getElementById('v1').value;
    if (n.test(a)) {
        if (t = '/calibratev?Calv4=1&RealVCalL1=' + a, 'WBM' != e) {
            var l = document.getElementById('v2').value,
                r = document.getElementById('v3').value;
            if (!n.test(l)) return void alert('Format error on v2. It is mandatory.');
            if (!n.test(r)) return void alert('Format error on v3. It is mandatory.');
            t += '&RealVCalL2=' + l + '&RealVCalL3=' + r
        }
        1 == getStatus(t) ? alert('Calibrated correctly.') : alert('Error, please try again.')
    } else alert('Format error on v1. It is mandatory.')
}

function boto54() {
    var e = document.getElementById('i1').value,
        t = document.getElementById('i2').value,
        n = document.getElementById('i3').value,
        a = /^[0-9.]*$/;
    a.test(e) ? a.test(t) ? a.test(n) ? 1 == getStatus('/calibratei?Cali4=1&RealICalL1=' + e + '&RealICalL2=' + t + '&RealICalL3=' + n) ? alert('Calibrated correctly.') : alert('Error, please try again.') : alert('Format error on L3. It is mandatory.') : alert('Format error on L2. It is mandatory.') : alert('Format error on L1. It is mandatory.')
}

function calibrateL(e) {
    var t = document.getElementById(e).value;
    if (/^[0-9.]*$/.test(t)) {
        var n,
            a = '';
        'i1' == e && (n = '/calibratei?Cali1=1&RealICalL1=' + t, a = 'L1'),
            'i2' == e && (n = '/calibratei?Cali2=1&RealICalL2=' + t, a = 'L2'),
            'i3' == e && (n = '/calibratei?Cali3=1&RealICalL3=' + t, a = 'L3'),
            1 == getStatus(n) ? alert(a + ' calibrated correctly.') : alert('Error, please try again.')
    } else alert('Format error on ' + e + '. It is mandatory.')
}

function accept_button() {
    document.getElementById('loading_gif').style.display = 'block';
    var e,
        t,
        n,
        a,
        l = document.getElementById('name'),
        r = document.getElementById('dhcp'),
        o = '/config_value?name=' + encodeURIComponent(l.value) + '&dhcp=' + r.checked,
        d = [
            'ip_intro',
            'gateway',
            'subnet',
            'dns1',
            'dns2'
        ],
        s = [
            '&ip=',
            '&gw=',
            '&subnet=',
            '&dns1=',
            '&dns2='
        ],
        c = /^([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){2}(\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$/;
    if ('' == l.value) return window.alert('Error, the Device Name is empty.'),
        void(document.getElementById('loading_gif').style.display = 'none');
    if (0 == /^[-_\w\s\d]+$/.test(l.value)) return window.alert('Error, invalid character in Device Name (only alphanumeric, space and -_'),
        void(document.getElementById('loading_gif').style.display = 'none');
    for (i = 0; i < 5; i++) {
        if (1 != c.test(document.getElementById(d[i]).value) && 'dns2' != document.getElementById(d[i]).getAttribute('id')) return window.alert('Error, please check the data entered'),
            void(document.getElementById('loading_gif').style.display = 'none');
        if (data = document.getElementById(d[i]).value.split('.'), e = parseInt(data[0], 10), t = parseInt(data[1], 10), n = parseInt(data[2], 10), a = parseInt(data[3], 10), e > 255 || t > 255 || n > 255 || a > 255) return window.alert('Error, please check the data entered'),
            void(document.getElementById('loading_gif').style.display = 'none');
        string = (e < 16 ? '0' : '') + e.toString(16) + (t < 16 ? '0' : '') + t.toString(16) + (n < 16 ? '0' : '') + n.toString(16) + (a < 16 ? '0' : '') + a.toString(16),
            o += s[i] + string
    }
    return cond = getStatus(o),
        1 == cond ? void setTimeout(function() {
            wifi_button()
        }, 300) : (alert('Connection error. Please try again.'), void(document.getElementById('loading_gif').style.display = 'none'))
}
var estat = 0;

function wifi_button() {
    estat++;
    var e,
        t = document.getElementById('ssid').value,
        n = document.getElementById('keyText').value,
        a = document.getElementById('typekeycombo').value,
        l = document.getElementById('securitycombo').value,
        r = [
            '5',
            '13',
            '8'
        ];
    if ('' == n && 0 != l) return window.alert('Error, empty Key field.'),
        document.getElementById('loading_gif').style.display = 'none',
        void(estat = 0);
    if ('' == t || '-1' == t) return alert('You must select a valid SSID.'),
        document.getElementById('loading_gif').style.display = 'none',
        void(estat = 0);
    if ('99' == t) {
        if ('' == document.getElementById('ssidhidden').value) return window.alert('You must enter wifi SSID.'),
            document.getElementById('loading_gif').style.display = 'none',
            void(estat = 0);
        t = document.getElementById('ssidhidden').value
    }
    if (1 == a && 0 == /^[0-9A-F]*$/.test(n)) return alert('Key is not HEX'),
        document.getElementById('loading_gif').style.display = 'none',
        void(estat = 0);
    if (2 == l || 1 == l) {
        if (1 == a && n.length != 2 * r[l - 1]) return alert('The key must be exactly ' + 2 * r[l - 1] + ' hexadecimal characters.'),
            document.getElementById('loading_gif').style.display = 'none',
            void(estat = 0);
        if (2 == a && n.length != r[l - 1]) return alert('The key must be exactly ' + r[l - 1] + ' characters. Click on Advanced Options menu to check your Security type selection (WEP 64 BITS or WEP 128 BITS) and Password format(PASS PHRASE or HEX KEY)'),
            document.getElementById('loading_gif').style.display = 'none',
            void(estat = 0)
    } else if (l > 2 && n.length < 8) return alert('The key must be bigger than 8 characters.'),
        document.getElementById('loading_gif').style.display = 'none',
        void(estat = 0);
    1 == estat ? (e = '/config_value?ssid=' + encodeURIComponent(t) + '&security=' + document.getElementById('securitycombo').value + '&typekey=' + document.getElementById('typekeycombo').value, cond = getStatus(e), 1 == cond ? wifi_button() : 0 == cond && (alert('Connection error. Please try again.'), document.getElementById('loading_gif').style.display = 'none', estat = 0)) : 2 == estat && (e = '/config_value?pass=' + encodeURIComponent(document.getElementById('keyText').value), cond = getStatus(e), 1 == cond ? setTimeout(function() {
        configure_server()
    }, 300) : (alert('Error. Please try again.'), document.getElementById('loading_gif').style.display = 'none'), estat = 0)
}

function selectWifi() {
    var e = new Object,
        t = (e = document.getElementById('ssid')).options[e.selectedIndex].id.split('|¬');
    if (-1 != t[0].indexOf('^invalid_SSID')) return alert('This SSID is not valid for the device configuration.'),
        document.getElementById('ssid').selectedIndex = '0', !1;
    var n = parseInt(t[1]),
        a = 0;
    switch (document.getElementById('ssidhiddenrow').style.display = 'none', n) {
        case 0:
            break;
        case 1:
            a = 2;
            break;
        case 5:
            a = 3;
            break;
        case 9:
        case 13:
            a = 4
    }
    switch (e.value) {
        case '-1':
            a = 0;
            break;
        case '99':
            document.getElementById('ssidhiddenrow').style.display = 'table-row',
                a = 3
    }
    document.getElementById('securitycombo').selectedIndex = a
}

function reset_button() {
    1 == getStatus('/config_value?reset=true') ? (document.getElementById('loading_gif').style.display = 'none', alert('Configuration successful.\n\r Wibeee will be rebooting during few seconds.\n\r Please wait.')) : alert('Error. Please try again.')
}

function newUpdate() {
    var e = loadXML('status.xml?rnd=' + Math.random()),
        t = 'fase' + document.getElementById('id_fase').value,
        n = e.getElementsByTagName('time')[0].childNodes[0].nodeValue,
        a = (new Date).getTime();
    if (1000 * n > a - 86400000 && 1000 * n < a + 86400000) {
        var l,
            r = new Date(1000 * n),
            o = r.getFullYear(),
            d = ('0' + (r.getMonth() + 1)).slice(-2);
        l = ('0' + r.getDate()).slice(-2) + '/' + d + '/' + o + '  ' + r.getHours() + ':' + ('0' + r.getMinutes()).slice(-2) + ':' + ('0' + r.getSeconds()).slice(-2)
    } else l = '-';
    'WGD' == model && (document.getElementById('ground').innerHTML = e.getElementsByTagName('ground')[0].childNodes[0].nodeValue),
        document.getElementById('time').innerHTML = l,
        document.getElementById('vrms').innerHTML = e.getElementsByTagName(t + '_vrms')[0].childNodes[0].nodeValue + ' V',
        document.getElementById('irms').innerHTML = e.getElementsByTagName(t + '_irms')[0].childNodes[0].nodeValue + ' A',
        document.getElementById('p_aparent').innerHTML = e.getElementsByTagName(t + '_p_aparent')[0].childNodes[0].nodeValue + ' VA',
        document.getElementById('p_activa').innerHTML = e.getElementsByTagName(t + '_p_activa')[0].childNodes[0].nodeValue + ' W',
        document.getElementById('p_reactiva_ind').innerHTML = e.getElementsByTagName(t + '_p_reactiva_ind')[0].childNodes[0].nodeValue + ' VArL',
        document.getElementById('p_reactiva_cap').innerHTML = e.getElementsByTagName(t + '_p_reactiva_cap')[0].childNodes[0].nodeValue + ' VArC',
        document.getElementById('frecuencia').innerHTML = e.getElementsByTagName(t + '_frecuencia')[0].childNodes[0].nodeValue + ' Hz',
        document.getElementById('factor_potencia').innerHTML = e.getElementsByTagName(t + '_factor_potencia')[0].childNodes[0].nodeValue,
        document.getElementById('energia_activa').innerHTML = e.getElementsByTagName(t + '_energia_activa')[0].childNodes[0].nodeValue + ' Wh',
        document.getElementById('energia_reactiva_ind').innerHTML = e.getElementsByTagName(t + '_energia_reactiva_ind')[0].childNodes[0].nodeValue + ' VArLh',
        document.getElementById('energia_reactiva_cap').innerHTML = e.getElementsByTagName(t + '_energia_reactiva_cap')[0].childNodes[0].nodeValue + ' VArCh';
    try {
        document.getElementById('thd').innerHTML = e.getElementsByTagName(t + '_thd_total')[0].childNodes[0].nodeValue + ' %',
            document.getElementById('harmonic_fund').innerHTML = e.getElementsByTagName(t + '_thd_fund')[0].childNodes[0].nodeValue + ' A',
            document.getElementById('harmonic_3').innerHTML = e.getElementsByTagName(t + '_thd_ar3')[0].childNodes[0].nodeValue + ' A',
            document.getElementById('harmonic_5').innerHTML = e.getElementsByTagName(t + '_thd_ar5')[0].childNodes[0].nodeValue + ' A',
            document.getElementById('harmonic_7').innerHTML = e.getElementsByTagName(t + '_thd_ar7')[0].childNodes[0].nodeValue + ' A',
            document.getElementById('harmonic_9').innerHTML = e.getElementsByTagName(t + '_thd_ar9')[0].childNodes[0].nodeValue + ' A',
            document.getElementById('thdV').innerHTML = e.getElementsByTagName(t + '_thd_tot_V')[0].childNodes[0].nodeValue + ' %',
            document.getElementById('harmonic_fundV').innerHTML = e.getElementsByTagName(t + '_thd_fun_V')[0].childNodes[0].nodeValue + ' V',
            document.getElementById('harmonic_3V').innerHTML = e.getElementsByTagName(t + '_thd_ar3_V')[0].childNodes[0].nodeValue + ' V',
            document.getElementById('harmonic_5V').innerHTML = e.getElementsByTagName(t + '_thd_ar5_V')[0].childNodes[0].nodeValue + ' V',
            document.getElementById('harmonic_7V').innerHTML = e.getElementsByTagName(t + '_thd_ar7_V')[0].childNodes[0].nodeValue + ' V',
            document.getElementById('harmonic_9V').innerHTML = e.getElementsByTagName(t + '_thd_ar9_V')[0].childNodes[0].nodeValue + ' V'
    } catch (e) {}
}

function controlRescan() {
    if ('4' == document.getElementById('network_type').value) {
        if (1 == getStatus('/config_value?softaprescan=true')) {
            document.getElementById('loading_gif').style.display = 'none',
                alert('Wi-Fi connection will be rebooted to complete the scan, in about 20 seconds page will refresh automatically. \n\rIf the page doesn\'t load automatically please check your wifi connection.'),
                resetSelectSSID(),
                document.getElementById('mensaje').innerHTML = '',
                document.getElementById('mensaje').innerHTML = 'Searching';
            var e = document.createElement('div');
            e.className += 'overlay',
                document.body.appendChild(e),
                document.body.style.cursor = 'wait',
                setTimeout('document.location.reload()', 10000)
        } else alert('Error. Please try again.')
    } else resetSelectSSID(),
        rescanNetwork(0),
        selectWifi()
}

function rescanNetwork(e) {
    var t = '/scan.cgi?scan=1';
    document.getElementById('mensaje').innerHTML = '',
        document.getElementById('mensaje').innerHTML = 'Searching',
        loadWithCallback(t, function() {
            if (4 == xmlhttp.readyState && 200 == xmlhttp.status)
                if (1 == getStatus('/scan.cgi?getAllBss')) t = '/scanallresults.xml?rnd=' + Math.random(),
                    (xmlDoc = loadXML(t)) && updateWifis(xmlDoc);
                else if (e < 3) rescanNetwork(e + 1);
            else if (e >= 3) return void alert('Scanning has failed , please try again.')
        })
}

function updateWifis(e) {
    for (x = e.getElementsByTagName('bss'), y = e.getElementsByTagName('ssid')[0].childNodes[0].nodeValue, i = 0; i < x.length; i++) '1' == x[i].childNodes[0].childNodes[0].nodeValue && (x[i].childNodes[1].childNodes[0].nodeValue == y ? addWifi(x[i].childNodes[1].childNodes[0].nodeValue, x[i].childNodes[2].childNodes[0].nodeValue, x[i].childNodes[3].childNodes[0].nodeValue, '1') : addWifi(x[i].childNodes[1].childNodes[0].nodeValue, x[i].childNodes[2].childNodes[0].nodeValue, x[i].childNodes[3].childNodes[0].nodeValue, '0'));
    document.getElementById('mensaje').innerHTML = '',
        document.getElementById('mensaje').innerHTML = '<a onclick=\'controlRescan();\'>Rescan</a>',
        selectWifi()
}

function addWifi(e, t, n, a) {
    var l = new Object;
    l = document.getElementById('ssid');
    var r = document.createElement('option');
    r.setAttribute('id', e + '|¬' + t + '|¬' + n),
        r.setAttribute('value', e),
        1 == a && r.setAttribute('selected', 'selected'),
        r.text = e;
    try {
        l.add(r, r.options.null)
    } catch (e) {
        l.add(r, null)
    }
}

function resetSelectSSID() {
    var e = document.createElement('option');
    e.text = 'Choose a network...',
        e.value = '-1',
        e.id = '',
        e.selected = 'selected';
    var t = document.createElement('option');
    t.text = 'Other...',
        t.value = '99',
        t.id = 'other#5#1#1',
        document.getElementById('ssid').options.length = 0,
        document.getElementById('ssid').add(e),
        document.getElementById('ssid').add(t)
}

function sendCableSection() {
    var e = document.getElementById('cablesec').value;
    1 == getStatus('/section?Section=' + e) ? alert('Cable section changed to value: ' + e) : alert('Error with cable section, please try again.')
}

function sendPhasesSequence() {
    var e = document.getElementById('phases_sequence_wbb').value;
    1 == getStatus('/config_value?phases_sequence=' + e) ? alert('Phase Sequence changed to value: ' + e) : alert('Error with Phase Sequence, please try again.')
}

function sendWiringConnection() {
    var e = document.getElementById('wiring_connection').value;
    1 == getStatus('/wiring_connection?wiring_connection=' + e) ? '3' == e ? alert('Connection Type changed. Note that, in this configuration, voltage measurements represent the phase voltage values (Vrms phase-phase)') : '0' == e ? alert('Choose a valid Connection Type') : alert('Connection Type changed. Note that, in this configuration, voltage measurements represent the phase voltage values (Vrms phase-neutral)') : alert('Error with Connection Type, please try again.')
}

function loadPhases(e) {
    if ('WBB' == e) {
        var t = (i = (d = document.getElementById('phases')).insertRow(0)).insertCell(0),
            n = i.insertCell(1);
        t.innerHTML = '<a href=\'phase1.html\'>Circuit 1</a>',
            t.className = 'td_left',
            n.innerHTML = '<a href=\'phase1.html\'>></a>',
            n.className = 'td_right';
        var a = (s = d.insertRow(1)).insertCell(0),
            l = s.insertCell(1);
        a.innerHTML = '<a href=\'phase2.html\'>Circuit 2</a>',
            a.className = 'td_left',
            l.innerHTML = '<a href=\'phase2.html\'>></a>',
            l.className = 'td_right';
        var r = (c = d.insertRow(2)).insertCell(0),
            o = c.insertCell(1);
        return r.innerHTML = '<a href=\'phase3.html\'>Circuit 3</a>',
            r.className = 'td_left',
            o.innerHTML = '<a href=\'phase3.html\'>></a>',
            void(o.className = 'td_right')
    }
    var d,
        i;
    t = (i = (d = document.getElementById('phases')).insertRow(0)).insertCell(0),
        n = i.insertCell(1);
    if (t.innerHTML = 'WGD' == e ? '<a href=\'phase1.html\'>Ground Measurement</a>' : '<a href=\'phase1.html\'>Phase 1</a>', t.className = 'td_left', n.innerHTML = '<a href=\'phase1.html\'>></a>', n.className = 'td_right', 'WBM' != e && 'WBP' != e && 'WGD' != e) {
        var s;
        a = (s = d.insertRow(1)).insertCell(0),
            l = s.insertCell(1);
        a.innerHTML = '<a href=\'phase2.html\'>Phase 2</a>',
            a.className = 'td_left',
            l.innerHTML = '<a href=\'phase2.html\'>></a>',
            l.className = 'td_right';
        var c;
        r = (c = d.insertRow(2)).insertCell(0),
            o = c.insertCell(1);
        r.innerHTML = '<a href=\'phase3.html\'>Phase 3</a>',
            r.className = 'td_left',
            o.innerHTML = '<a href=\'phase3.html\'>></a>',
            o.className = 'td_right'
    }
}

function dafaultButton() {
    1 == getStatus('/calibratei?resettofactorycal=1') ? (alert('Factory calibration loaded.'), location.reload()) : alert('Error, please try again.')
}

function switchPlug() {
    var e,
        t = '/coilSet?coilSet=1&coil';
    document.getElementById('plugControl').checked ? (t += 'On=1', e = !0) : (t += 'Off=1', e = !1),
        1 == getStatus(t) ? e ? alert('Devices connected to WibeeePlug have been started.') : alert('Devices connected to WibeeePlug have been stopped.') : alert('Error, please try again.')
}