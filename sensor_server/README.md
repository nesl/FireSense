##FireSense

Sensor Server
=========
The __sensor server__ receives traffic summary packets from the firewall sensor and logs the files to the correct directory.

#### Table of Contents
- [Sensor Message Format](#sensor-message-format)
- [Data Storage](#data-storage)
- [Configuration](#configuration)
- [Installation](#installation)

Sensor Message Format
----
Data from the firewall sensor is expected to be in JSON format. The data must also have the minimum attributes based on the packet type.
Available packet types are:

- Router
- Peer
- Stream
- Event

The following table shows what JSON attributes need to be present for each packet type.

- Entries indicate an exact value for the attribute.
- Dashes (-) indicate no value is needed
- Checks (X) indicate that any value is valid

Attribute | Router   | Peer     | Stream   | Event
--------- | -------- | -------- | -------- | -----
Type      | Router   | Peer     | Stream   | -
Event     | Periodic | Periodic | Periodic | Event
LocalIP   | -        | X        | X        | X

Data Storage
----
 Data is stored in the following manner:

- The root directory of all data is specified under _data_folder_ in __server.cfg__
- Under the root directory, images are further grouped by date (year-month-day)
  - Note: A packet's date is determined by when the server received it, and can be different from the data's data. This is done to ensure that error packets are placed in the correct dated folder.
- Under the date directories sits:
  - The router log (router.txt)
  - The error log (ErrorLog.txt)
  - Folders for each Local IP received in a JSON
- Under the Local IP folders sit:
  - The peer log (peer.txt)
  - The stream log (stream.txt)
  - The event log (event.txt)

An example directory tree is as follows:

- Data_Folder
  - 2013-03-14
    - 192.168.1.10
	  - peer.txt
	  - stream.txt
	  - event.txt
    - 192.168.1.42
	  - peer.txt
	  - stream.txt
	  - event.txt
	- router.txt
	- ErrLog.txt

Configuration
----
The following section details the settings available in __server.cfg__ under the _[server]_ header.

Name                 | Variable        | Type    | Description
-------------------- | --------------- | ------- | -----------
__Server Port__      | _port_          | integer | Indicates which port the sensor server should serve on.
__Data Folder__      | _data_folder_   | string  | Location of the root data folder/directory for storage of data.

Installation
----
1. Ensure python 1.6 or higher is installed.
2. Copy server.cfg and server.py into the sensor server installation folder.
3. Fill in the details in server.cfg
4. Run server.py
