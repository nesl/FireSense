##FireSense

Camera Server
=========
The __camera server__ takes open/close events from door sensors in NESL and snaps camera pictures for the purpose of determining how many people entered or left the lab. Pictures are taken between open and close events from the door sensors. The attached cameras must each have an accessible url that can be used to grab the latest picture off the camera.

#### Table of Contents
- [Sensor Communication](#Sensor-Communication)
- [Data Storage](#Data-Storage)
- [Configuration](#Configuration)
- [Installation](#Installation)

Sensor Communication
---------
The camera server is a TCP server that receives and operates on messages from door sensors.
A door open / capture start message must use the following format:
```
[Camera_ID] Open
```
A door close / capture end message must use the following format:
```
[Camera_ID] Close
```
where _[Camera_ID]_ is the identifier for the camera as defined in *cameras* in **server.py**.

Data Storage
---------
Images are stored in the following manner:

- The root directory of all images is specified under __data_folder__ in server.cfg
- Under the root directory, images are further grouped by date (year-month-day)
- Under the date directories, images are finally grouped by open event time (hour-minute-seconds)

An example directory tree is as follows:

- Data_Folder
  - 2013-03-14
    - 09-11-12.345678
	  - cam_capture000.jpg
	  - cam_capture001.jpg
	  - cam_capture002.jpg
    - 10-32-67.543210
	  - cam_capture000.jpg
	  - cam_capture001.jpg
	  - cam_capture002.jpg
	  - cam_capture003.jpg

Configuration
---------
### Server.cfg ###
The following section details settings in **server.cfg** under the *[server]* header.

Name                 | Variable        | Type    | Description
-------------------- | --------------- | ------- | -----------
__Server Port__      | _port_          | integer | Indicates which port the camera server should serve on.
__Data Folder__      | _data_folder_   | string  | Location of the root data folder/directory for storage of images.
__Capture Interval__ | _interval_      | float   | Time interval in seconds between snapshots.
__Error Log File__   | _log_file_      | string  | Location of the file to be used for the error log. If not specified (or if variable removed), no error log will be generated.

### Cameras ###
Cameras can be added, removed, or edited in **server.py**.

In __server.py__, camera information is stored in the *cameras* dictionary.
Each dictionary entry is used to store the details of a different camera. Dictionary entries have the following format:
```python
'<Camera_ID>' : {'enable': False, 'url': '<Camera URL>'}
```

where Camera ID is the name the associated sensor will provide in its messages and Camera URL is the url link that always contains the most recent image taken from the camera. Camera IDs **cannot** contain spaces.

Installation
---------
1. Ensure python 1.6 or higher is installed.
2. Copy server.cfg and server.py into the camera server installation folder.
3. Fill in the details in server.cfg
4. Run server.py

Sensor installation must be done separately.