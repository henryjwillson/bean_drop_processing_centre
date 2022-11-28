#''' This file builds the Cafe Details Class '''

import sqlite3 #Importing SQLite
# from passlib_authentication_module import hash_pwd, verify_pwd
import mysql.connector
from mysql.connector import errorcode

class Cafe_class:
	'''This class contains the details for the cafe for data storage'''
	
	def __init__(self, cafe_id, cafe_pwd, cafe_name, POS_ID, cafe_server_ID, cafe_server_pwd):
		self.cafe_id = cafe_id						#Cafe_id is using QR_generator encrypted user id
		self.cafe_pwd = cafe_pwd
		self.cafe_name = cafe_name
		self.POS_ID = POS_ID
		self.cafe_server_ID = cafe_server_ID 		#Cafe_server_id is the non encrypted id. Cafe_id is using QR_generator encrypted user id
		self.cafe_server_pwd = cafe_server_pwd
		
	def update_cafe_pwd(self, old_pwd, new_pwd):
		if old_pwd == self.cafe_pwd:
			self.cafe_pwd = new_pwd
			return True
		else:
			return False
		
	def __str__(self):
		return 'Cafe name: %s , POS ID: %s' % (self.cafe_name, self.POS_ID)

if __name__ == "__main__":
	pass
