#OpenCV Program to identify dirty cups

from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import os
import subprocess
import math
import logging
import numpy

class cup_camera():
	
	def __init__(self, camera_type, camera_position, cup_position, capture_image):
		self.camera_type = camera_type
		self.camera_position = camera_position
		self.cup_position = cup_position
		self.capture_image = capture_image
		
	def simple_camera_output(self):
		if self.camera_type == "webcam":
			resolution = (720, 1280)
			vs = VideoStream(src=0, resolution=resolution).start()
		else:
			vs = VideoStream(usePiCamera=True).start()
		time.sleep(2.0)
		
		while True:
			frame = vs.read()
			cv2.imshow("frame", frame)
			key = cv2.waitKey(1) & 0xFF
			
		time.sleep(10)
		csv.close()
		cv2.destroyAllWindows()
		vs.stop()
			
			
	def capture_foreign_objects(self):
		if self.camera_type == "webcam":
			resolution = (720, 1280)
			vs = VideoStream(src=0, resolution=resolution).start()
		else:
			vs = VideoStream(usePiCamera=True).start()
		time.sleep(2.0)
		
		original_frame = vs.read()
		print("First frame captured")
		time.sleep(3)
		
		while True:
			second_frame = vs.read()
			time.sleep(0.1)
			print("Second frame captured")
			scaling_factor = 2
			original_cv2_resize = cv2.resize(original_frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
			second_frame_cv2_resize = cv2.resize(second_frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
			cv2.imshow("frame_diff", self.two_frame_diff(original_cv2_resize, second_frame_cv2_resize))
			key = cv2.waitKey(1) & 0xFF
			
		time.sleep(10)
		csv.close()
		cv2.destroyAllWindows()
		vs.stop()
		
	def capture_non_blue_objects(self):
		if self.camera_type == "webcam":
			resolution = (720, 1280)
			vs = VideoStream(src=0, resolution=resolution).start()
		else:
			vs = VideoStream(usePiCamera=True).start()
		time.sleep(2.0)
		
		original_frame = vs.read()
		print("First frame captured")
		time.sleep(3)
		
		while True:
			second_frame = vs.read()
			scaling_factor = 2
			second_frame_cv2_resize = cv2.resize(second_frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
			hsv_frame = cv2.cvtColor(second_frame_cv2_resize, cv2.COLOR_BGR2HSV)
			#Define HSV upper and lower values
			lower = numpy.array([80,50,20])
			upper = numpy.array([150,255,255])
			mask = cv2.inRange(hsv_frame, lower, upper)
			img_bitwise_and = cv2.bitwise_and(hsv_frame, hsv_frame, mask=mask)
			blurred_img = cv2.medianBlur(img_bitwise_and, 5)
			time.sleep(0.1)
			cv2.imshow("second_frame", second_frame)
			cv2.imshow("blue_frame", blurred_img)
			key = cv2.waitKey(1) & 0xFF
			
		time.sleep(10)
		csv.close()
		cv2.destroyAllWindows()
		vs.stop()
		
	def motion_capture_difference(self):
		if self.camera_type == "webcam":
			resolution = (720, 1280)
			vs = VideoStream(src=0, resolution=resolution).start()
		else:
			vs = VideoStream(usePiCamera=True).start()
		time.sleep(2.0)
		
		while True:
			time.sleep(0.1)
			frame = vs.read()
			time.sleep(0.1)
			second_frame = vs.read()
			time.sleep(0.1)
			third_frame = vs.read()
			#grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			#frame_resize = imutils.resize(frame, width=500)
			scaling_factor = 2
			frame_cv2_resize = cv2.resize(frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
			second_frame_cv2_resize = cv2.resize(second_frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
			third_frame_cv2_resize = cv2.resize(third_frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
			#cv2.imshow("Cup Preview", frame)
			#cv2.imshow("Gray Scale Preview", grey_frame)
			#cv2.imshow("Second Frame Preview", second_frame)
			cv2.imshow("frame_diff", self.three_frame_diff(frame_cv2_resize, second_frame_cv2_resize, third_frame_cv2_resize))
			key = cv2.waitKey(1) & 0xFF
			
		time.sleep(10)
		csv.close()
		cv2.destroyAllWindows()
		vs.stop() 
		
	def three_frame_diff(self, first_frame, second_frame, third_frame):
		diff = cv2.absdiff(first_frame, second_frame)
		diff2 = cv2.absdiff(second_frame, third_frame)
		return cv2.bitwise_and(diff, diff2)
		
	def two_frame_diff(self, first_frame, second_frame):
		diff = cv2.absdiff(first_frame, second_frame)
		return cv2.bitwise_and(first_frame, diff)


if __name__ == "__main__":
	
	raspi_cam = cup_camera("raspi", 1, 1, False)
	raspi_cam.simple_camera_output()
