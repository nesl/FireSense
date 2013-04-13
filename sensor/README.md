##FireSense

Sensor
=========
The __sensor__ monitors ip traffic through the pfsense firewall and reports events and periodic summaries to the __sensor server__.

#### Table of Contents
- [Operating Principles](#Operating-Principles)
- [Configuration](#Configuration)
- [Starting the Sensor](#Starting-the-Sensor)
- [Installation](#Installation)

Operating Principles
----
The sensor incorporates both a python program and tshark. Tshark is used to acquire and process ip information, which is then fed to the python program for further processing. Finally, events and periodic summary data are sent to the sensor server.

Due to the discrepancy between input/output rates in tshark, it is possible for tshark to crash when data comes in too quickly. For this reason, __capture.sh__ contains an infinite loop that will restart the sensor when either tshark or the sensor crashes.

Configuration
----
There are two tshark scripts: __port_tshark.sh__ and __tshark.sh__. 

* tshark.sh captures all tcp and udp packets going through the firewall
* port_tshark.sh captures tcp packets going through the firewall using specific ports

To pick one script verses another, edit the script call in __capture.sh__.

### Editing the Capture Filter
The capture filter is used in __port_tshark.sh__ and lists the ports that tshark will process. To update the list, add or remove port numbers from the _CAPTURE\_FILTER_ variable.

### Choosing the Input Interface
Tshark will usually default to the WAN interface of the pfsense firewall. To specify your own interface (e.g. LAN) or if tshark does not choose the correct interface, add the `-i #' option to the tshark call in either _tshark.sh_ or _port_tshark.sh_ where # is the number associated with the interface.

To see the available interfaces and associated numbers, use the command: `tshark -D`

### Config.cfg Options
#### Reporting Intervals
Reporting intervals are listed in __config.cfg__ under the _intervals_ tag. They dictate how much time passes between each periodic update.

[intervals] | Variable        | Type    | Description
----------- | --------------- | ------- | -----------
Router      | router_interval | integer | Time (in seconds) to wait before sending another router-level summary
Peer        | peer_interval   | integer | Time (in seconds) to wait before sending another peer-level summary
Stream      | stream_interval | integer | Time (in seconds) to wait before sending another stream-level summary

#### Server Details
Server details are listed in __config.cfg__ under the _server_ tag. These settings allow the sensor to communicate with the sensor server.

[server]         | Variable | Type    | Description
---------------- | -------- | ------- | -----------
Server (Host) IP | host     | string  | Sensor server IP address
Server Port      | port     | integer | Sensor server port number

#### Timeout Details
Timeouts are listed in __config.cfg__ under the _timeouts_ tag. They determine how long the sensor will wait before taking certain actions.

[timeouts]            | Variable | Type    | Description
--------------------- | -------- | ------- | -----------
Peer Timeout          | peer     | integer | Inactivity period (in seconds) to wait before autmatically removing a peer
Stream Timeout        | stream   | integer | Inactivity period (in seconds) to wait before automatically closing a stream
Input (Reset) Timeout | input    | integer | Inactivity period (in seconds) to wait without input before terminating the program

#### Filter Details
Filters are listed in __config.cfg__ under the _filters_ tag. Currently, there is only one filter: local_ip. This filter is a list of regular expressions that determine what should be considered a local ip address. Multiple addresses regular expressions can be used if they are separated by a comma (,). If multiple regular expressions are used, any ip matching at least one regular expression will be considered a local ip address.

[filters]            | Variable | Type    | Description
-------------------- | -------- | ------- | -----------
Local IP Regex List  | local_ip | integer | List of regular expressions whose matches indicate a local ip address

Starting the Sensor
----
To start the sensor, navigate to the installation folder and run capture.sh: `./capture.sh`

Installation
----
A note on uploading files to the pfsense box:

- Files can be uploaded onto the pfsense box by using the _command line_ utility under the _Diagnostic Tools_ option of the firewall webgui.
- Use the file browser to find a file on your computer to upload onto the pfsense box.
- Uploading is complete when the browser shows it is no longer loading/busy. Do not navigate away or touch any on-screen buttons during this time.
- Uploaded files will show up in the __/tmp__ directory in the pfsense box.

1. Connect to the pfsense through the serial port. You may need a serial male/female converter and a serial/usb converter.
2. On the initial menu, enter command `8` (Shell) to get to the linux shell.
3. Enable filesystem writes through the serial port: `sudo /etc/rc.conf_mount_rw`
4. Enable filesystem writes on startup:
   a. Navigate to the "Run on startup" directory: `cd /usr/local/etc/rc.d/`
   b. Create a script that will run the write enable command on startup: `sudo echo /etc/rc.conf_mount_rw > rw.sh`
   c. Assign executable permissions to the new file: `chmod +x rw.sh`
5. Install python: `pkg_add -r ftp://ftp-archive.freebsd.org/pub/FreeBSD-Archive/ports/i386/packages-8.1-release/Latest/tshark.tbz`
   * If the installation fails due to missing files (libasn1.so.10, libgssapi.so.10, libheimntlm.so.10, etc), the files can be downloaded from the web:
     ```bash
     cd /usr/local/lib/ && fetch http://e-sac.siteseguro.ws/pfsense/8/All/ldd/libasn1.so.10
     cd /usr/local/lib/ && fetch http://e-sac.siteseguro.ws/pfsense/8/All/ldd/libgssapi.so.10
     cd /usr/local/lib/ && fetch http://e-sac.siteseguro.ws/pfsense/8/All/ldd/libheimntlm.so.10
     cd /usr/local/lib/ && fetch http://e-sac.siteseguro.ws/pfsense/8/All/ldd/libhx509.so.10
     cd /usr/local/lib/ && fetch http://e-sac.siteseguro.ws/pfsense/8/All/ldd/libkrb5.so.10
     cd /usr/local/lib/ && fetch http://e-sac.siteseguro.ws/pfsense/8/All/ldd/libroken.so.10
	 # Alternatively, take the files from missing_libs.tbz (which must be downloaded as mentioned above)*
     cd /tmp && tar xf missing_libs.tbz
	 cd /usr/local/lib/ && cp /tmp/missing_libs/* .
	 # Then set the permissions for the files
     chmod 0755 /usr/local/lib/libasn1.so.10
     chmod 0755 /usr/local/lib/libgssapi.so.10
     chmod 0755 /usr/local/lib/libheimntlm.so.10
     chmod 0755 /usr/local/lib/libhx509.so.10
     chmod 0755 /usr/local/lib/libkrb5.so.10
     chmod 0755 /usr/local/lib/libroken.so.10
	 ```
6. Navigate to the install directory
7. Upload sensor.tbz and move it into the installation directory `mv /tmp/sensor.tbz install_dir`
8. Untar sensor.tbz\* `tar xf sensor.tbz`
9. Go to the sensor directory `cd sensor`
0. Initialize the settings (see [Configuration](#Configuration) above)
1. Start the sensor `./capture.sh`

\* Note: If tar does not work, individual files will have to be uploaded onto the pfsense box instead.