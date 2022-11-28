# Bean Drop Processing Center
The Bean Drop Processing Center is a user interface designed for use in the daily operation of Bean Drop by Bean Drop employees. It allows employees to access all required functions and actions in the Bean Drop process cycle and link them to the main database. The software interacts with various compliments of hardware including, rfid scanners, rfid multiplexers, thermal printers, camera modules (normal, IR and Thermal). It is designed to be run on custom hardware setups which can be both fixed or portable solutions.

# Functions

# Python Libraries / Software
- Tkinter
- 

# Hidden Functions / Code
- Connect_functions.py has a significant number of functions removed/hidden as part of commercial security as they access the Bean Drop production database. The connect_functions.py uses a class named 'server_connection_details' to access our mySQL database based on the Google clound using the mysql.connector library and SSL connection protocols. 10 / 61 class based methods are shown in the code as examples, however even amoungst the examples shown, table/column names have been changes / retracted as part of commercial security. 'XXX' is often used to replace names in the code.
- 5 / ???? methods within the '' class are shown, the rest have been removed to limit database naming conventions being revealed.
- .gitignore is setup to not track files within certs folder
User interface for all database functions involved in Bean Drop Process Cycle. Software linked to hardware connections of a thermal printer, rfid scanner, rfid multiplexer, camera modules.
