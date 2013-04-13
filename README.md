FireSense
=========

Firewall-based IP traffic sensor for use on pfsense

Project Sections
----

- Sensor
- Sensor Server
- Camera Server

The following sections are descriptions of the project sections

Sensor
----
This section contains code run on the pfsense firewall.

The sensor grabs ip traffic going through the firewall, processes it, and sends information to the sensor server.

Sensor Server
----
This section contains code run on the vm server that retrieves information from the server.

The sensor server receives data from the server and stores it into a specific directory structure for later processing.

Camera Server
----
This section contains code run on the vm server that operates the camera for ground truth determination.

The camera server receives open/close event notifications from the door sensors and takes camera shots to determine how many people are entering/leaving the lab.