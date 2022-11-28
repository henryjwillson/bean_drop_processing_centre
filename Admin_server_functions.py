#Admin Server Functions
from tkinter import *
import os
import multiprocessing
from multiprocessing import Process, Pipe
import RPi.GPIO as GPIO
from PIL import Image, ImageTk
import subprocess
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
#import itertools #python3 library for zip function allowing interation over two lists simultaneously

import _thread
import queue
import sqlite3								# Used as local database for access to orders without need for connection to server network
import datetime								# Time tracking

from rfid_scanner_class import rfid_scanner, rfid_threaded_listener
from rfid_mqtt_subscriber_continous_operation import rfid_multiplex_mqtt_listener
from Connect_functions import server_connection_details #imports all mysql connection functions
from Cafe_details.passlib_authentication_module import hash_pwd, verify_pwd, combined_variables_hash #imports hashing and encryption functions
from certs.program_connection_details import * #importing the local connection details file

import time

from collections.abc import Mapping
from Frame_Sizing_Class import Frame_Sizing
main_frame_size = Frame_Sizing(1024,600)

# Importing a copy of the screen numbers class from the main POS GUI. Plenty of redundancy in this class for the processing center
# however acts as an easy means to duplicate code and work between both GUI's
from Screen_Numbers_Class import screen_numbers
mainscreen = screen_numbers(0, False, "henry willson", 0, 0, "", 0, 0, 0, 0, 0, 0, 0, 0,"", "", "", "", "")

# WARNING CHECK BEAN DROP SALES VALUES ARE STILL CORRECT---------------------------------------------
from Bean_drop_sales_values import Bean_drop_sales_values
BD_charge = Bean_drop_sales_values(3.00, 0.25, 0.25, 0.25)
# WARNING ABOVE ---------------------------------------------------------------------

from Cafe_details.Cafe_class import Cafe_class

#Cafe_class details class----------------------------------------------------------------------------------------------------
Bean_drop_cafe = Cafe_class("XXX",123, "XXX", 4,5,"XXX") #The Cafe
Bean_drop_processing_centre = Cafe_class("XXX",123, "XXX", 4, 5, "XXX") #Temporary class used for BH details of Processing Centre class. 
HW_Temp_account = "XXX"
Bean_drop_station_Ems = "XXX"
Bean_drop_delivery_box_1 = "XXX"

def cafe_name_and_id_recall():
	return_dict = {}
	cafe_name_and_id = server1.admin_recall_cafe_database_name_id()
	cafe_name_and_id_dict = {}
	cafe_name_list = []
	for item in cafe_name_and_id:
		cafe_name_and_id_dict[item[1]] = item[0]
		cafe_name_list.append(item[1])
	print("This is the cafe name and id dictionary: ",cafe_name_and_id_dict)
	print("This is the cafe_name_list: ",cafe_name_list)
	return_dict[1] = cafe_name_and_id_dict
	return_dict[2] = cafe_name_list
	return return_dict
	
def cafe_company_name_and_id_recall():
	return_dict = {}
	cafe_company_name_and_id = server1.admin_recall_customer_company_database_name_id()
	cafe_company_name_and_id_dict = {}
	cafe_company_name_list = []
	for item in cafe_company_name_and_id:
		cafe_company_name_and_id_dict[item[1]] = item[0]
		cafe_company_name_list.append(item[1])
	print("This is the cafe name and id dictionary: ",cafe_company_name_and_id_dict)
	print("This is the cafe_name_list: ",cafe_company_name_list)
	return_dict[1] = cafe_company_name_and_id_dict
	return_dict[2] = cafe_company_name_list
	return return_dict


def update_restricted_cafes_list(connection_class):
# Populating temporary list of cafe accounts which are restricted and cannot be used to make an order.
	try:
		cafe_list = connection_class.admin_recall_cafe_dictionary()
		cafe_list_length = len(cafe_list)
		cafe_dictionary = {}
		for k in range (1, cafe_list_length + 1):       #Converting list to dictionary as it will be faster to sort through in future compared to that of a list
				cafe_dictionary[k] = str(cafe_list[k-1])[2:42]
		print("printing the cafe dictionary: ",cafe_dictionary)
		return cafe_dictionary
	except Exception as cafe_dictionary_error:
		print("cafe_dictionary{} error is : ",cafe_dictionary_error)
		
def update_dictionary_of_bean_drop_stations_details(connection_class):
	#Populate dictionary with more details about cafe_details
	try:
		drop_station_details_dictionary = {}
		restricted_drop_station_list = connection_class.admin_recall_bean_drop_station_dictionary_details()
		for i in restricted_drop_station_list:
			print(i)
			drop_station_details_dictionary[i[2]] = {'bdcentre_owner':i[1],'return_location_id':i[2], 'name':i[3],'Address Line 1': i[4], 'City': i[5], 'County': i[6], 'Post Code': i[7], 'Storage Capacity': i[8], 'Quarantine Capacity': i[9], 'Current cups': i[10], 'Cups in Quarantine':i[11], 'BDS_box_bag':i[19]}
			print(drop_station_details_dictionary)
		return drop_station_details_dictionary
	except Exception as error:
		print("Error in update_dictionary_of_bean_drop_stations_details is: ", error)
		
def list_of_bean_drop_station_names():
	bean_drop_station_appended_list=[]
	for value in restricted_bean_drop_dictionary.values():
		bean_drop_station_appended_list.append(bean_drop_station_details_dictionary[value]['name'])
	return bean_drop_station_appended_list
		

class screen_variables():
	'''Class to allow transfer of values between processes and screens'''
	
	def __init__(self, variable_1, variable_2, variable_3, variable_4, variable_5, thread_condition):
		self.variable_1 = variable_1
		self.variable_2 = variable_2
		self.variable_3 = variable_3
		self.variable_4 = variable_4
		self.variable_5	= variable_5
		self.thread_condition = thread_condition
	
	def reset_variables(self):
		self.variable_1 = ""
		self.variable_2 = ""
		self.variable_3 = ""
		self.variable_4 = ""
		self.variable_5	= ""
		self.thread_condition = 1
		
		
# RFID polling setup ------------------------------------------------------------------------
cup_scanner = rfid_scanner(True, True, "ADD")
(ParentEnd, ChildEnd) = Pipe()
child = Process(target = cup_scanner.auto_polling, args=(ChildEnd,))
child.start()

def rfid_scanner_add():
    cup_scanner.scanning_status = True
    cup_scanner.scanning_operation = "ADD"

def rfid_scanner_remove():
    cup_scanner.scanning_status = True
    cup_scanner.scanning_operation = "REMOVE"

def rfid_scanner_off():
    cup_scanner.scanning_status = False
    cup_scanner.scanning_operation = "REMOVE"
    
def rfid_dictionary_updater():    
    global cups_used_numbers
    
    while True:
        
        if cup_scanner.scanning_status == True:
            last_scanned_rfid = ParentEnd.recv()
            if cup_scanner.scanning_operation == "ADD":
                print("starting rfid_checker loop")
                print("just recieved a scanned rfid from child process: ",last_scanned_rfid)
                already_registered = last_scanned_rfid in cups_used_dictionary.values()
                if already_registered == False:  # If statement stops duplicate adding of cup RFID's in a single order by registering a list in a dictionary
                    cups_used_dictionary[cups_used_numbers] = last_scanned_rfid
                    cups_used_numbers = cups_used_numbers+1
                    print(cups_used_dictionary)
                    register_cup()
                    dataQueue.put(last_scanned_rfid)
                else:
                    print("cup already registered")
                    print(cups_used_dictionary)
            elif cup_scanner.scanning_operation == "REMOVE":
                already_registered = last_scanned_rfid in cups_used_dictionary.values()
                if already_registered == True:  # If statement stops duplicate adding of cup RFID's in a single order by registering a list in a dictionary
                    print(get_key(last_scanned_rfid))
                    del cups_used_dictionary[get_key(last_scanned_rfid)]
                    print("Removed Key from dictionary, new updated dictionary", cups_used_dictionary)
                    print(cups_used_dictionary)
                    register_cup_removal()
                    dataQueue.put(last_scanned_rfid)
                    time.sleep(0.5)
                else:
                    # No warning of cup not being already registered on screen yet....
                    print("cup is not yet registered, can't remove cup")
                    print(cups_used_dictionary)
                    # Not adding data, but adds to queue which is being checked, a value in the queue causes screen update
                    dataQueue.put(last_scanned_rfid)
                    # Added time after removing cup prevents adding of cup immediately after
                    time.sleep(0.25)

				
