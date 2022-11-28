#client_paho_library_ rfid_mqtt c1 mux operation
import paho.mqtt.client as mqtt
import time
import sys
import datetime
import logging
import smtplib
import json #Using for parsing json data from rfid c1_mux mqtt data

#from email_certs.temp_email_certs import *
from Connect_functions import server_connection_details #imports all mysql connection functions
from Cafe_details.passlib_authentication_module import hash_pwd, verify_pwd, combined_variables_hash #imports hashing and encryption functions
from certs.program_connection_details import * #importing the local connection details file


server1 = server_connection_details(local_con_details.host, local_con_details.port, local_con_details.user, local_con_details.pwd, local_con_details.DB_Name, local_con_details.ssl_ca, local_con_details.ssl_cert, local_con_details.ssl_key)

from queue import Queue
import _thread

#q = Queue()

#logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s)", handlers = [logging.FileHandler("debug.log"), logging.StreamHandler()])

def datetime_formatted():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	
client_unique_name = "RaspiTestSubscriber"


local_broker_address = "192.168.1.210"

def on_log(client, userdata, level, buf):
	logging.debug("MQTT internal buff: " + buf)

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		client.connected_flag = True #set flag
		logging.info("connected OK Returned code = " + str(rc))
	else:
		client.bad_connection_flag = True
		#print("Bad connection Returned code = ", rc)
		logging.info("Bad connection Returned code = " + str(rc))
		#0: Connection successful
		#1: Connection refused – incorrect protocol version
		#2: Connection refused – invalid client identifier
		#3: Connection refused – server unavailable
		#4: Connection refused – bad username or password
		#5: Connection refused – not authorised
		#6-255: Currently unused.
		
def on_disconnect(client, userdata, rc):
	logging.info("disconnecting reason " +str(rc))
	if rc != 0:
		logging.error("Unexpected disconection not caused by calling disconnect")
	client.connected_flag = False
	client.disconnected_flag = True
	
def on_subscribe(client, userdata, mid, granted_qos):
	logging.info("in on subscribe callback response " + str(mid))
	for t in client.topic_ack:
		if t[1] == mid:
			t[2] = 1 #set acknowledgement flag
			logging.info("subscription acknoledged " + str(t[0]))
			client.suback_flag = True
	
def on_message(client, userdata, message):
	print("on_message is kinda working....(outside of class construction)")
	logging.info(userdata)
	logging.info(message)
	q.put(message)
	
	
def on_publish(client, userdata, mid):		#mid = message id
	logging.info("In on_pub callback mid = " + str(mid))
	pass

def reset():
	ret = client.publish("test/message", "", 0, True)
	
def check_subs(client):
	#returns false if have an unacknowledged subscription
	print(client.topic_ack)
	for t in client.topic_ack.values():
		logging.debug("topic_ack in check subs is " + str(t))	
		if t['rc'] != 0:
			logging.warning("subscription acknowledgement " + t + " not acknowledged")
			return False
	return True

def unique_client_id(datetime):
	logging.info("UNIQUE CLIENT ID FOR MQTT CLIENT: %s", str(client_unique_name + datetime))
	return str(client_unique_name + datetime)

class MQTTClient(mqtt.Client):

	def __init__(self,cname,**kwargs):
		super(MQTTClient, self).__init__(cname,**kwargs)
		self.last_pub_time=time.time()
		self.topic_ack={}
		self.subscribe_flag=False
		self.bad_connection_flag=False
		self.connected_flag=False
		self.retry_count = 0
		self.disconnect_flag=False
		self.disconnect_time=0.0
		self.pub_msg_count=0
		self.devices=[]


