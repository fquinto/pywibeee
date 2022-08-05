# ESTABLECER RED

       c0a8011e = 192.168.1.30
       c0a80101 = 192.168.1.1
       08080808 = 8.8.8.8
       08080404 = 8.8.4.4

       curl 'http://192.168.1.150/config_value?name=WIBEEE&dhcp=false&ip=c0a8011e&gw=c0a80101&subnet=ffffff00&dns1=08080808&dns2=08080404&id=0.4281428711978198' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Referer: http://192.168.1.150/en/index.html'

       curl 'http://192.168.1.150/config_value?gw=c0a80101&subnet=ffffff00&dns2=08080404&ip=c0a8011e&dns1=08080808&name=WIBEEE&id=0.8&dhcp=false' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Referer: http://192.168.1.150/en/index.html'

Ip = 192.168.1.30

       http -v http://192.168.1.150/config_value?name=WIBEEE&dhcp=false&ip=c0a8011e&gw=c0a80101&subnet=ffffff00&dns1=08080808&dns2=08080404

Ip = 192.168.0.1

       http -v http://192.168.1.150/config_value?name=WIBEEE&dhcp=false&ip=c0a80001&gw=c0a80101&subnet=ffffff00&dns1=08080808&dns2=08080404

SETUP DNS 1 a IP 8.8.8.8
       http -v http://192.168.1.150/config_value?dns1=08080808

# ESTABLECER WIFI SSID

Security: 0 = abierto     y   5 = WPA2

       curl 'http://192.168.1.150/config_value?ssid=yourwifinetwork&security=5&typekey=2&id=0.7332966499446105' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Referer: http://192.168.1.150/en/index.html'

       curl 'http://192.168.1.150/config_value?security=0&typekey=2&id=0.5&ssid=yourwifinetwork' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Referer: http://192.168.1.150/en/index.html'

       http -v http://192.168.0.1/config_value?ssid=yourwifinetwork&security=5&typekey=2

# ESTABLECER WIFI PASS

       curl 'http://192.168.1.150/config_value?pass=12345678&id=0.022384919271379755' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Referer: http://192.168.1.150/en/index.html'

       curl 'http://192.168.1.150/config_value?pass=12345678&id=0.6' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Referer: http://192.168.1.150/en/index.html'

       http -v http://192.168.0.1/config_value?pass=12345678

# ESTABLECER SERVIDOR

NOTA: Son valores en HEX: el 2198 es en realidad el 8600 (DEC)

## FORMA 1

       curl 'http://192.168.1.150/configura_server?URLServidor=wattius.mirubee.com&portServidor=2198&id=0.12399868601518238' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Referer: http://192.168.1.150/en/index.html'

## FORMA 2

       curl 'http://192.168.1.150/configura_server?ipServidor=wattius.mirubee.com&URLServidor=wattius.mirubee.com&portServidor=2198&id=0.7' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Referer: http://192.168.1.150/en/index.html'

ip = 192.168.1.50
port = 50 hex = 80 dec

       http -v http://192.168.1.150/configura_server?ipServidor=192.168.1.50&URLServidor=192.168.1.50&portServidor=0050

       http -v http://192.168.0.1/configura_server?ipServidor=192.168.1.50&URLServidor=192.168.1.50&portServidor=0050

port = 2198 hex = 8600 dec
ip = 192.168.0.1

       http -v http://192.168.0.1/configura_server?ipServidor=192.168.1.50&URLServidor=192.168.1.50&portServidor=2198

port = 2198 hex = 8600 dec
ip = 192.168.1.30

       http -v http://192.168.1.30/configura_server?ipServidor=192.168.1.50&URLServidor=192.168.1.50&portServidor=2198

# REFRESCO

NOTA: Valid values are from 1 to 10080 seconds.
measuresRefresh

       curl 'http://192.168.1.150/web_refresh_value?web_refresh=600'

NOTA: valores validos from 1 to 60 (or -1 to stop sending)

       curl 'http://192.168.1.150/app_refresh_value?app_refresh=10'

NOTA: valores validos from 1 to 60 (or -1 to stop sending)

       curl 'http://192.168.1.150/hdata_save_value?hdatasave_refresh=10'

NOTA: Frequency valid values are from 40 to 65000 Hz  (or -1 to stop).

       curl 'http://192.168.1.150/hdata_save_value?wave_frequency=50'

       http -v http://192.168.1.150/web_refresh_value?web_refresh=600
       http -v http://192.168.1.150/app_refresh_value?app_refresh=10
       http -v http://192.168.1.150/hdata_save_value?hdatasave_refresh=10

       http -v http://192.168.0.1/web_refresh_value?web_refresh=6
       http -v http://192.168.0.1/app_refresh_value?app_refresh=-1
       http -v http://192.168.0.1/hdata_save_value?hdatasave_refresh=-1
       http -v http://192.168.0.1/hdata_save_value?wave_frequency=50

# Parar scanner

       http -v http://192.168.1.150/config_value?softaprescan=false

# VER VARIABLES

       http -v http://192.168.1.150/services/user/values.xml?id=WIBEEE
       http -v http://192.168.1.150/services/user/values.xml?id=WIBEEE.phasesSequence
       http -v http://192.168.1.150/services/user/values.xml?id=WIBEEE.model
       http -v http://192.168.1.150/services/user/values.xml?id=WIBEEE.macAddr
       http -v http://192.168.1.150/services/user/harmonics.xml?id=WIBEEE

# RESET

       curl 'http://192.168.1.150/config_value?reset=true&id=0.29530562759822854' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Referer: http://192.168.1.150/en/index.html'

       http -v http://192.168.1.150/config_value?reset=true

# REBOOT

       http -v http://192.168.0.1/config_value?reboot=1

# Establecer 3 phases medidoras

       curl 'http://192.168.0.1/wiring_connection?wiring_connection=3&id=0.4571727516576659' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Referer: http://192.168.0.1/en/index.html' -H 'Cookie: uid=0fEsJHjv8Z'

# STATUS

       http -v http://192.168.0.1:80/en/status.xml
