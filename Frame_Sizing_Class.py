# Frame Class
import math

class Frame_Sizing:
	'''This class is designed to modify all of the visual properties to fit screens of different sizes'''
	
	def __init__(self, width, height):
		self.width = width
		self.height = height
		
	@property
	def row_size_8(self):
		row_size_8_value = self.height / 8
		return row_size_8_value
		
	@property
	def column_size_10(self):
		column_size_10_value = self.width / 10
		return column_size_10_value
		
	@property
	def height_scale_factor_from_original(self):
		height_factor = self.height / 600
		return height_factor
		
	@property
	def width_scale_factor_from_original(self):
		width_factor = self.width / 1024
		return width_factor
		
	@property
	def auto_text_scale_factor(self):
		auto_text_scale_factor_value = (self.height_scale_factor_from_original + self.width_scale_factor_from_original)/2
		return auto_text_scale_factor_value


def text_auto(Frame_sizing_class,size):
	text_auto_value = math.floor(Frame_sizing_class.auto_text_scale_factor * int(size))
	return text_auto_value
	

