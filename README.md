FireSense
=========

Firewall-based IP traffic sensor for use on pfsense

Project Sections
---------
* Sensor
* Sensor Server
* Camera Server

The following sections are descriptions of the project sections.

Sensor
--------
This section refers to the code that is run on the pfsense firewall.

The sensor grabs ip traffic through the firewall, processes it, and sends information to the sensor server.

Senser Server
--------
This section refers to the code that is run on the vm server and communicates with the sensor.

The sensor server receives information from the sensor and stores it in a specific directory/file structure.

Camera Server
--------
This section refers to the code that is run on the vm server and handles the camera-based ground truth retrieval.

The camera server receives open/close event notifications from the door sensors and takes camera shots to learn how many people are entering/leaving the lab.