class highlighted_border_label():
	'''This class is build to add a flat boarder around a label with a highlighted colour. Overcoming Tkinter limitations
	 by implementing individual frames and there backgrounds for a label.'''
	 
	def __init__(self, hbg, hfg, hfont, highlight_colour):
		self.hbg = hbg
		self.hfg = hfg
		self.hfont = hfont
		self.highlight_colour = highlight_colour
		
	def insert_button(self, frame_name, hframe, hcolumn, hcolumn_span, hwidth, hrow, hrow_span, hheight, highlighted_bd_size, hwrap_length, htext, chosen_command):
		frame_name = Frame(hframe, height = hheight, width =  hwidth, bg = self.highlight_colour)
		frame_name.grid(column = hcolumn, columnspan= hcolumn_span, row = hrow, rowspan = hrow_span, sticky = E+W+N+S, padx=highlighted_bd_size, pady= highlighted_bd_size)
		
		label_name = Button(frame_name, text= htext, bg = self.hbg, fg = self.hfg, font = self.hfont, wraplength = hwrap_length, anchor = "center", command = chosen_command)
		label_name.pack(expand=True, fill=BOTH, padx=highlighted_bd_size, pady= highlighted_bd_size)
		
	def insert_button_kwargs(self,parent_frame, frame_name, chosen_command, **kwargs):
		frame_name = Frame(parent_frame, height = kwargs.get('height', None), width =  kwargs.get('width',None), bg = self.highlight_colour)
		frame_name.grid(column = kwargs.get('column', 0), columnspan= kwargs.get('column_span',1), row = kwargs.get('row', 0), rowspan = kwargs.get('row_span',1), sticky = E+W+N+S, padx=kwargs.get('frame_external_pad_size',1), pady= kwargs.get('frame_external_pad_size',1))
		
		label_name = Button(frame_name, text= kwargs.get('text',""), bg = self.hbg, fg = self.hfg, font = self.hfont, wraplength = kwargs.get('wraplength',0), anchor = "center", activebackground = kwargs.get('activebackground', "white"), activeforeground = kwargs.get('activeforeground',self.hfg), command = chosen_command)
		label_name.pack(expand=True, fill=BOTH, padx=kwargs.get('highlighted_bd_size',1), pady= kwargs.get('highlighted_bd_size',1))
	 
class pallette_colours():
	'''This is a class to setup colour palletes that can be used to stylise tkinter GUI'''
	
	def __init__(self, main_background, second_background, title, heading_text, main_text, highlighted_boarder):
		self.main_background = main_background
		self.second_background = second_background
		self.title = title
		self.heading_text = heading_text
		self.main_text = main_text
		self.highlighted_boarder = highlighted_boarder

