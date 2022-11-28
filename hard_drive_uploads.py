#Hardrive upload to server program
#Program will download all images from the hard drive and upload them to the raspberry pi and the local NAS storage server when setup


import sqlite3								# Used as local database for access to orders without need for connection to server network
import sys, os
import subprocess

class bean_drop_station_database:
	
	def __init__(self, database_file):
		self.database_file = database_file
		self.transfer_database = transfer_database
		
	def create_photo_database_table(self):
		conn_local_db = sqlite3.connect(self.database_file)
		c = conn_local_db.cursor()
		try:
			with conn_local_db:
				c.execute("""CREATE TABLE cup_return_images (
						cup_return_id integer,
						cup_image_name text,
						download_status integer,
						download_date_time datetime,
						PRIMARY KEY (cup_return_id),
						UNIQUE (cup_image_name)
						)""")
				conn_local_db.commit()
				conn_local_db.close()
				print("New table successfully built into cup_return_image_database.db")
		except sqlite3.Error as err:
			print("The error in creating table in database was: ", err)
	
	def create_transfer_photo_database_table(self):
		conn_local_db = sqlite3.connect(self.transfer_database)
		c = conn_local_db.cursor()
		try:
			with conn_local_db:
				c.execute("""CREATE TABLE cup_return_images (
						cup_return_id integer,
						cup_image_name text,
						download_status integer,
						download_date_time datetime,
						PRIMARY KEY (cup_return_id),
						UNIQUE (cup_image_name)
						)""")
				conn_local_db.commit()
				conn_local_db.close()
				print("New table successfully built into cup_return_image_database.db")
		except sqlite3.Error as err:
			print("The error in creating table in database was: ", err)

	def download_camera_photos_hard_drive(self, media_drive, date_time, transfer_database_file):
			conn_local_db = sqlite3.connect(self.database_file)
			c = conn_local_db.cursor()
			conn_local_db2 = sqlite3.connect(self.transfer_database_file)
			c2 = conn_local_db2.cursor()
			cwd_retrieve = os.getcwd()
			picture_storage_directory = str(cwd_retrieve) + "/Cup_photo_folder" #Appends string to GUI_Sounds directory
			try:
				with conn_local_db:
					c2.execute("SELECT `cup_image_name` FROM `cup_return_images`;")
					un_uploaded_photo_list = c2.fetchall()
					c2.execute("SELECT * FROM `cup_return_images`;")
					image_details_list = c2.fetchall()							#Details used in this list to append to new hard-drive
					print(len(un_uploaded_photo_list))
					for image in un_uploaded_photo_list and image_det in image_details_list:
						print("this is the image: ", image)
						print("these are the image details: " image_det)
						formatted_image_name = str(image)[2:-3]
						args_list = ["sudo cp /media/pi/", media_drive, formatted_image_name, " ", picture_storage_directory,formatted_image_name]
						shell_command = ''.join([str(item) for item in args_list])
						print(shell_command)
						p3 = subprocess.run([shell_command], cwd = picture_directory, shell=True, capture_output=True,text=True)
						print("The standard output is: ",p3.stdout)
						if p3.stdout == None or p3.stdout == "" or p3.stdout == " b''":
							print("captured standard output when its printing nothing")
						print("The standard error is: ",p3.stderr)
						if p3.stderr != None or p3.stderr != "" or p3.stderr != " b''":
							print("captured error")
							break
						#download_status_variables = (2,date_time,formatted_image_name)			#download state set to the number 2 confirming it has indeed been downloaded by the main Raspi System
						download_status_result = self.update_photo_download_status(2,date_time,formatted_image_name)
						print(download_status_result)
						setup_result = self.fetchall_cup_image_table
						print(setup_result())
						

	def update_photo_download_status(self, download_status, date_time, cup_return_id):
		conn_local_db = sqlite3.connect(self.database_file)
		c = conn_local_db.cursor()
		try:
			with conn_local_db:
				variables_set = (download_status, date_time, cup_return_id)
				update_cup_image_download_status_query = "UPDATE `cup_return_images` SET `download_status` = ? , `download_date_time` = ? WHERE `cup_image_name` = ?;"
				#UPDATE `cup_db` SET `OWNER_ID`= %s,`Number_of_uses`=`Number_of_uses`+1 ,`Last_use`=%s WHERE `RFID_UID` = %s;"
				c.execute(update_cup_image_download_status_query,(download_status, date_time, cup_return_id))
				conn_local_db.commit()
				return "update_photo_download_status completed method..."
		except Exception as err:
			print("Error in updating photo download status was: ", err)
			return False
		finally:
			conn_local_db.close()
