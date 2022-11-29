# Bean Drop Processing Center
The Bean Drop Processing Center is a user interface designed for use in the daily operation of Bean Drop by Bean Drop employees. It allows employees to access all required functions and actions in the Bean Drop process cycle and link them to the main database. The software interacts with various compliments of hardware including, rfid scanners, rfid multiplexers, camera modules (normal, IR and Thermal). It is designed to be run on custom hardware setups which can be both fixed or portable solutions.




The main file to run is named: 'Admin_server_functions.py'. This is normally executed by an executable file deployed outside of the project folders. All other files supliment and help run 'Admin_server_functions.py'. Code makes used of class based OOP throughout.

# Functions
- Admin controls and functions over main Bean Drop database. Conducting daily transactions and operations for internal Bean Drop operation.
- Scan RFID's using both single scanners and multiplexing scanners
- RFID Multiplex Scanner linked with MQTT protocol
- Resizing of GUI windows depending upon screen size
- Advanced Tkinter / GUI design to allow for intuative/easy daily use by employees who have not been trained on each an every function distinctly. 

### Example Portable Design Image Below
![image](https://user-images.githubusercontent.com/60620955/204510735-b71cee1e-8138-4706-84c2-af9c48ac1aa4.png)

# Python Libraries / Software
- collections.abc
- cv2
- datetime
- json
- logging
- math
- matplotlib
- multiprocessing
- mysql.connector
- numpy
- os
- paho.mqtt.client
- passlib.context
- PIL
- queue
- RPi.GPIO
- sqlite3
- subprocess
- sys
- _thread
- time
- tkinter
- traceback

# Hidden Functions / Code
- Connect_functions.py has a significant number of functions removed/hidden as part of commercial security as they access the Bean Drop production database. The connect_functions.py uses a class named 'server_connection_details' to access our mySQL database based on the Google clound using the mysql.connector library and SSL connection protocols. 10 / 61 class based methods are shown in the code as examples, however even amoungst the examples shown, table/column names have been changes / retracted as part of commercial security. 'XXX' is often used to replace names in the code.
- Admin_server_functions.py has a significant number of functions removed/hidden as part of commercial security. Significantly a large number of the class based Tkinter Frames have been removed/hidden.  A number of Example frames have already been provided and represent the same quality of code in the hidden frames. 9/29 tkinter class based Frames are shown, the rest have been removed as part of commercial security. These hidden frames are shown to be operational here:
- .gitignore is setup to not track files within certs folder


User interface for all database functions involved in Bean Drop Process Cycle. Software linked to hardware connections of a rfid scanner, rfid multiplexer, camera modules.
