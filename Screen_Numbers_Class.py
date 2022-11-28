#Screen Numbers Class
Cup_deposit_value = 3
Wash_value = 0.25

class screen_numbers:
    '''This class represents the numbers on the mainscreen GUI'''

    def __init__(self, threadcondition, thread_qr_code, username, user_account_number,lookup_user_account_number, entry_widget_user_number, unique_order_number, amount_of_RFID_Numbers_Registered, user_funds, cups_in_user_account, Washes_in_user_account, local_order_id, POS_hash, switching_value, variable_text_output, selected_admin_user, pin_success_to_screen, pin_fail_return_screen, back_button_press_screen):
        # This is used to raise an elif statement in polling to break thread (has a delay of 0.25 seconds the time of the thread)
        self.threadcondition = threadcondition
        self.thread_qr_code = thread_qr_code
        self.username = username
        self.user_account_number = user_account_number
        self.lookup_user_account_number = lookup_user_account_number
        self.entry_widget_user_number = entry_widget_user_number
        self.unique_order_number = unique_order_number
        self.amount_of_RFID_Numbers_Registered = amount_of_RFID_Numbers_Registered
        self.user_funds = user_funds
        self.cups_in_user_account = cups_in_user_account        #misleading, this represents the value of cups in account to be used and not number of cups they have out in use (essentially value of deposits in account divided by value of a Bean Drop Cup)
        self.Washes_in_user_account = Washes_in_user_account
        self.local_order_id = local_order_id
        self.POS_hash = POS_hash
        self.switching_value = switching_value
        self.variable_text_output = variable_text_output
        self.selected_admin_user = selected_admin_user
        self.pin_success_to_screen = pin_success_to_screen
        self.pin_fail_return_screen = pin_fail_return_screen
        self.back_button_press_screen = back_button_press_screen

    @property
    def RFIDCups_minus_account_cups(self):
        result_RFIDCups_minus_account_cups = int(self.amount_of_RFID_Numbers_Registered) - int(self.cups_in_user_account)
        if result_RFIDCups_minus_account_cups <= 0:  # If statement is to makesure a negative value cannot be returned on screen
            result_RFIDCups_minus_account_cups = 0
        return result_RFIDCups_minus_account_cups

    @property
    def RFIDCups_minus_account_washes(self):
        result_RFIDCups_minus_account_washes = int(self.amount_of_RFID_Numbers_Registered) - int(self.Washes_in_user_account)
        if result_RFIDCups_minus_account_washes <= 0:  # If statement is to makesure a negative value cannot be returned on screen
            result_RFIDCups_minus_account_washes = 0
        return result_RFIDCups_minus_account_washes

    @property
    def Beandrop_payment_value(self):
        if (self.RFIDCups_minus_account_cups * Cup_deposit_value) - (self.user_funds % Cup_deposit_value) <= 0: #float was used initially...changed to decimal...
            return 0.0
        else:
            return (self.RFIDCups_minus_account_cups * Cup_deposit_value) - (self.user_funds % Cup_deposit_value) #float was used initially...changed to decimal...
        # return float(self.RFIDCups_minus_account_cups * Cup_deposit_value + self.RFIDCups_minus_account_washes * Wash_value) # Original calc before washes were removed
    
    @property
    def Value_of_order(self):
        return float(self.amount_of_RFID_Numbers_Registered * (Cup_deposit_value))
        
    def Order_reset_class(self, unique_order_number_value, local_order_number):
        self.user_name = ""
        self.user_account_number = 0
        self.unique_order_number = unique_order_number_value
        self.amount_of_RFID_Numbers_Registered = 0
        self.user_funds = 0
        self.cups_in_user_account = 0
        self.Washes_in_user_account = 0
        self.local_order_id = local_order_number