def datetime_formatted():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# Main Tkinter Class based Frames
class Admin_Options_Home_Frame(Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, parent, width=main_frame_size.width, height=main_frame_size.height, bg="light blue")
		self.focus_set()
		# self.focus_force() 														# must set focus to Frame for button binds to work
		self.grid_location(0, 0) 													# setting frame starting location in root window
		# setting row sizes my runnning repeat row configures, rows and columns in .grid start at value of zero (0).
		for r in range(0, 8):
			self.grid_rowconfigure(r, minsize=main_frame_size.row_size_8)
		for c in range(0, 9):
			self.grid_columnconfigure(c, minsize=main_frame_size.column_size_10*10/9)

		self.grid(sticky=W+E+N+S)													# Sticky W+E+N+S causes grid to expand to frame size
		self.make_widgets()

	def make_widgets(self):
		Resize_screen_button = Button(self, text="RESIZE SCREEN", bg="light grey", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Re_size_screen,"","","","",""))
		Resize_screen_button.grid(column=0, columnspan=3, row=0, rowspan=2, sticky=W+E+N+S, padx=10, pady=10) 
		Add_new_boxes_button = Button(self, text="ADDITIONS TO DATABASE", bg="orange", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_database_additions_frame,"","","","",""))
		Add_new_boxes_button.grid(column=3, columnspan=3, row=0, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Process_cycle_transfers_button = Button(self, text="PROCESS CYCLE TRANSFERS", bg="#34f6f1", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_bean_drop_process_cycle_transfers,"","","","",""))
		Process_cycle_transfers_button.grid(column=6, columnspan=3, row=0, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Various_admin_transfers_button = Button(self, text="VARIOUS ADMIN TRANSFERS", bg="violet", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_various_admin_transfers_frame,"","","","",""))
		Various_admin_transfers_button.grid(column=0, columnspan=3, row=4, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		rfid_matrix_scanner_button = Button(self, text="RFID MATRIX SCANNER", bg="violet", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_rfid_matrix_scanner_frame,"","","","",""))
		rfid_matrix_scanner_button.grid(column=3, columnspan=3, row=4, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Identify_owner_of_rfid = Button(self, text="IDENTIFY RFID OWNER", bg="violet", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_identify_rfid_owner,"","","","",""))
		Identify_owner_of_rfid.grid(column=0, columnspan=3, row=6, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Cup_distrubution_monitoring = Button(self, text="CUP DISTRUBUTION MONITORING", bg="violet", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Bean_Drop_Cup_monitoring,"","","","",""))
		Cup_distrubution_monitoring.grid(column=3, columnspan=3, row=6, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Exit_admin_program_frame_button = Button(self, text="EXIT PROGRAM", bg="red",fg="white", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Exit_Program_Frame,"","","","",""))
		Exit_admin_program_frame_button.grid(column=6, columnspan=3, row=6, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		
		       

	def launch_selected_frame(self, selected_frame,variable_1, variable_2, variable_3, variable_4, variable_5):  # Linked to button event
		if selected_frame != "":
			main_screen_variables.variable_1 = variable_1
			main_screen_variables.variable_2 = variable_2
			main_screen_variables.variable_3 = variable_3
			main_screen_variables.variable_4 = variable_4
			main_screen_variables.variable_5 = variable_5
			self.destroy()
			print("launching ", selected_frame)
			selected_frame(root)
			selected_frame = ""
		
	def back_button_generic(self):
		back_label = Button(self, text="Back [/]", bg="yellow", relief=RAISED, bd=5, command = self.back_button_generic_action)
		back_label.grid(column=0, columnspan=2, row=0, sticky=W+E+N+S)
	
	def back_button_generic_action(self):
		# Changing value to 0 allows polling to restart at next screen (Value of 1 pauses polling)
		mainscreen.threadcondition = 0
		time.sleep(0.05)
		mainscreen.entry_widget_user_number = ""
		self.destroy()
		mainscreen.back_button_press_screen(root)
		
	def blinking_widget(self, selected_button_in_screen_class_variable):
		green_list = ["#55ff33", "#5fff3f", "#66FF47", "#73ff57", "#7bff60", "#84ff6c", "#8eff77", "#9aff85", "#a1ff8e", "#acff9c", "#b5ffa6", "#beffb1", "#c3ffb7", "#caffbf", "#d3ffca", "#dcffd5", "#e5ffe0", "#eeffeb", "#f7fff6", "#ffffff"]
		selected_button_in_screen_class_variable.variable_1.config(bg=green_list[self.green_fade_counter])
		if self.green_fade_counter <= 18 and self.green_fade_out == True:
			self.green_fade_counter += 1
			if self.green_fade_counter == 18:
				self.green_fade_out = False
		else:
			self.green_fade_counter -= 1
			if self.green_fade_counter == 0:
				self.green_fade_out = True
		self.after(100, lambda: self.blinking_widget(selected_button_in_screen_class_variable))
		
	def rfid_matrix_preview_setup(self, frame):
		self.launch_rfid_mqtt_scanning()
		
		self.text_instruction_var = StringVar()
		self.text_instruction_var.set("SCAN CUPS USING MULTIPLE ANTENNAS")
		
		self.confirmation_button_var = StringVar()
		self.confirmation_button_var.set("CONFIRM SCANNED CUPS")
		
		# Setting up StringVars for matrix
		self.status_row_0_antenna_0 = StringVar()
		self.status_row_0_antenna_1 = StringVar()
		self.status_row_0_antenna_2 = StringVar()
		self.status_row_0_antenna_3 = StringVar()
		self.status_row_0_antenna_4 = StringVar()
		
		self.status_row_1_antenna_0 = StringVar()
		self.status_row_1_antenna_1 = StringVar()
		self.status_row_1_antenna_2 = StringVar()
		self.status_row_1_antenna_3 = StringVar()
		self.status_row_1_antenna_4 = StringVar()
		
		self.status_row_2_antenna_0 = StringVar()
		self.status_row_2_antenna_1 = StringVar()
		self.status_row_2_antenna_2 = StringVar()
		self.status_row_2_antenna_3 = StringVar()
		self.status_row_2_antenna_4 = StringVar()
		
		self.status_row_3_antenna_0 = StringVar()
		self.status_row_3_antenna_1 = StringVar()
		self.status_row_3_antenna_2 = StringVar()
		self.status_row_3_antenna_3 = StringVar()
		self.status_row_3_antenna_4 = StringVar()
		
		self.status_row_4_antenna_0 = StringVar()
		self.status_row_4_antenna_1 = StringVar()
		self.status_row_4_antenna_2 = StringVar()
		self.status_row_4_antenna_3 = StringVar()
		self.status_row_4_antenna_4 = StringVar()
		
		self.status_name_dict = {
								"status_row_0_antenna_0":self.status_row_0_antenna_0, 
								"status_row_0_antenna_1":self.status_row_0_antenna_1,
								"status_row_0_antenna_2":self.status_row_0_antenna_2,
								"status_row_0_antenna_3":self.status_row_0_antenna_3,
								"status_row_0_antenna_4":self.status_row_0_antenna_4,
								"status_row_1_antenna_0":self.status_row_1_antenna_0, 
								"status_row_1_antenna_1":self.status_row_1_antenna_1,
								"status_row_1_antenna_2":self.status_row_1_antenna_2,
								"status_row_1_antenna_3":self.status_row_1_antenna_3,
								"status_row_1_antenna_4":self.status_row_1_antenna_4,
								"status_row_2_antenna_0":self.status_row_2_antenna_0, 
								"status_row_2_antenna_1":self.status_row_2_antenna_1,
								"status_row_2_antenna_2":self.status_row_2_antenna_2,
								"status_row_2_antenna_3":self.status_row_2_antenna_3,
								"status_row_2_antenna_4":self.status_row_2_antenna_4,
								"status_row_3_antenna_0":self.status_row_3_antenna_0, 
								"status_row_3_antenna_1":self.status_row_3_antenna_1,
								"status_row_3_antenna_2":self.status_row_3_antenna_2,
								"status_row_3_antenna_3":self.status_row_3_antenna_3,
								"status_row_3_antenna_4":self.status_row_3_antenna_4,
								"status_row_4_antenna_0":self.status_row_4_antenna_0, 
								"status_row_4_antenna_1":self.status_row_4_antenna_1,
								"status_row_4_antenna_2":self.status_row_4_antenna_2,
								"status_row_4_antenna_3":self.status_row_4_antenna_3,
								"status_row_4_antenna_4":self.status_row_4_antenna_4}
								
		# Setting up ArrowVar for the rows
		self.arrow_row_0 = StringVar()
		self.arrow_row_0.set("\u279f")
		self.arrow_row_1 = StringVar()
		self.arrow_row_2 = StringVar()
		self.arrow_row_3 = StringVar()
		self.arrow_row_4 = StringVar()
		
		self.arrow_status_dict = {
								"status_row_0_antenna_0":self.arrow_row_0, 
								"status_row_0_antenna_1":self.arrow_row_0,
								"status_row_0_antenna_2":self.arrow_row_0,
								"status_row_0_antenna_3":self.arrow_row_0,
								"status_row_0_antenna_4":self.arrow_row_0,
								"status_row_1_antenna_0":self.arrow_row_1, 
								"status_row_1_antenna_1":self.arrow_row_1,
								"status_row_1_antenna_2":self.arrow_row_1,
								"status_row_1_antenna_3":self.arrow_row_1,
								"status_row_1_antenna_4":self.arrow_row_1,
								"status_row_2_antenna_0":self.arrow_row_2, 
								"status_row_2_antenna_1":self.arrow_row_2,
								"status_row_2_antenna_2":self.arrow_row_2,
								"status_row_2_antenna_3":self.arrow_row_2,
								"status_row_2_antenna_4":self.arrow_row_2,
								"status_row_3_antenna_0":self.arrow_row_3, 
								"status_row_3_antenna_1":self.arrow_row_3,
								"status_row_3_antenna_2":self.arrow_row_3,
								"status_row_3_antenna_3":self.arrow_row_3,
								"status_row_3_antenna_4":self.arrow_row_3,
								"status_row_4_antenna_0":self.arrow_row_4, 
								"status_row_4_antenna_1":self.arrow_row_4,
								"status_row_4_antenna_2":self.arrow_row_4,
								"status_row_4_antenna_3":self.arrow_row_4,
								"status_row_4_antenna_4":self.arrow_row_4}
		
		self.arrow_row_list = [self.arrow_row_0, self.arrow_row_1, self.arrow_row_2, self.arrow_row_3, self.arrow_row_4]
		self.row_list = [0,1,2,3,4]
		
		self.current_cup_scanned_list = []
		
		self.total_cups_scanned = IntVar()
		self.total_cups_scanned.set(0)
		
		self.rfid_matrix_diagram(frame)
		
	def rfid_matrix_diagram(self, frame):
		for row, arrow in zip(self.row_list, self.arrow_row_list):
			self.row_name = Label(frame, text=str("Row " + str(row) +":"), bg="white", font=("Helvetica", int(-10*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*1)    
			self.row_name.grid(column=1, columnspan=2, row=(1+row), rowspan=1, sticky=E+N+S, padx=10, pady=(10,0))
			self.row_arrow = Label(frame, textvariable=arrow, bg="white", font=("Helvetica", int(-10*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*1)    
			self.row_arrow.grid(column=0, columnspan=1, row=(1+row), rowspan=1, sticky=E+N+S, padx=10, pady=(10,0))
		
		for antenna in range(5):
			self.antenna_name = Label(frame, text=str("A" + str(antenna) +":"), bg="white", font=("Helvetica", int(-10*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*1)    
			self.antenna_name.grid(column=(3+antenna), columnspan=1, row=0, rowspan=1, sticky=W+E+N+S, padx=10, pady=(10,0))
		
		for rfid_row in range(5):
			for antenna in range(5):
				var_status_name = ("status_row_"+str(rfid_row)+"_antenna_"+str(antenna))
				#var_label_name = ("status_row_"+str(rfid_row)+"_antenna_"+str(antenna)+"_label")
				self.var_label_name = Label(frame, textvariable=self.status_name_dict[var_status_name], bg="white", borderwidth=2, font=("Helvetica", int(-10*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*1)    
				self.var_label_name.grid(column=(3+antenna), columnspan=1, row=(1+rfid_row), rowspan=1, sticky=W+E+N+S, padx=10, pady=(10,0))
	
	def rfid_matrix_variable_updater(self):
		old_rfid_matrix = [["","",""],["","",""],["","",""]] #Initiated to allow for list comprehesion and comparison of matrices as they update
		while True:
			try:
				latest_rfid_matrix = self.RFID_ParentEnd.recv()
				print("------------- RFID MQTT EXTERNAL CLASS SENDING PIPED MSG -------------")
				print(latest_rfid_matrix)
				
				#Develop list comprehension comparison here between old rfid_matrix and latest_rfid_matrix
				row = 0
				antenna = 0
				print("-- side by side comparison below --")
				for old_list_row, new_list_row in zip(old_rfid_matrix, latest_rfid_matrix):
					for old_list_antenna_uid, new_list_antenna_uid in zip(old_list_row, new_list_row):
						if old_list_antenna_uid != new_list_antenna_uid: #comparing old uid in matrix to new uid in matrix
							print("Comparison found differences: ",old_list_antenna_uid,":", new_list_antenna_uid)
							var_status_name = ("status_row_"+str(row)+"_antenna_"+str(antenna))
							if row == 0:
								last_var_status_name_row = ("status_row_"+str(row+4)+"_antenna_"+str(antenna))
							else:
								last_var_status_name_row = ("status_row_"+str(row-1)+"_antenna_"+str(antenna))
							self.arrow_status_dict[last_var_status_name_row].set("")
							self.arrow_status_dict[var_status_name].set("\u279f")
							if new_list_antenna_uid == "":
								self.status_name_dict[var_status_name].set("")
							else:
								self.status_name_dict[var_status_name].set("!")
								registered_rfid_queue.put((new_list_antenna_uid, var_status_name))
						antenna += 1
					row += 1
					antenna = 0
				old_rfid_matrix = latest_rfid_matrix
			except Exception as e:
				print(e)
		
	def clean_cup_check_updater(self):
		'''  ---  Assesses rfid's passed to the rfid registered queue, checks their clean condition and updates their status on the GUI  ---  '''
		while True:
			try:
				latest_registered_cup = registered_rfid_queue.get()
				print("latest rigistered cup for clean condition checking recieved: ", latest_registered_cup)
				clean_condition = server1.admin_return_cup_clean_condition(latest_registered_cup[0])
				if clean_condition:
					self.status_name_dict[latest_registered_cup[1]].set("\u2713")
				else:
					self.status_name_dict[latest_registered_cup[1]].set("X")
			except Exception as e:
				print("Exception occured whilst checking clean cup in rfid matrix scanner, exception: ", e)
				
			
		
	def launch_rfid_mqtt_scanning(self):
		(self.RFID_ParentEnd, RFID_ChildEnd) = Pipe()
		external_rfid_mqtt_class = rfid_multiplex_mqtt_listener(5, 5)
		external_rfid_mqtt_class.launch_mqtt_listener(RFID_ChildEnd)
		_thread.start_new_thread(self.rfid_matrix_variable_updater, ())
		_thread.start_new_thread(self.clean_cup_check_updater, ())
		
	def disconnect_rfid_mqtt(self):
		external_rfid_mqtt_class.manual_disconnect()
		
class Admin_database_additions_frame(Admin_Options_Home_Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, parent, width=main_frame_size.width, height=main_frame_size.height, bg="light blue")
		self.focus_set()
		# self.focus_force() 														# must set focus to Frame for button binds to work
		self.grid_location(0, 0) 													# setting frame starting location in root window
		# setting row sizes my runnning repeat row configures, rows and columns in .grid start at value of zero (0).
		for r in range(0, 8):
			self.grid_rowconfigure(r, minsize=main_frame_size.row_size_8)
		for c in range(0, 9):
			self.grid_columnconfigure(c, minsize=main_frame_size.column_size_10*10/9)

		self.grid(sticky=W+E+N+S)													# Sticky W+E+N+S causes grid to expand to frame size
		self.after(50, lambda: self.make_widgets())
		mainscreen.back_button_press_screen = Admin_Options_Home_Frame
		self.back_button_generic()
		
	def make_widgets(self):
		Add_new_cups_button = Button(self, text="ADD NEW CUPS TO SYSTEM", bg="orange", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)),  bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_add_new_cups_frame,"","","","",""))
		Add_new_cups_button.grid(column=0, columnspan=3, row=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Add_new_boxes_button = Button(self, text="ADD NEW DELIVERY BOXES TO SYSTEM", bg="orange", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_add_new_boxes_frame,"","","","",""))
		Add_new_boxes_button.grid(column=3, columnspan=3, row=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Add_new_cafe_button = Button(self, text="ADD NEW CAFE TO SYSTEM", bg="orange", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_add_new_cafe_frame,"","","","",""))
		Add_new_cafe_button.grid(column=6, columnspan=3, row=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Admin_add_new_bike_frame_button = Button(self, text="ADD NEW VEHICLE TO SYSTEM", bg="orange", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_add_new_bike_frame,"","","","",""))
		Admin_add_new_bike_frame_button.grid(column=0, columnspan=3, row=4, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Admin_unregister_rfid_from_database = Button(self, text="UNREGISTER RFID", bg="red", fg="white", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_unregister_rfid,"","","","",""))
		Admin_unregister_rfid_from_database.grid(column=6, columnspan=3, row=6, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		
		
class Admin_bean_drop_process_cycle_transfers(Admin_Options_Home_Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, parent, width=main_frame_size.width, height=main_frame_size.height, bg="light blue")
		self.focus_set()
		# self.focus_force() 														# must set focus to Frame for button binds to work
		self.grid_location(0, 0) 													# setting frame starting location in root window
		# setting row sizes my runnning repeat row configures, rows and columns in .grid start at value of zero (0).
		for r in range(0, 8):
			self.grid_rowconfigure(r, minsize=main_frame_size.row_size_8)
		for c in range(0, 9):
			self.grid_columnconfigure(c, minsize=main_frame_size.column_size_10*10/9)

		self.grid(sticky=W+E+N+S)													# Sticky W+E+N+S causes grid to expand to frame size
		self.after(50, lambda: self.make_widgets())
		mainscreen.back_button_press_screen = Admin_Options_Home_Frame
		self.back_button_generic()
		
	def make_widgets(self):
		Add_cups_to_delivery_box_button = Button(self, text="ADD CUPS TO DELIVERY BOX", bg="#34f6f1", font=("Helvetica", int(-15*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_add_cups_to_boxes_frame,"","","","",""))
		Add_cups_to_delivery_box_button.grid(column=3, columnspan=3, row=0, rowspan=1, sticky=W+E+N+S, padx=10, pady=(10,0))
		Add_cups_to_delivery_box_button_stylized = Button(self, text="(STYLED FRAME)", bg="#34f6f1", font=("Helvetica", int(-15*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_add_cups_to_boxes_frame_styled,"","","","",""))
		Add_cups_to_delivery_box_button_stylized.grid(column=3, columnspan=3, row=1, rowspan=1, sticky=W+E+N+S, padx=10, pady=(0,10))
		Add_delivery_box_to_bike_button = Button(self, text="ADD DELIVERY BOX TO BIKE", bg="#34f6f1", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Add_delivery_boxes_to_bike_frame,"","","","",""))
		Add_delivery_box_to_bike_button.grid(column=6, columnspan=3, row=0, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Deliver_box_to_cafe_button = Button(self, text="DELIVER BOX OF CUPS TO CAFE", bg="#34f6f1", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_deliver_delivery_boxes_to_cafes,"","","","",""))
		Deliver_box_to_cafe_button.grid(column=0, columnspan=3, row=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Return_Cup_to_Bean_Drop_Station_button = Button(self, text="RETURN CUP TO BEAN DROP STATION", bg="#34f6f1", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_return_cups_to_bean_drop_station_options_frame,"",0,"","",""))
		Return_Cup_to_Bean_Drop_Station_button.grid(column=3, columnspan=3, row=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Wash_cup_button = Button(self, text="WASH CUPS", bg="#34f6f1", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_wash_cups_frame,"","","","",""))
		Wash_cup_button.grid(column=6, columnspan=3, row=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Review_quarantined_cups_button = Button(self, text="REVIEW QUARANTINED CUPS", bg="#34f6f1", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_add_new_cups_frame,"","","","",""))
		Review_quarantined_cups_button.grid(column=0, columnspan=3, row=4, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Collect_cups_from_BD_station_button = Button(self, text="COLLECT CUPS FROM BEAN DROP STATION", bg="#34f6f1", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_collect_cups_from_bd_station_frame,"","","","",""))
		Collect_cups_from_BD_station_button.grid(column=3, columnspan=3, row=4, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Empty_delivery_vehicle_button = Button(self, text="EMPTY DELIVERY VEHICLE", bg="#34f6f1", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_empty_delivery_vehicle_completely,"","","","",""))
		Empty_delivery_vehicle_button.grid(column=6, columnspan=3, row=4, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		
		
class Admin_various_admin_transfers_frame(Admin_Options_Home_Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, parent, width=main_frame_size.width, height=main_frame_size.height, bg="light green")
		self.focus_set()
		# self.focus_force() 														# must set focus to Frame for button binds to work
		self.grid_location(0, 0) 													# setting frame starting location in root window
		# setting row sizes my runnning repeat row configures, rows and columns in .grid start at value of zero (0).
		for r in range(0, 8):
			self.grid_rowconfigure(r, minsize=main_frame_size.row_size_8)
		for c in range(0, 9):
			self.grid_columnconfigure(c, minsize=main_frame_size.column_size_10*10/9)

		self.grid(sticky=W+E+N+S)													# Sticky W+E+N+S causes grid to expand to frame size
		self.after(50, lambda: self.make_widgets())
		mainscreen.back_button_press_screen = Admin_Options_Home_Frame
		self.back_button_generic()
		
	def make_widgets(self):
		Remove_cups_from_box_and_return_to_BD_button = Button(self, text="REMOVE CUPS FROM DELIVERY BOX AND RETURN TO BEAN DROP OWNERSHIP", bg="white", font=("Helvetica", int(-20*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_remove_cups_from_boxes_frame,"","","","",""))
		Remove_cups_from_box_and_return_to_BD_button.grid(column=3, columnspan=3, row=0, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Return_delivery_box_to_BD_button = Button(self, text="RETURN DELIVERY BOXES TO BEAN DROP", bg="white", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_return_delivery_box_to_BD,"","","","",""))
		Return_delivery_box_to_BD_button.grid(column=0, columnspan=3, row=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Empty_delivery_box_button = Button(self, text="EMPTY DELIVERY BOXES", bg="white", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_Empty_delivery_boxes_frame,"","","","",""))
		Empty_delivery_box_button.grid(column=6, columnspan=3, row=0, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Admin_remove_delivery_boxes_from_delivery_vehicle_button = Button(self, text="REMOVE DELIVERY BOXES FROM BIKE", bg="white", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_remove_delivery_boxes_from_delivery_vehicle,"","","","",""))
		Admin_remove_delivery_boxes_from_delivery_vehicle_button.grid(column=3, columnspan=3, row=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Admin_empty_bds_delivery_bags_from_delivery_vehicle_button = Button(self, text="EMPTY BDS DELIVERY BAGS FROM BIKE", bg="white", font=("Helvetica", int(-20*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2.5, command =lambda: self.launch_selected_frame(Admin_empty_bds_bags_from_delivery_vehicle,"","","","",""))
		Admin_empty_bds_delivery_bags_from_delivery_vehicle_button.grid(column=6, columnspan=3, row=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		
        
class Admin_add_new_cups_frame(Admin_Options_Home_Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, parent, width=main_frame_size.width, height=main_frame_size.height, bg="white")
		self.focus_set()
		# self.focus_force() 														# must set focus to Frame for button binds to work
		self.grid_location(0, 0) 													# setting frame starting location in root window
		# setting row sizes my runnning repeat row configures, rows and columns in .grid start at value of zero (0).
		for r in range(0, 8):
			self.grid_rowconfigure(r, minsize=main_frame_size.row_size_8)
		for c in range(0, 10):
			self.grid_columnconfigure(c, minsize=main_frame_size.column_size_10)
		
		self.rfid_info_var = StringVar()
		self.rfid_info_var.set("")
		
		self.rfid_value_var = StringVar()
		self.rfid_value_var.set("")
		
		self.new_rfid_cups_added = IntVar()
		self.new_rfid_cups_added.set(0)
		
		self.grid(sticky=W+E+N+S)													# Sticky W+E+N+S causes grid to expand to frame size
		self.make_widgets()
		mainscreen.back_button_press_screen = Admin_database_additions_frame
		self.back_button_generic()
		
		
		
		self.launch_rfid_scanning()
		self.variable_updater()

	def make_widgets(self):
		Scan_new_cups_label = Label(self, text="SCAN NEW CUPS TO ADD THEM TO CUP_DB", bg="white", font=("Helvetica", int(-40*main_frame_size.auto_text_scale_factor)), wraplength=main_frame_size.column_size_10*8)
		Scan_new_cups_label.grid(column=2, columnspan=6, row=0, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Number_of_new_cups_label_title = Label(self, text="Number of new cups added to the server:", bg="white", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor), "italic"), wraplength=main_frame_size.column_size_10*7)
		Number_of_new_cups_label_title.grid(column=2, columnspan=6, row=2, rowspan=1, sticky=W+E+N+S, padx=10, pady=10)
		Number_of_new_cups_label = Label(self, textvariable=self.new_rfid_cups_added, bg="white", font=("Helvetica", int(-70*main_frame_size.auto_text_scale_factor)), wraplength=main_frame_size.column_size_10*7)
		Number_of_new_cups_label.grid(column=2, columnspan=6, row=3, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		Last_RFID_UID_label_title = Label(self, text="Last RFID scanned: ", bg="white", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), wraplength=main_frame_size.column_size_10*7)
		Last_RFID_UID_label_title.grid(column=2, columnspan=3, row=5, rowspan=1, sticky=E+N+S, pady=10)
		Last_RFID_UID_label = Label(self, textvariable=self.rfid_value_var, bg="white", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)), wraplength=main_frame_size.column_size_10*7)
		Last_RFID_UID_label.grid(column=5, columnspan=3, row=5, rowspan=1, sticky=W+N+S, pady=10)
		Cup_already_registered_warning_label = Label(self, textvariable=self.rfid_info_var, bg="white", fg="red", font=("Helvetica italic", int(-25*main_frame_size.auto_text_scale_factor)), wraplength=main_frame_size.column_size_10*7)
		Cup_already_registered_warning_label.grid(column=2, columnspan=6, row=7, rowspan=1, sticky=E+W+N+S, pady=10)
		
	def variable_updater(self):
		if self.rfid_value_var.get() != main_screen_variables.variable_3:
			self.rfid_value_var.set(main_screen_variables.variable_3)
			if main_screen_variables.variable_2 == "RFID availible for addition to database and linking to new delivery vehicle.":
				self.rfid_info_var.set("")		# clearing warning of incorrect values that may exist beforehand.
				current_time = datetime_formatted()
				variables = (main_screen_variables.variable_3, Bean_drop_processing_centre.cafe_id, 0, current_time, current_time, BD_charge.cup_deposit)
				cup_added = server1.admin_add_bean_drop_cups_to_server(variables)
				if cup_added == True:
					self.new_rfid_cups_added.set((self.new_rfid_cups_added.get()+1))
			else:
				self.rfid_info_var.set(main_screen_variables.variable_2)	#Updating to show there is an error with the last scanned rfid tag
		self.after(100, lambda: self.variable_updater())
		
	def launch_rfid_scanning(self):
		cup_scanner.scanning_operation = "IDENTIFY_RFID"
		cup_scanner.scanning_status = True
			
class Admin_add_new_bike_frame(Admin_Options_Home_Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, parent, width=main_frame_size.width, height=main_frame_size.height, bg="white")
		self.focus_set()
		# self.focus_force() 														# must set focus to Frame for button binds to work
		self.grid_location(0, 0) 													# setting frame starting location in root window
		# setting row sizes my runnning repeat row configures, rows and columns in .grid start at value of zero (0).
		for r in range(0, 8):
			self.grid_rowconfigure(r, minsize=main_frame_size.row_size_8)
		for c in range(0, 10):
			self.grid_columnconfigure(c, minsize=main_frame_size.column_size_10)

		self.grid(sticky=W+E+N+S)													# Sticky W+E+N+S causes grid to expand to frame size
		mainscreen.back_button_press_screen = Admin_database_additions_frame
		self.back_button_generic()
		
		self.launch_rfid_scanning()
		
		self.text_instruction_var = StringVar()
		self.text_instruction_var.set("SCAN RFID ON NEW DELIVERY VEHICLE")
		
		self.confirmation_button_var = StringVar()
		self.confirmation_button_var.set("PRESS TO CONFIRM RFID")
		
		self.rfid_info_var = StringVar()		#Linked to main_screen_variables.variables2
		self.rfid_info_var.set("")
		
		self.description_of_vehicle = StringVar()
		self.description_of_vehicle.set("")
		
		self.vehicle_name = StringVar()
		self.vehicle_name.set("")
		
		self.replacement_var = IntVar()
		self.maintance_freq_var = IntVar()
		self.cleaning_freq_var = IntVar()
		
		steps_frame = Frame(self, width=main_frame_size.column_size_10*2, height=main_frame_size.row_size_8*3, bg="black", relief = FLAT)
		steps_frame.grid(column=0, columnspan=2, row=1, rowspan=7, sticky=W+E+N+S, padx=5, pady=5)
		self.step_1_title_label = Label(self, text="STEP 1: \nSCAN RFID ON NEW \nDELIVERY VEHICLE", bg="green", font=("Helvetica", int(-16*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*3)    
		self.step_1_title_label.grid(column=0, columnspan=2, row=1, rowspan=1, sticky=W+E+N+S, padx=10, pady=(10,0))
		self.step_2_title_label = Label(self, text="STEP 2: \nENTER VEHICLE \nDESCRIPTION", bg="white", font=("Helvetica", int(-16*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*3)    
		self.step_2_title_label.grid(column=0, columnspan=2, row=2, rowspan=1, sticky=W+E+N+S, padx=10)
		self.step_3_title_label = Label(self, text="STEP 3: \nENTER VEHICLE \nNAME", bg="white", font=("Helvetica", int(-16*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*3)    
		self.step_3_title_label.grid(column=0, columnspan=2, row=3, rowspan=1, sticky=W+E+N+S, padx=10)
		self.step_4_title_label = Label(self, text="STEP 4: \nENTER REPLACEMENT \nVALUE", bg="white", font=("Helvetica", int(-16*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*3)    
		self.step_4_title_label.grid(column=0, columnspan=2, row=4, rowspan=1, sticky=W+E+N+S, padx=10)
		self.step_5_title_label = Label(self, text="STEP 5: \nENTER CLEANING \nFREQUENC", bg="white", font=("Helvetica", int(-16*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*3)    
		self.step_5_title_label.grid(column=0, columnspan=2, row=5, rowspan=1, sticky=W+E+N+S, padx=10)
		self.step_6_title_label = Label(self, text="STEP 6: \nENTER MAINTENANCE \nFREQUENCY", bg="white", font=("Helvetica", int(-16*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*3)    
		self.step_6_title_label.grid(column=0, columnspan=2, row=6, rowspan=1, sticky=W+E+N+S, padx=10)
		self.step_7_title_label = Label(self, text="STEP 7: \nCONFIRM ENTRY", bg="white", font=("Helvetica", int(-16*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*3)    
		self.step_7_title_label.grid(column=0, columnspan=2, row=7, rowspan=1, sticky=W+E+N+S, padx=10, pady=(0,10))
		self.current_step = 1
		self.green_fade_counter = 0
		self.green_fade_out = True
		main_screen_variables.variable_1 = self.step_1_title_label
		self.blinking_widget(main_screen_variables)
		self.make_widgets()
		self.step_1_rfid_info()
		self.variable_updater()		
		
		
	def make_widgets(self):
		main_instruction_label = Label(self, textvariable=self.text_instruction_var, bg="white", font=("Helvetica", int(-30*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*6)    
		main_instruction_label.grid(column=3, columnspan=6, row=0, rowspan=2, sticky=W+E+N+S, padx=10, pady=(10,0))
		next_step_button = Button(self, textvariable=self.confirmation_button_var, bg="#55ff33", font=("Helvetica", int(-30*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*8, command =lambda: self.completed_steps(main_screen_variables))    
		next_step_button.grid(column=3, columnspan=6, row=6, rowspan=1, sticky=W+E+N+S, padx=10, pady=10)
		
	def step_1_rfid_info(self):
		self.rfid_scan_response_label = Label(self, textvariable=self.rfid_info_var, bg="white", fg="red", font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor), "italic"), relief=FLAT, wraplength=main_frame_size.column_size_10*6)    
		self.rfid_scan_response_label.grid(column=3, columnspan=6, row=2, rowspan=2, sticky=W+E+N+S, padx=10, pady=(10,0))
		
	def description_text_entry_widget(self):
		self.description_text_entry = Text(self, bg = "light blue", bd=2, width = 30, height = 3, font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)))
		self.description_text_entry.insert(INSERT,"A short description of the vehicle including it's name, brand, model and its purpose.")
		self.description_text_entry.grid(column=3, columnspan=6, row=2, rowspan=3, sticky=W+E+N+S)
		
	def step_entry_widget(self, text_var_for_step):
		self.step_value_entry = Entry(self, bg = "light blue", bd=2, textvariable=text_var_for_step, font=("Helvetica", int(-25*main_frame_size.auto_text_scale_factor)))
		self.step_value_entry.grid(column=3, columnspan=6, row=2, rowspan=1, sticky=W+E+N+S)
		
	def int_warning_lable(self):
		self.int_only_warning_lable = Label(self, text="Whole numbers are the only values excepted. Please remove any letters or other non-numerical characters from the entry.", bg="white", fg="red", font=("Helvetica", int(-20*main_frame_size.auto_text_scale_factor), "italic"), relief=FLAT, wraplength=main_frame_size.column_size_10*6)    
		self.int_only_warning_lable.grid(column=3, columnspan=6, row=3, rowspan=2, sticky=W+E+N+S, padx=10, pady=(10,0))
		
	def new_entry_summary(self):
		new_entry_summary_text = ("\nNew vehicle rfid: ", str(main_screen_variables.variable_3),
									"\nVehicle description: ", str(self.description_of_vehicle.get()),
									"\nVehicle name: ", str(self.vehicle_name.get()),
									"\nReplacement value: £", str(self.replacement_var.get()),
									"\nCleaning frequency (Trips/clean): ", str(self.cleaning_freq_var.get()),
									"\nMaintenance frequency (Trips/maintenance): ", str(self.maintance_freq_var.get())) 
		new_entry_summary_text_formatted = "".join(new_entry_summary_text)							
		summary_label_rfid_tag = Label(self, text=new_entry_summary_text_formatted, bg="white", font=("Helvetica", int(-20*main_frame_size.auto_text_scale_factor)), relief=FLAT, wraplength=main_frame_size.column_size_10*6)    
		summary_label_rfid_tag.grid(column=3, columnspan=6, row=2, rowspan=4, sticky=W+E+N+S, padx=10, pady=(10,0))
		
	def selected_server_update_operation(self):
		current_time = datetime_formatted()
		cleaning_freq = self.cleaning_freq_var.get()
		maintenance_frq = self.maintance_freq_var.get()
		replacement_val =  self.replacement_var.get()
		vehicle_description =  str(self.description_of_vehicle.get())
		vehicle_name = str(self.vehicle_name.get())
		result = server1.admin_add_bean_drop_delivery_vehicle_to_server(Bean_drop_processing_centre.cafe_id, current_time, cleaning_freq, maintenance_frq, replacement_val, vehicle_description,main_screen_variables.variable_3, vehicle_name)
		print(result)
		
	def completed_steps(self, screen_number_class):
		step_label_titles = {1:self.step_1_title_label, 2: self.step_2_title_label, 3:self.step_3_title_label, 4:self.step_4_title_label, 5:self.step_5_title_label, 6:self.step_6_title_label, 7:self.step_7_title_label}
		step_instructions = {1:"SCAN RFID ON NEW DELIVERY VEHICLE", 
								2:"ENTER A BRIEF VEHICLE DESCRIPTION",
								3:"ENTER A VEHICLE NAME", 
								4:"ENTER REPLACEMENT VALUE OF THE VEHICLE IN £", 
								5:"ENTER CLEANING FREQUENCY AS THE NUMBER OF VEHICLE TRIPS BETWEEN CLEANING", 
								6:"ENTER MAINTENANCE FREQUENCY AS THE NUMBER OF VEHICLE TRIPS BETWEEN MAINTENANCE", 
								7:"CHECK THE DETAILS ARE CORRECT AND CONFIRM ENTRY",
								8:""}
								
		step_button_confirmation_titles = {1:"PRESS TO CONFIRM RFID", 
								2:"PRESS TO CONFIRM DESCRIPTION",
								3:"PRESS TO CONFIRM NAME",
								4:"PRESS TO CONFIRM VALUE", 
								5:"PRESS TO CONFIRM CLEANING", 
								6:"PRESS TO CONFIRM MAINTENANCE", 
								7:"PRESS TO SUBMIT TO DATABASE",
								8:""}
								
		step_variables = {1:self.rfid_info_var,
							2:self.description_of_vehicle,
							3:self.vehicle_name,
							4:self.replacement_var,
							5:self.cleaning_freq_var,
							6:self.maintance_freq_var}
		
		#Removing any old warning lables
		try:
			self.int_only_warning_lable.grid_forget()
		except Exception as e:
			print(e)
		
		#Checking data entry to Int entry widget is only int and not str
		try:
			if self.current_step == 1 and self.rfid_info_var.get() != "RFID availible for addition to database and linking to new delivery vehicle.":
				print("FREE RFID NOT REGISTERED IN SYSTEM, BLOCKED AND WARNING RAISED")
				raise Exception
			elif self.current_step == 4 or self.current_step == 5 or self.current_step == 6:
				int(self.step_value_entry.get())
		except ValueError:
			print("Couldnt convert value into int")
			self.int_warning_lable()
		except Exception as e:
			print(e)
		else:
							
			try:
				step_variables[self.current_step] = self.step_value_entry.get()
				print("Current Step Variables are:",
						"\nrfid_info_var: ", self.rfid_info_var.get(),
						"\ndescription_text_entry: ", self.description_of_vehicle.get(),
						"\nVehicle name: ", str(self.vehicle_name.get()),
						"\nreplacement_var: ", self.replacement_var.get(),
						"\ncleaning_freq_var: ", self.cleaning_freq_var.get(),
						"\nmaintance_freq_var: ", self.maintance_freq_var.get())
			except Exception as e:
				print(e)
				
			
			self.current_step += 1
			self.text_instruction_var.set(step_instructions[self.current_step])
			self.confirmation_button_var.set(step_button_confirmation_titles[self.current_step])
			
			
			print(self.current_step)
			for step_number in step_label_titles:
				if step_number < self.current_step:
					step_label_titles[step_number].config(bg="#55ff33")
				elif step_number == self.current_step:
					screen_number_class.variable_1 = step_label_titles[step_number]
				elif step_number > self.current_step:
					step_label_titles[step_number].config(bg="white")
					
			if self.current_step == 2:
				try:
					self.description_text_entry_widget()
					self.rfid_scan_response_label.grid_forget()
					self.pause_scanning()
				except Exception as e:
					print(e)
			elif self.current_step == 3:
				try:
					self.description_of_vehicle.set(self.description_text_entry.get('1.0','end'))
					print(self.description_of_vehicle.get())
					self.description_text_entry.grid_forget()
					self.step_entry_widget(self.vehicle_name)
				except Exception as e:
					print(e)
			elif self.current_step == 4 or self.current_step == 5 or self.current_step == 6:
				try:
					self.step_value_entry.grid_forget()
					self.step_entry_widget(step_variables[self.current_step])
				except Exception as e:
					print(e)
			elif self.current_step == 7:
				try:
					self.step_value_entry.grid_forget()
					self.new_entry_summary()
				except Exception as e:
					print(e)
			elif self.current_step == 8:
				self.selected_server_update_operation()
	
	def variable_updater(self):
		if self.rfid_info_var != main_screen_variables.variable_2:
			self.rfid_info_var.set(main_screen_variables.variable_2)
		self.after(100, lambda: self.variable_updater())
		
	def launch_rfid_scanning(self):
		cup_scanner.scanning_operation = "IDENTIFY_RFID"
		cup_scanner.scanning_status = True
		
	def pause_scanning(self):
		cup_scanner.scanning_status = False
		
class Admin_add_new_cafe_frame(Admin_Options_Home_Frame):
	pass
		
		
class Admin_unregister_rfid(Admin_Options_Home_Frame):
	pass
			
class Admin_add_new_boxes_frame(Admin_Options_Home_Frame):
	pass
			
class Admin_add_cups_to_boxes_frame_styled(Admin_Options_Home_Frame):
	pass
			
class Admin_add_cups_to_boxes_frame(Admin_Options_Home_Frame):
	pass

class Admin_rfid_matrix_scanner_frame(Admin_Options_Home_Frame):
	pass
				
class Admin_remove_cups_from_boxes_frame(Admin_Options_Home_Frame):
	pass
		
class Admin_Empty_delivery_boxes_frame(Admin_Options_Home_Frame):
	pass
		

class Admin_remove_delivery_boxes_from_delivery_vehicle(Admin_Options_Home_Frame):
	pass


class Admin_return_delivery_box_to_BD(Admin_Options_Home_Frame):
	pass
		
class Admin_empty_bds_bags_from_delivery_vehicle(Admin_Options_Home_Frame):
	pass
		
class Admin_empty_delivery_vehicle_completely(Admin_Options_Home_Frame):
	pass
		
class Admin_deliver_delivery_boxes_to_cafes(Admin_Options_Home_Frame):
	pass
		
class Admin_collect_cups_from_bd_station_frame(Admin_Options_Home_Frame):
	pass

class Add_delivery_boxes_to_bike_frame(Admin_Options_Home_Frame):
	pass
					
class Admin_return_cups_to_bean_drop_station_options_frame(Frame):
	pass

class Admin_return_cups_to_bean_drop_station_process_frame(Frame):
	pass
		
class Admin_wash_cups_frame(Admin_Options_Home_Frame):
	pass

class Admin_identify_rfid_owner(Admin_Options_Home_Frame):
	pass
			
class Bean_Drop_Cup_monitoring(Admin_Options_Home_Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, parent, width=main_frame_size.width, height=main_frame_size.height, bg="white")
		self.focus_set()
		# self.focus_force() 														# must set focus to Frame for button binds to work
		self.grid_location(0, 0) 													# setting frame starting location in root window
		# setting row sizes my runnning repeat row configures, rows and columns in .grid start at value of zero (0).
		for r in range(0, 8):
			self.grid_rowconfigure(r, minsize=main_frame_size.row_size_8)
		for c in range(0, 10):
			self.grid_columnconfigure(c, minsize=main_frame_size.column_size_10)

		self.grid(sticky=W+E+N+S)													# Sticky W+E+N+S causes grid to expand to frame size
		self.selected_graph = "bd_stations"
		#self.update_cup_records_on_graph()
		self.back_button_generic()
		mainscreen.back_button_press_screen = Admin_Options_Home_Frame
		self.select_graph_widgets()
		
		self.processing_centre_cup_numbers = 1
		self.cafe_cup_numbers = 1
		self.customer_cup_numbers = 1
		self.cup_totals = 2
		
		self.original_bd_stations_dict = {}
		self.beandrop_stations_result = server1.admin_recall_bean_drop_station_dictionary_details()
		for station in self.beandrop_stations_result:
			print(station)
			self.original_bd_stations_dict[station[3]] = (station[10],station[8])
			
		self.original_cafes_dict = {}
		self.cafes_result = server1.admin_recall_cafe_details()
		for cafe in self.cafes_result:
			print(cafe)
			cafe_current_cup_stock = server1.old_owner_details_bluehost(cafe[1])			
			self.original_cafes_dict[cafe[2]] = (cafe_current_cup_stock[3], cafe[8])

		#self.plot_graph()
		self.plot_multi_graph()
		self.update_cup_records_on_graph()
		self.after(1000, lambda: self.Update_Frame())
		
	def select_graph_widgets(self):
		bd_station_monitoring_selection = Button(self, text="BD STATIONS", bg="light green", font=("Helvetica", int(-20*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2, command = lambda: self.select_graph_command("bd_stations"))    
		bd_station_monitoring_selection.grid(column=3, columnspan=2, row=0, rowspan=1, sticky=W+E+N+S, padx=10, pady=10)
		cafes_monitoring_selection = Button(self, text="CAFES", bg="orange", font=("Helvetica", int(-20*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2, command = lambda: self.select_graph_command("cafes"))    
		cafes_monitoring_selection.grid(column=5, columnspan=2, row=0, rowspan=1, sticky=W+E+N+S, padx=10, pady=10)
		overview_selection_button = Button(self, text="OVERVIEW", bg="light blue", font=("Helvetica", int(-20*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, wraplength=main_frame_size.column_size_10*2, command = lambda: self.select_graph_command("overview"))    
		overview_selection_button.grid(column=7, columnspan=2, row=0, rowspan=1, sticky=W+E+N+S, padx=10, pady=10)
		
	def select_graph_command(self, selected_graph):
		self.selected_graph = selected_graph
		print(self.selected_graph)
		self.plot_multi_graph()
		
	def plot_graph(self):
		width = 6 * main_frame_size.auto_text_scale_factor
		height = 5 * main_frame_size.auto_text_scale_factor
		plt.rcParams['figure.figsize'] = [width, height]
		fig, ax = plt.subplots()#figure(figsize=(6,6), dpi=100)
		labels = ['Processing Centre', 'Cafe', 'Bean Drop Station']
		cup_numbers = [main_screen_variables.variable_1 , main_screen_variables.variable_2 , main_screen_variables.variable_3 ]
		ax.bar(labels, cup_numbers, align='center', alpha=1.0)
		canvas = FigureCanvasTkAgg(fig, master = self)
		canvas.draw()
		canvas.get_tk_widget().grid(row=1, column=0, rowspan = 6, columnspan = 10, pady=10)
		
	def plot_multi_graph(self):
		
		if self.selected_graph == "bd_stations":
			bd_stations_name_list = []
			bd_stations_name_number = []
			bd_stations_name_extra_capacity = []
			for station in self.original_bd_stations_dict:
				bd_stations_name_list.append(station)
				bd_stations_name_number.append(self.original_bd_stations_dict[station][0])
				bd_stations_name_extra_capacity.append(self.original_bd_stations_dict[station][1]-self.original_bd_stations_dict[station][0])
			x_axis_list = bd_stations_name_list
			y_axis_list = bd_stations_name_number
			y_axis_capcity_additional = bd_stations_name_extra_capacity
			
		if self.selected_graph == "cafes":
			print("selected graph is cafes")
			cafes_name_list = []
			cafes_name_number = []
			cafes_name_empty_capacity = []
			for cafe in self.original_cafes_dict:
				cafes_name_list.append(cafe)
				cafes_name_number.append(self.original_cafes_dict[cafe][0])
				cafes_name_empty_capacity.append(self.original_cafes_dict[cafe][1]-self.original_cafes_dict[cafe][0])
			x_axis_list = cafes_name_list
			y_axis_list = cafes_name_number
			y_axis_capcity_additional = cafes_name_empty_capacity
			print(cafes_name_empty_capacity)
			
		if self.selected_graph == "overview":
			print("selected graph is overview")
			cup_overview_location_list = ["Bean Drop", "Cafes", "Customers"]
			cup_overview_location_numbers = [self.processing_centre_cup_numbers, self.cafe_cup_numbers, self.customer_cup_numbers]
			pie_labels = cup_overview_location_list
			pie_figures = cup_overview_location_numbers
			
		width = 6 * main_frame_size.auto_text_scale_factor
		height = 5 * main_frame_size.auto_text_scale_factor
		plt.rcParams['figure.figsize'] = [width, height]
		plt.rcParams['figure.autolayout'] = True	#Used to automatically fit plot into figure size
		fig, ax = plt.subplots()#figure(figsize=(6,6), dpi=100)
		if self.selected_graph == "bd_stations":
			p1 = ax.bar(x_axis_list, y_axis_list, align='center', alpha=1.0, color="orange", edgecolor="red")
			ax.bar(x_axis_list, y_axis_capcity_additional, align='center', alpha=1.0, bottom = y_axis_list, label = "Capacity", color="white", edgecolor="red")
			ax.set_xticklabels(x_axis_list, fontsize = 'x-small')
			ax.bar_label(p1 ,label_type = 'edge')
			for tick in ax.get_xticklabels():
				tick.set_rotation(55)
		if self.selected_graph == "cafes":
			p1 = ax.bar(x_axis_list, y_axis_list, align='center', alpha=1.0, color="#75FF00", edgecolor="green")
			ax.bar(x_axis_list, y_axis_capcity_additional, align='center', alpha=1.0, bottom = y_axis_list, label = "Capacity", color="white", edgecolor="green")
			ax.set_xticklabels(x_axis_list, fontsize = 'x-small')
			ax.bar_label(p1 ,label_type = 'edge')
			for tick in ax.get_xticklabels():
				tick.set_rotation(55)
		if self.selected_graph == "overview":
			ax.pie(pie_figures, labels=pie_labels, autopct='%1.1f%%') #autopct='%1.1f%%'
			ax.axis('equal')
		canvas = FigureCanvasTkAgg(fig, master = self)
		canvas.draw()
		canvas.get_tk_widget().grid(row=1, column=0, rowspan = 6, columnspan = 10, pady=10)
	
	def update_cup_records_on_graph(self):
		#_thread.start_new_thread(self.return_cup_ownership_details_for_graph, ())
		_thread.start_new_thread(self.return_cup_ownership_details_multi_stations_graph, ())
		
	def Update_Frame(self):  # dataqueue is not capturing or not updating. Register_cups() method is always running and passing in polling method
		print("Frame trying to update")
		self.update_cup_records_on_graph()
		self.after(3000, lambda: self.Update_Frame())
		
	def return_cup_ownership_details_multi_stations_graph(self):
		update_condition = False
		if self.selected_graph == "bd_stations":
			beandrop_stations_result = server1.admin_recall_bean_drop_station_dictionary_details()
			updated_bd_station_dict = {}
			for bd_station in beandrop_stations_result:
				updated_bd_station_dict[bd_station[3]] = (bd_station[10], bd_station[8])
			for key in updated_bd_station_dict:
				if updated_bd_station_dict[key][0] != self.original_bd_stations_dict[key][0]:
					self.original_bd_stations_dict[key][0] = updated_bd_station_dict[key][0] 
					update_condition = True
		if self.selected_graph == "cafes":
			cafes_result = server1.admin_recall_cafe_details()
			updated_cafe_dict = {}
			for cafe in cafes_result:
				cafe_current_cup_stock = server1.old_owner_details_bluehost(cafe[1])			
				updated_cafe_dict[cafe[2]] = (cafe_current_cup_stock[3], cafe[8])
			print(updated_cafe_dict)
			for key in updated_cafe_dict:
				print("new_number is...:", updated_cafe_dict[key])
				print(key)
				if updated_cafe_dict[key][0] != self.original_cafes_dict[key][0]:
					self.original_cafes_dict[key][0] = updated_cafe_dict[key][0]
					update_condition = True
		if self.selected_graph == "overview":
			return_processing_centre_cup_numbers = server1.admin_return_total_cups_in_bd_processing_centres()
			return_cafe_cup_numbers = server1.admin_return_total_cups_in_cafes()
			return_cup_totals = server1.admin_return_total_cups_in_circulation()
			print("Customer cup totals being calculated")
			return_customer_cup_numbers = return_cup_totals[1] - return_cafe_cup_numbers[1] - return_processing_centre_cup_numbers[1]
			#return_bds_cup_numbers = server1 
			if return_processing_centre_cup_numbers[1] != self.processing_centre_cup_numbers or return_cafe_cup_numbers[1] != self.cafe_cup_numbers or return_cup_totals[1] != self.cup_totals:
				self.cup_totals = return_cup_totals[1]
				self.customer_cup_numbers = return_customer_cup_numbers
				self.processing_centre_cup_numbers = return_processing_centre_cup_numbers[1]
				self.cafe_cup_numbers = return_cafe_cup_numbers[1]
				update_condition = True
		if update_condition == True:
			self.plot_multi_graph()
		
	def return_cup_ownership_details_for_graph(self):
		update_condition = False
		try:
			Bean_drop_station_Ems_cups = server1.old_owner_details_bluehost(Bean_drop_station_Ems)
			if main_screen_variables.variable_1 != (Bean_drop_station_Ems_cups[3]):
				update_condition = True
			main_screen_variables.variable_1 = (Bean_drop_station_Ems_cups[3])
			#print("printing unique extraction",cup_numbers_bd_station[3])
		except Exception as e:
			print("Exception captured is:", e)
			cup_numbers_bd_station = None
		try:
			Bean_drop_cafe_cups = server1.old_owner_details_bluehost(Bean_drop_cafe.cafe_id)
			if main_screen_variables.variable_2 != (Bean_drop_cafe_cups[3]):
				update_condition = True
			main_screen_variables.variable_2 = (Bean_drop_cafe_cups[3])
		except Exception as e:
			print("Exception captured is:", e)
			main_cafe_cup_numbers = None
		try:
			Bean_drop_processing_centre_cups = server1.old_owner_details_bluehost(Bean_drop_processing_centre.cafe_id)
			if main_screen_variables.variable_3 != (Bean_drop_processing_centre_cups[3]):
				update_condition = True
			main_screen_variables.variable_3 = (Bean_drop_processing_centre_cups[3])
		except Exception as e:
			print("Exception captured is:", e)
			processing_centre_cup_numbers = None
		if update_condition == True:
			self.plot_graph()

class Re_size_screen(Admin_Options_Home_Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, parent, width=main_frame_size.width, height=main_frame_size.height, bg="white")
		self.focus_set()
		# self.focus_force() 														# must set focus to Frame for button binds to work
		self.grid_location(0, 0) 													# setting frame starting location in root window
		# setting row sizes my runnning repeat row configures, rows and columns in .grid start at value of zero (0).
		for r in range(0, 8):
			self.grid_rowconfigure(r, minsize=main_frame_size.row_size_8)
		for c in range(0, 10):
			self.grid_columnconfigure(c, minsize=main_frame_size.column_size_10)

		self.grid(sticky=W+E+N+S)													# Sticky W+E+N+S causes grid to expand to frame size
		self.back_button_generic()
		mainscreen.back_button_press_screen = Admin_Options_Home_Frame
		self.screen_resize_buttons()
		
	def screen_resize_buttons(self):
		increase_screen_size_button = Button(self, text="+", bg="light blue", font=("Helvetica", int(-40*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, command = self.increase_screen_size)    
		increase_screen_size_button.grid(column=0, columnspan=1, row=1, rowspan=1, sticky=W+E+N+S, padx=10, pady=10)
		decrease_screen_size_button = Button(self, text="-", bg="violet", font=("Helvetica", int(-40*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, command = self.decrease_screen_size)    
		decrease_screen_size_button.grid(column=0, columnspan=1, row=2, rowspan=1, sticky=W+E+N+S, padx=10, pady=10)
		
	def increase_screen_size(self):
		root.geometry('1024x600+0+0')
		main_frame_size.width = 1024
		main_frame_size.height = 600
		self.destroy()
		Re_size_screen(root)
		
		
	def decrease_screen_size(self):
		root.geometry('800x480+0+0')
		main_frame_size.width = 800
		main_frame_size.height = 480
		self.destroy()
		Re_size_screen(root)

	
class Exit_Program_Frame(Admin_Options_Home_Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, parent, width=main_frame_size.width, height=main_frame_size.height, bg="white")
		self.focus_set()
		# self.focus_force() 														# must set focus to Frame for button binds to work
		self.grid_location(0, 0) 													# setting frame starting location in root window
		# setting row sizes my runnning repeat row configures, rows and columns in .grid start at value of zero (0).
		for r in range(0, 8):
			self.grid_rowconfigure(r, minsize=main_frame_size.row_size_8)
		for c in range(0, 10):
			self.grid_columnconfigure(c, minsize=main_frame_size.column_size_10)

		self.grid(sticky=W+E+N+S)													# Sticky W+E+N+S causes grid to expand to frame size
		self.back_button_generic()
		mainscreen.back_button_press_screen = Admin_Options_Home_Frame
		self.make_widgets()
		
	def make_widgets(self):
		Quit_program_button = Button(self, text="EXIT PROGRAM", bg="RED", fg="white", font=("Helvetica", int(-40*main_frame_size.auto_text_scale_factor)), bd=5, relief=RAISED, command = self.exit_program_command)    
		Quit_program_button.grid(column=3, columnspan=4, row=3, rowspan=2, sticky=W+E+N+S, padx=10, pady=10)
		
	def exit_program_command(self):
		self.destroy()
		os._exit(1)
		quit()
		root.quit()






if __name__ == "__main__":
	server1 = server_connection_details(local_con_details.host, local_con_details.port, local_con_details.user, local_con_details.pwd, local_con_details.DB_Name, local_con_details.ssl_ca, local_con_details.ssl_cert, local_con_details.ssl_key)
	main_screen_variables = screen_variables("","","","","", 0) 																		# Setting up main variables used for transfering information across screens in GUI
	dataQueue = queue.Queue()																										# Shared global storage queue, infinite size
	registered_rfid_queue = queue.Queue()
	
	server1.connection_test()
	
	restricted_cafe_dictionary = update_restricted_cafes_list(server1)								# Populating restricted cafe_dictionary
	print("This is the restricted cafe_dictionary value [1]: ",restricted_cafe_dictionary[1])
	print("new method completed for updating restricted cafes list")

	
	print("\n\n Updating Bean Drop Station Dictionary with details \n")
	bean_drop_station_details_dictionary = update_dictionary_of_bean_drop_stations_details(server1)
	bean_drop_station_list = []
	for user_account, name in bean_drop_station_details_dictionary.items():
			print(name['name'])
			bean_drop_station_list.append(name['name'])
	
			
			
	print("\n\n Setting up the list of cafes currently in operation - a dictionary with id's and names and a cafe_name_list for easy recall \n")
	# Setting up the list of cafes currently in operation - a dictionary with id's and names and a cafe_name_list for easy recall 
	cafe_return_dict_and_list = cafe_name_and_id_recall()
	cafe_name_and_id_dict = cafe_return_dict_and_list[1]
	cafe_name_list = cafe_return_dict_and_list[2]
	
	cafe_company_return_dict_and_list = cafe_company_name_and_id_recall()
	cafe_company_name_and_id_dict = cafe_company_return_dict_and_list[1]
	cafe_company_name_list = cafe_company_return_dict_and_list[2]
	
	quick_cafe_id_list = []
	for key in cafe_name_and_id_dict:
		print(key)
		print(cafe_name_and_id_dict[key])
		quick_cafe_id_list.append(cafe_name_and_id_dict[key])
	
	quick_stations_list = []
	beandrop_stations_result = server1.admin_recall_bean_drop_station_dictionary()
	for station in beandrop_stations_result:
		print(station[0])
		quick_stations_list.append(station[0])
	
	#Launching Threaded RFID Parent Reciever loop
	rfid_listener = rfid_threaded_listener(cup_scanner, ParentEnd, dataQueue, server1, main_screen_variables)
	_thread.start_new_thread(rfid_listener.rfid_dictionary_updater,())
	
	
	root = Tk()
	root.geometry('1024x600+0+0')
	root.title('App Window')
	# root.attributes('-type', 'dock') # Removes title bar, must use focus_force

	Admin_Options_Home_Frame(root)
	root.mainloop()
