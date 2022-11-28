# Value of sales class

class Bean_drop_sales_values:
	'''This class holds the values of Bean Drop products being sold'''
	
	def __init__(self, cup_deposit, cleaning_value, cup_lid, cup_sleeve):
		self.cup_deposit = cup_deposit
		self.cleaning_value = cleaning_value
		self.cup_lid = cup_lid
		self.cup_sleeve = cup_sleeve
		
	def __str__(self):
		return 'cup_deposit: £ %s , cleaning_value: £ %s , cup_lid: £ %s , cup_sleeve: £ %s' % (self.cup_deposit, self.cleaning_value, self.cup_lid, self.cup_sleeve)
		
if __name__ == '__main__':
	BD_charge = Bean_drop_sales_values(3.00, 0.25, 0.25, 0.25)
	print(BD_charge)
