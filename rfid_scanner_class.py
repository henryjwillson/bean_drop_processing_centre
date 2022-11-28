# class to control RFID scanner
import subprocess
from subprocess import Popen, PIPE
import time
import datetime

class rfid_scanner():
	
	def __init__(self, rfid_status, scanning_status, scanning_operation):		#rfid status determines if the rfid is on (can be used to manually restart rfid program), scanning status determines if the gui is still looking to scan new cups
		self.rfid_status = rfid_status
		self.scanning_status = scanning_status
		self.scanning_operation = scanning_operation
		
	def auto_polling(self, pipe):
		# use Popen class instead of run class as Popen class returns standard output as a live feed whereas run class returns standard output only at the end of the process
		p1 = subprocess.Popen(["./rfidb1-tool /dev/ttyS0 poll"],
									cwd="/home/pi/rfidb1-tool_v1.1", shell=True, stdout= subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		try:
			print(p1.stdout.decode())  # capure_output=True takes the response normally returned to console and returns it to the variable instead. stdout = standard output # .decode() method passes result out as a string eg. print(p1.stdout.decode())
		except Exception as error:
			print(error)
			
		while self.rfid_status == True:
			#print(self.rfid_status)
			#time.sleep(0.1)
			while self.scanning_status == True:
				global global_dicitonary_numbers	#I believe this is one of my bodges...
				
				try:
					value =  p1.stdout.readline()
					print("Final decode is: ",value)
					print(value[10:17])
					#print(p1.stdout.decode()) # capure_output=True takes the response normally returned to console and returns it to the variable instead. stdout = standard output # .decode() method passes result out as a string eg. print(p1.stdout.decode())
					if value[10:17] == "NTAG213":
						print("correct tag type is found...", value)
						rfid_size = p1.stdout.readline()
						rfid_uid = p1.stdout.readline()
						print("first rfid size call...", rfid_size)
						print("first rfid uid call...", rfid_uid)
						print("formatted rfid uid call...", rfid_uid[5:20])
						formatted_rfid_uid = rfid_uid[5:20]
						pipe.send(formatted_rfid_uid)
						#decoded_rfid_queue.put(decoded_cup_RFID)			#currently this just updates the screen i believe
				except Exception as error:
					print(error)
					pass
					

class rfid_threaded_listener():
	def __init__(self, rfid_scanner_class, parent_pipe, data_queue, server_connector_class, main_screen_variables_class):
		self.rfid_scanner_class = rfid_scanner_class
		self.parent_pipe = parent_pipe
		self.data_queue = data_queue
		self.server_connector_class = server_connector_class
		self.main_screen_variables_class = main_screen_variables_class
		self.cup_numbers = 0
		self.cups_used_dict = {}
		
	def rfid_scanner_add(self):
		self.rfid_scanner_class.scanning_status = True
		self.rfid_scanner_class.scanning_operation = "ADD"

	def rfid_scanner_remove(self):
		self.rfid_scanner_class.scanning_status = True
		self.rfid_scanner_class.scanning_operation = "REMOVE"

	def rfid_scanner_off(self):
		self.rfid_scanner_class.scanning_status = False
		self.rfid_scanner_class.scanning_operation = "REMOVE"
		
	def datetime_formatted(self):
		return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		
	def rfid_dictionary_updater(self):    
		global cups_used_numbers
		
		while True:
			
			if self.rfid_scanner_class.scanning_status == True:
				last_scanned_rfid = self.parent_pipe.recv()
				print("last_scanned_rfid value is: ", last_scanned_rfid)
				print("modified last scanned rfid is: ", last_scanned_rfid[:-1])
				print("The rfid scanner operation is: ", self.rfid_scanner_class.scanning_operation)
				if self.rfid_scanner_class.scanning_operation == "ADD":
					print("starting rfid_checker loop")
					print("just recieved a scanned rfid from child process: ",last_scanned_rfid)
					already_registered = last_scanned_rfid in self.cups_used_dict.values()
					if already_registered == False:  # If statement stops duplicate adding of cup RFID's in a single order by registering a list in a dictionary
						self.cups_used_dict[self.cup_numbers] = last_scanned_rfid
						self.cup_numbers = self.cup_numbers+1
						print(self.cups_used_dict)
						#register_cup()
						self.main_screen_variables_class.amount_of_RFID_Numbers_Registered += 1
						self.data_queue.put(last_scanned_rfid)
					else:
						print("cup already registered")
						print(self.cups_used_dict)
						
						
				elif self.rfid_scanner_class.scanning_operation == "REMOVE":
					already_registered = last_scanned_rfid in self.cups_used_dict.values()
					if already_registered == True:  # If statement stops duplicate adding of cup RFID's in a single order by registering a list in a dictionary
						print(get_key(last_scanned_rfid))
						del self.cups_used_dict[get_key(last_scanned_rfid)]
						print("Removed Key from dictionary, new updated dictionary", self.cups_used_dict)
						print(self.cups_used_dict)
						#register_cup_removal()
						self.main_screen_variables_class.amount_of_RFID_Numbers_Registered -= 1
						self.data_queue.put(last_scanned_rfid)
						time.sleep(0.5)
					else:
						# No warning of cup not being already registered on screen yet....
						print("cup is not yet registered, can't remove cup")
						print(self.cups_used_dict)
						# Not adding data, but adds to queue which is being checked, a value in the queue causes screen update
						self.data_queue.put(last_scanned_rfid)
						# Added time after removing cup prevents adding of cup immediately after
						time.sleep(0.25)
						
						
				elif self.rfid_scanner_class.scanning_operation == "IDENTIFY_RFID":
					print("Starting new rfid loop in rfid_dict_updater: scanning rfid and identifying it in the database")
					current_rfid_owner = self.server_connector_class.admin_rfid_registered_checker(last_scanned_rfid[:-1])
					print(current_rfid_owner)
					if current_rfid_owner == None:
						print("rfid is not in use on the database and is availible for registration")
						self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
						self.main_screen_variables_class.variable_2 = ("RFID availible for addition to database and linking to new delivery vehicle.")
						
					else:
						print("rfid is currently in use in table: ", current_rfid_owner)
						self.main_screen_variables_class.variable_2 = ("RFID is unavailible for addition to database, currently in use as: ", current_rfid_owner)
						self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
						
				elif self.rfid_scanner_class.scanning_operation == "IDENTIFY_DELIVERY_BOX":
					selected_box = self.server_connector_class.admin_return_box_rfid_uid_details(last_scanned_rfid[:-1])
					print(selected_box)
					print(selected_box[0])
					if selected_box[0] == True:
						if selected_box[1] == self.main_screen_variables_class.variable_5:
							print("found box owned by current selected admin, the box contains ",selected_box[2] ," cups currently.")
							self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
							if selected_box[2] == 0:
								return_message = ("Delivery Box Info: \nCurrent Cups: ", str(selected_box[2]), "\nCurrent Owner: ", str(selected_box[3]), "\nIn Delivery Vehicle: ", str(selected_box[4]))
								self.main_screen_variables_class.variable_2 = ["".join(return_message), selected_box[2], selected_box[3], selected_box[4], selected_box[5], selected_box[6]]
							elif selected_box[2] > 0:
								return_message = ("Delivery Box Info: \nCurrent Cups: ", str(selected_box[2]), "\nCurrent Owner: ", str(selected_box[3]), "\nIn Delivery Vehicle: ", str(selected_box[4]))
								self.main_screen_variables_class.variable_2 = ["".join(return_message), selected_box[2], selected_box[3], selected_box[4], selected_box[5], selected_box[6]]
						else:
							self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
							if selected_box[2] == 0:
								return_message = ("Delivery Box Info: \nCurrent Cups: ", str(selected_box[2]), "\nCurrent Owner: ", str(selected_box[3]), "\nIn Delivery Vehicle: ", str(selected_box[4]))
								self.main_screen_variables_class.variable_2 = ["".join(return_message), selected_box[2], selected_box[3], selected_box[4], selected_box[5], selected_box[6]]
							elif selected_box[2] > 0:
								return_message = ("Delivery Box Info: \nCurrent Cups: ", str(selected_box[2]), "\nCurrent Owner: ", str(selected_box[3]), "\nIn Delivery Vehicle: ", str(selected_box[4]))
								self.main_screen_variables_class.variable_2 = ["".join(return_message), selected_box[2], selected_box[3], selected_box[4], selected_box[5], selected_box[6]]
					elif selected_box[0] == False:
						self.main_screen_variables_class.variable_2 = "DELIVERY BOX NOT IDENTIFIED IN THE DATABASE"
						
				elif self.rfid_scanner_class.scanning_operation == "IDENTIFY_DELIVERY_BOX_FULL_DETAILS":
					selected_box = self.server_connector_class.admin_return_box_rfid_uid_details(last_scanned_rfid[:-1])
					print(selected_box)
					if selected_box[0] == True:
						print("found box owned by current selected admin, the box contains ",selected_box[2] ," cups currently.")
						self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
						if selected_box[2] == 0:
							self.main_screen_variables_class.variable_2 = "Delivery Box should be empty and ready for use"
						elif selected_box[2] > 0:
							return_message = ("Delivery Box should have ", str(selected_box[2]), " cups currently.")
							self.main_screen_variables_class.variable_2 = "".join(return_message)
					elif selected_box[0] == False:
						self.main_screen_variables_class.variable_2 = "DELIVERY BOX NOT IDENTIFIED IN THE DATABASE"
							
				elif self.rfid_scanner_class.scanning_operation == "IDENTIFY_CUP_RFID_ADMIN_OWNED_CLEAN_ADD_TO_BOX":
					selected_cup_owner = self.server_connector_class.admin_cup_rfid_ownership_check(last_scanned_rfid[:-1]) # self.main_screen_variables_class.variable_5)
					print(selected_cup_owner)
					if selected_cup_owner[0] == True:
						cup_clean_condition = self.server_connector_class.admin_return_cup_clean_condition(last_scanned_rfid[:-1])
						if selected_cup_owner[1] == self.main_screen_variables_class.variable_5:
							if cup_clean_condition == True:
								cup_in_box_already = self.server_connector_class.admin_check_rfid_in_delivery_box(last_scanned_rfid[:-1])
								print("result of cup already being registered in another delivery box is: ", cup_in_box_already)
								if cup_in_box_already[0] != True:
									print("Found cup owned by current selected admin and the cup is clean. Cup is not currently in another delivery box")
									self.main_screen_variables_class.variable_2 = "Found cup owned by current selected admin and the cup is clean. Cup is not currently in another delivery box"
									self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
								elif cup_in_box_already[0] == True:
									print("Found cup owned by current selected admin and the cup is clean. However Cup is currently in another delivery box")
									self.main_screen_variables_class.variable_2 = "Found cup owned by current selected admin and the cup is clean. However Cup is currently in another delivery box"
									self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
							elif cup_clean_condition == False:
								print("Found cup owned by current selected admin, however the cup is not clean.")
								self.main_screen_variables_class.variable_2 = "Found cup owned by current selected admin, however the cup is not clean."
								self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
						else:
							if cup_clean_condition == True:
								print("Found cup is not owned by current selected admin, the cup is clean.")
								self.main_screen_variables_class.variable_2 = "Found cup is not owned by current selected admin, the cup is clean."
								self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
							elif cup_clean_condition == False:
								print("Found cup is not owned by current selected admin, however the cup is not clean")
								self.main_screen_variables_class.variable_2 = "Found cup is not owned by current selected admin, however the cup is not clean"
								self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
								
					else:
						print("RFID not recognised in the cup database")
						return_message = ("Scanned RFID ", last_scanned_rfid[:-1], "has not been found or recognised in the cup database.")
						self.main_screen_variables_class.variable_2 = "".join(return_message)
						
				elif self.rfid_scanner_class.scanning_operation == "IDENTIFY_DELIVERY_VEHICLE":
					delivery_vehicle_details = self.server_connector_class.admin_return_delivery_vehicle_details(last_scanned_rfid[:-1]) # self.main_screen_variables_class.variable_5)
					print(delivery_vehicle_details)
					if delivery_vehicle_details == "RFID did not match in delivery_vehicle_db":
						self.main_screen_variables_class.variable_2 = "RFID did not match in delivery_vehicle_db"
						self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
					elif delivery_vehicle_details != False:
						print(delivery_vehicle_details[1])
						delivery_vehicle_composition = self.server_connector_class.admin_return_delivery_vehicle_composition_details(last_scanned_rfid[:-1])
						print(delivery_vehicle_composition)
						if delivery_vehicle_composition[0] == True:
							return_message = ("Delivery Bike: ", str(delivery_vehicle_details[10]), " It contains ", str(delivery_vehicle_composition[1]), " boxes already")
						else:
							return_message = ("Delivery Bike: ", str(delivery_vehicle_details[10]), " It contains an unknown number of boxes, error searching vehicle composition database")
						self.main_screen_variables_class.variable_2 = "".join(return_message)
						self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]
					else:
						return_message = ("Error in dataase: ", delivery_vehicle_details)
						self.main_screen_variables_class.variable_2 = "".join(return_message)
						self.main_screen_variables_class.variable_3 = last_scanned_rfid[:-1]

				elif self.rfid_scanner_class.scanning_operation == "ADD_NEW_BOXES":
					print("starting add delivery boxes loop in rfid_dictionary_updater")
					current_rfid_owner = self.server_connector_class.admin_rfid_registered_checker(last_scanned_rfid[:-1])
					print(current_rfid_owner)
					if current_rfid_owner == None:
						print("rfid is not in use on the database and is availible for registration")

if __name__ == '__main__':
	
	import subprocess
	from subprocess import Popen, PIPE
	
	from multiprocessing import Process, Pipe
	import sys
	
	(ParentEnd, ChildEnd) = Pipe()
	cup_scanner = rfid_scanner(True, True, "ADD")
	child = Process(target = cup_scanner.auto_polling, args=(ChildEnd,))
	child.start()
	
	Scanned_list = []
	
	while True:
		last_scanned_rfid = ParentEnd.recv()
		print("parent end recieved....", last_scanned_rfid)
		
		if last_scanned_rfid in Scanned_list:
			print("rfid already in list")
		else:
			Scanned_list.append(last_scanned_rfid)
			print("current scanned list",Scanned_list)
		pass