class rfid_multiplex_mqtt_listener():
	
	def __init__(self, rows, antennas):
		self.client = MQTTClient(unique_client_id(datetime_formatted()))	#Initialising MQTTclient on setup of class, re-initialised with each listener launch
		self.run_main = False
		self.run_flag = True
		self.q = Queue()
		self.rows = rows
		self.antennas = antennas
	
	# -- def class methods to call when using main --
	
	def on_log(self, client, userdata, level, buf):
		#print(buf)
		logging.debug("MQTT internal buff: " + buf)

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			client.connected_flag = True #set flag
			logging.info("connected OK Returned code = " + str(rc))
		else:
			client.bad_connection_flag = True
			logging.info("Bad connection Returned code = " + str(rc))
			#0: Connection successful
			#1: Connection refused – incorrect protocol version
			#2: Connection refused – invalid client identifier
			#3: Connection refused – server unavailable
			#4: Connection refused – bad username or password
			#5: Connection refused – not authorised
			#6-255: Currently unused.
			
	def on_disconnect(self, client, userdata, rc):
		logging.info("disconnecting reason " +str(rc))
		if rc != 0:
			logging.error("Unexpected disconection not caused by calling disconnect")
		client.connected_flag = False
		client.disconnected_flag = True
		
	def on_subscribe(self, client, userdata, mid, granted_qos):
		logging.info("in on subscribe callback response " + str(mid))
		for t in client.topic_ack:
			if t[1] == mid:
				t[2] = 1 #set acknowledgement flag
				logging.info("subscription acknoledged " + str(t[0]))
				client.suback_flag = True
		
	def on_message(self, client, userdata, message):
		logging.info(userdata)
		logging.info(message)
		self.q.put(message)
		
		
	def on_publish(self, client, userdata, mid):		#mid = message id
		logging.info("In on_pub callback mid = " + str(mid))
		pass

	def reset(self):
		ret = self.client.publish("test/message", "", 0, True)
		
	def check_subs(self, client):
		#returns false if have an unacknowledged subscription
		print(client.topic_ack)
		for t in client.topic_ack.values():
			logging.debug("topic_ack in check subs is " + str(t))	
			if t['rc'] != 0:
				logging.warning("subscription acknowledgement " + t + " not acknowledged")
				return False
		return True

	def unique_client_id(datetime):
		logging.info("UNIQUE CLIENT ID FOR MQTT CLIENT: %s", str(client_unique_name + datetime))
		return str(client_unique_name + datetime)

	def MQTT_queued_messages_and_matrix_plotter(self, pipe):
		
		# Generate rows and antennas
		current_row = 0
		matrix_nested_list = []
		for row in range(self.rows):
			row_antenna_list = []
			for antenna in range(self.antennas):
				row_antenna_list.append("")
			matrix_nested_list.append(row_antenna_list)

		while True:
			try:
				message = self.q.get()
				if message is None:
				   continue
				try:
					logging.debug("--This is the newly nested list list--")
					logging.debug(matrix_nested_list)
					logging.debug("--This is the newly nested list list--")
					string_message = str(message.payload)
					msg_to_parse = str(message.payload.decode("utf-8"))
					parsed_msg = json.loads(msg_to_parse)
					logging.info("MQTT server found rfid "+ str(parsed_msg['uid']) + "from antenna " + str(parsed_msg['antenna']))
					uid = parsed_msg['uid']
					antenna = parsed_msg['antenna']
					currently_registered_uid = matrix_nested_list[current_row][antenna-1]
					logging.debug("currently_registered_uid is: " + currently_registered_uid)
					if currently_registered_uid != uid and currently_registered_uid != "":
						if current_row == (self.rows-1):
							current_row = 0
							logging.debug("Current row in rfid plotter matrix reset to zero")
							matrix_nested_list[current_row] = ["","",""]
						else:
							current_row += 1
							logging.debug("Current row in rfid plotter matrix increased")
							matrix_nested_list[current_row] = ["","",""]
					matrix_nested_list[current_row][antenna-1] = uid
					pipe.send(matrix_nested_list)
					if message.topic == "test/message":
						pass

				except Exception as err:
					logging.warning("Decoding raised error as: " + (err))
			except Exception as e:
				logging.warning("Exception occured in threaded queue as: " + (e))

	def rfid_mqtt_listener(self, pipe):
		'''Main program used to connect to mqtt broker and subscribe to topics where the rfid's are being published'''
		
		self.client = MQTTClient(unique_client_id(datetime_formatted()))

		self.client.on_connect = self.on_connect	#bind call back function
		self.client.on_log = self.on_log
		self.client.on_disconect = self.on_disconnect
		self.client.on_subscribe = self.on_subscribe
		self.client.on_publish = self.on_publish
		self.client.on_message = self.on_message
		topics = [("test/message",0), ("test/text", 0), ("BDS/outbuilding", 0)]
		topic_ack = []
		topic_sub_dict = {"test/message": 1, "test/text": 1, "BDS/outbuilding": 1}

		self.run_main = False
		self.run_flag = True
		
		_thread.start_new_thread(self.MQTT_queued_messages_and_matrix_plotter,(pipe,))	#start thread to collect messages


		while self.run_flag:
			while not self.client.connected_flag and self.client.retry_count<3:
				for t in topics:
					topic_sub_dict[t[0]] = 1
				count = 0
				self.run_main=False
				try:
					logging.info("Connecting to broker: %s", local_broker_address)
					self.client.connect(local_broker_address, keepalive=30)		#.connect is a blocking function
					break
				except:
					logging.info("%s connection attempts failed", str(self.client.retry_count))
					self.client.retry_count += 1
					if self.client.rety_count > 3:
						self.run_flag = False
						
			if not self.run_main:
				self.client.loop_start()
				while True:
					if self.client.connected_flag:	#wait for CONNACK
						self.client.rety_count = 0
						self.run_main = True
						break
					if count > 6 or self.client.bad_connection_flag:	#dont wait forever
						self.client.loop_stop()
						self.client.retry_count += 1
						if self.client.rety_count > 3:
							self.run_flag = False
						break #break from while loop
						
					time.sleep(1)
					count += 1
					
			if self.run_main:
				try:
					#Do main loop
					logging.info("In the main client mqtt loop")	#subscribe and publish here
					
					time.sleep(3) 
					
					for t in topics:
						#if topic_sub_dict[t[0]] != 0:
						try:
							r=self.client.subscribe(t)
							if r[0] == 0:
								logging.info("subscribed to topic " + str(t[0]) + " return code" + str(r))
								self.client.topic_ack[t[0]] = {'mid':r[1], 'rc':0}	#keeping track of subscription
								topic_sub_dict[t[0]] = 0
							else:
								logging.error("error on subscribing " + str(r) + " sys.exit(1) being called.")
								self.client.loop_stop()
								sys.exit(1)
						except Exception as e:
							logging.error("error on subscribing " + str(e) + " sys.exit(1) being called.")
							self.client.loop_stop()
							sys.exit(1)
						#else:
							#logging.info("Client is already subscribed to " + t[0] + "and does not need re-subscribing")
					if not check_subs(self.client):
						logging.warning("Missing subscriber acknowledgements")
					
					time.sleep(3)
					
				except(KeyboardInterrupt):
					print("Keyboard interrupt so ending")
					self.run_flag = False
					
					
		print("quitting")
		self.client.disconnect()
		self.client.loop_stop()
		
	def launch_mqtt_listener(self, pipe):
		_thread.start_new_thread(self.rfid_mqtt_listener, (pipe,))
		
	def manual_disconnect(self):
		logging.info("Manual disconect called, run main and run flags reset")
		self.run_main = False
		self.run_flag = False
		



			
		



if __name__ == '__main__':
	#Setup local logging file
	logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s)", handlers = [logging.FileHandler("debug.log"), logging.StreamHandler()])
	
	from multiprocessing import Process, Pipe
	(ParentEnd, ChildEnd) = Pipe()
	
	
	external_rfid_mqtt_class = rfid_multiplex_mqtt_listener(3, 5)
	external_rfid_mqtt_class.launch_mqtt_listener(ChildEnd)
	
	reset_count = 0
	
	while True:
		last_processed_rfid = ParentEnd.recv()
		print("------------- RFID MQTT EXTERNAL CLASS SENDING PIPED MSG -------------")
		print(last_processed_rfid)
		reset_count += 1
		if reset_count == 10:
			external_rfid_mqtt_class.manual_disconnect()
		print("------------- RFID MQTT EXTERNAL CLASS SENDING PIPED MSG -------------")
	

