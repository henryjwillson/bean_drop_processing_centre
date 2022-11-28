#Check_user_account_addition on bluehost
import time
from Screen_Numbers_Class import screen_numbers
import mysql.connector
from mysql.connector import errorcode
from mysql.connector.constants import ClientFlag
import datetime
import math

# MySQL Connection to Bluehost ------------------------------------------------------------------------------------------------------

class server_connection_details:
    '''This class contains details used for making connection to the database server'''
    
    def __init__(self, host, port, user, pwd, DB_Name, ssl_ca, ssl_cert, ssl_key):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.DB_Name = DB_Name
        self.ssl_ca = ssl_ca
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        
        
    @property
    def connection_config(self):
        #return {'host': self.host, 'port': self.port, 'user': self.user, 'password': self.pwd}
        return{'user': self.user,
                'password': self.pwd,
                'host': self.host,
                'client_flags': [ClientFlag.SSL],
                'ssl_ca': self.ssl_ca,
                'ssl_cert': self.ssl_cert,
                'ssl_key': self.ssl_key}
    
    
    
    def connection_test(self):
        """This function tests the ability to connect to the server database"""
        
        conn = mysql.connector.connect(**self.connection_config) # Running mySQL on bluehost database
        c1 = conn.cursor(buffered=True)
        try:
            c1.execute("USE {}".format(self.DB_Name))
            return("Connection made")
        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(self.DB_Name))
            return("making database connection err is: ", err)

    
    
    def old_owner_cup_counts_bluehost(self, variables):
        """This function returns the value of cup deposits in a users account 
        from the server database"""
        
        conn = mysql.connector.connect(**self.connection_config)
        c1 = conn.cursor()
        try:
            c1.execute("USE {}".format(self.DB_Name))
            
        except mysql.connector.Error as err:
            return("making database connection err is: ", err)
            
        else:
            try:
                bean_drop_cups_ammount_query = "SELECT * FROM `users` WHERE `user_unique_ID` = %s;"          #Selects all values from row with user ID specified
                bean_drop_cups_ammount_value = c1.execute(bean_drop_cups_ammount_query,(variables,))
                return c1.fetchone()[2]
                
            except mysql.connector.Error as err:
                return("MySQL err is: ", err)
                
        finally:
            print("Finally Statement run")      #Finally statement runs even when return statement is passed; allowing return statement to continue; whilst not being blocked by the return statement.
            c1.close()
            conn.close()
    
    
    def old_owner_details_bluehost(self, variables):
        """This function returns the the details of a users account 
        from the server database when using QR_code details"""
        
        conn = mysql.connector.connect(**self.connection_config)
        c1 = conn.cursor()
        try:
            c1.execute("USE {}".format(self.DB_Name))
            
        except mysql.connector.Error as err:
            return("making database connection err is: ", err)
            
        else:
            try:
                bean_drop_cups_ammount_query = "SELECT * FROM `users` WHERE `XXX` = %s;"          #Selects all values from row with user ID specified
                bean_drop_cups_ammount_value = c1.execute(bean_drop_cups_ammount_query,(variables,))
                return c1.fetchone()
                
            except mysql.connector.Error as err:
                return("MySQL err is: ", err)
                
        finally:
            print("Finally Statement run")      #Finally statement runs even when return statement is passed; allowing return statement to continue; whilst not being blocked by the return statement.
            c1.close()
            conn.close()

    def return_current_order_history_id_bluehost(self, variables):
        """This function uses ORDERH_owner_id and ORDERH_datetime to return the sequential global order ID generated"""
        
        conn = mysql.connector.connect(**self.connection_config)
        c1 = conn.cursor()
        try:
            c1.execute("USE {}".format(self.DB_Name))
            
        except mysql.connector.Error as err:
            return("making database connection err is: ", err)
        
        else:
            try:
                recent_order_history_query = "SELECT * FROM `order_history` WHERE `owner_id` = %s AND `datetime` = %s;"          #Selects all values from row with user ID specified  AND `ORDERH_datetime` = %s
                recent_order_history_value = c1.execute(recent_order_history_query,(variables))
                return c1.fetchone()
            except mysql.connector.Error as err:
                return("MySQL err is: ", err)
        
        finally:
            print("Finally Statement run for return_current_order_history_id_bluehost")      #Finally statement runs even when return statement is passed; allowing return statement to continue; whilst not being blocked by the return statement.
            c1.close()
            conn.close()
        
    
    def insert_order_history_bluehost(self, variables):
        """This function inserts details of an order into the order_history database"""
            
            
    def add_cup_history_bluehost(self, variables):
        """This function inserts details of the trasfer of cups into the cup_history_db.
        Variables are: XXX, XXX, XXX, XXX and XXX"""
    
    
    def insert_new_user_bluehost(self, variables):
        """This function registers a new user in the server database with number of cups owned, 
        registration date time, XXX, XXX and XXX used in the order"""
        
    
            
    def bluehost_user_from_reg_date_POS_ID(self, variables):
        """This function takes the registration date of a user and the XXX used at registration
        to identify a user on server and returns website registration details
        linked to the account - Not needed now the XXX is generating these details"""
        
    
    def update_owner_bluehost(self, variables):   #Used to update number of cups owned by customer
        """This function updates the number of cups owned by a customer on the servers user_db
        variables are: user_unique_ID, (number of new cups owned by a customer) and deposit value to be reduced by for new cups.
        This function uses the 'SELECT ... FOR UPDATE' syntax in mySQL to lock row whilst updating preventing any dual transactions being undertaken.
        """
        
        conn = mysql.connector.connect(**self.connection_config) # Running mySQL on bluehost database
        c1 = conn.cursor()
        
        try:
            c1.execute("USE {}".format(self.DB_Name))
        except mysql.connector.Error as err:
            return("making database connection err is: ", err)
            
        else:
            try:
                user_cups_ammount_query = "SELECT * FROM `users` WHERE `unique_ID` = %s FOR UPDATE;"          #Selects all values from row with user ID specified
                user_cups_ammount_value = c1.execute(user_cups_ammount_query,(variables[0],))
                refreshed_user_data = c1.fetchone()
                if refreshed_user_data[2] >= variables[2]:
                    updated_cups_owned = refreshed_user_data[3] + variables[1]
                    new_variables = (variables[2], updated_cups_owned, variables[0])
                    bluehost_update_user_from_order = "UPDATE `users` SET `funds`= `funds` - %s, `cups`= %s WHERE `unique_ID` = %s;"
                    c1.execute(bluehost_update_user_from_order,(new_variables))
                    conn.commit()
                    return("User updated")
                else:
                    return("Insufficient Funds")
            except mysql.connector.Error as err:
                return("Error when updating user_db is: ", err)
        
        finally:
            print("Finally Statement run")      #Finally statement runs even when return statement is passed; allowing return statement to continue; whilst not being blocked by the return statement.
            c1.close()
            conn.close()
            
    def update_cup_data_bluehost(self, variables):
        """This function updates the cup database with new ownership of a bean drop cup
        variables are: USER_ID, current_date_time and RFID identification number"""
        
        conn = mysql.connector.connect(**self.connection_config) # Running mySQL on bluehost database
        c1 = conn.cursor()
        
        try:
            c1.execute("USE {}".format(self.DB_Name))
        except mysql.connector.Error as err:
            return("making database connection err is: ", err)
        
        else:
            try:
                update_cup_data_query="UPDATE `cups` SET `USER_ID`= %s,`Number_of_uses`=`Number_of_uses`+1 ,`Last_use`=%s WHERE `RFID_UID` = %s;"
                c1.execute(update_cup_data_query,(variables)) #variables only work with turples, this uses mutiliple values and so second row does not need to be shown to be empty
                conn.commit()
                return True
            except mysql.connector.Error as err:
                return("updating cup database error is: ", err)
                
        finally:
            c1.close
            conn.close()
      
            
    def admin_add_bean_drop_cups_to_server(self, variables):
        """This function is used by an admin to add a new Bean Drop cup to the servers"""
        
            
    def admin_update_wash_cup_condition_with_old_rfid(self):
        """This function is used by an admin to cleaan a Bean Drop cup and register it on the server"""
        
            
    def admin_add_new_cafe_to_server(self, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX):
        """This function is used by an admin to add a new cafe to the Bean Drop servers"""
        
        conn = mysql.connector.connect(**self.connection_config) # Running mySQL on bluehost database
        c1 = conn.cursor()
        
        result_dict = {}
        result_dict[0] = False
        result_dict[1] = False
        
        try:
            c1.execute("USE {}".format(self.DB_Name))
        except mysql.connector.Error as err:
            return("making database connection err is: ", err)
        
        else:
            try:
                bluehost_add_new_cafe_user = ("INSERT INTO users "
                                        "(XXX, XXX, XXX, XXX, XXX) "
                                        "VALUES (%s, %s, %s, %s, %s)")
                c1.execute(bluehost_add_new_cafe_user,(XXX, 0, XXX, XXX, XXX))
                
                new_cup_insert = ("""INSERT INTO cafe_locations 
                                        (XXX, 
                                        XXX,
                                        XXX,
                                        XXX,
                                        XXX,
                                        XXX,
                                        XXX,
                                        XXX,
                                        XXX,
                                        XXX,
                                        XXX,
                                        XXX,
                                        XXX) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")
                c1.execute(new_cup_insert,(XXX,XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX)) #variables only work with turples, this uses mutiliple values and so second row does not need to be shown to be empty
                conn.commit()
                result_dict[0] = True
                result_dict[1] = "New Cafe " + XXX + " succesfully added to the database"
                return result_dict
            except mysql.connector.Error as err:
                result_dict[1] = ("Error adding new cafe to database: ", err)
                return result_dict
                
        finally:
            c1.close
            conn.close()
            return result_dict
            
    def admin_rollback_new_cafe_from_server(self, XXX):
        """This function is used by an admin to rollback an addition of a new cafe to the Bean Drop servers"""
        
        conn = mysql.connector.connect(**self.connection_config) # Running mySQL on bluehost database
        c1 = conn.cursor()
        
        result_dict = {}
        result_dict[0] = False
        result_dict[1] = False
        
        try:
            c1.execute("USE {}".format(self.DB_Name))
        except mysql.connector.Error as err:
            return("making database connection err is: ", err)
        
        else:
            try:
                remove_cafe_SQL = "DELETE FROM cafe_locations WHERE id_global = %s;"
                c1.execute(remove_cafe_SQL,(XXX,))
                remove_user_SQL = "DELETE FROM users_db WHERE QR_generator = %s;"
                c1.execute(remove_user_SQL,(XXX,))
                conn.commit()
                result_dict[0] = True
                result_dict[1] = "New Cafe was succesfully rolled back and removed from the database"
            except mysql.connector.Error as err:
                result_dict[1] = ("Error rollingback new cafe to database: ", err)
                return result_dict
        finally:
            c1.close
            conn.close()
            return result_dict
            
    def admin_return_all_cup_rfid_values(self):
        """This function is used by an admin to return all rfid values in the cup_db"""
        
            
    def admin_add_bean_drop_cups_to_cup_wash_condition(self, cup_rfid):
        """This function is used by an admin to add a new Bean Drop cup to the servers cup wash condition database"""      
         
    def admin_check_rfid_in_delivery_box(self, cup_rfid):
        """This function is used by an admin to check if cup is registered in a delivery box"""
         
    def admin_add_cup_to_delivery_box(self, box_rfid , cup_rfid):
        """This function is used by an admin to add a Bean Drop cup to a delivery box"""
            
    def admin_remove_cup_from_delivery_box(self, cup_rfid):
        """This function is used by an admin to remove a Bean Drop cup to a delivery box"""
        
    def admin_empty_delivery_box(self, delivery_box_rfid):
        """This function is used by an admin to remove a Bean Drop cup to a delivery box"""        
            
    def super_admin_unregister_rfid(self, rfid_uid):
        """This function is used by a super admin to unregister and rfid from the database and all ascociated linked rows.
        This should not be used in the live database but only on the developer database"""
    
    def admin_add_bean_drop_delivery_box_to_server(self, rfid_uid, bean_drop_owner_users_db, current_date_time, replacement_value, condition_of_box, box_description):
        """This function is used by an admin to add a new Bean Drop delivery box to the servers
        """
             
    def admin_add_bean_drop_delivery_vehicle_to_server(self, owner_id_qr_generator, current_date_time, clean_frequency, maintenance_frequency, replacement_value, vehicle_description, rfid_uid, vehicle_name):
        """This function is used by an admin to add a new Bean Drop delivery box to the server        
        """
    
    def admin_create_table(self, TABLES_BH):
        """This function is used by an admin to create Tables for the Bean Drop Server
        
        """
    
    def complete_order_bluehost(self, variables, screen_class, rfid_dictionary, cafe_class):
        """This function aims to complete an entire order processing in the following method
        -
        new user generation or old customer update
        cafe / owner update
        order history
        cup database assigning, cup history assigning
        -
        The variables are: XXX, XXX"""
        
        conn = mysql.connector.connect(**self.connection_config) # Running mySQL on bluehost database
        c1 = conn.cursor()
        
        try:
            c1.execute("USE {}".format(self.DB_Name))
            print("Connection made")
        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(self.DB_Name))
            print("actual err was: ",err)
        else:
            try:
                # Creating a new user
                if variables[3] == True:
                    new_user_variables = (screen_class.amount_of_RFID_Numbers_Registered, variables[0], cafe_class.POS_ID, screen_class.user_account_number, variables[1])
                    bluehost_add_new_user = ("INSERT INTO users "
                                            "(XXX, XXX, XXX, XXX, XXX) "
                                            "VALUES (%s, %s, %s, %s, %s)")
                    c1.execute(bluehost_add_new_user,(new_user_variables))
                # Updating old user
                else:
                    user_cups_query_variables = (screen_class.user_account_number)
                    user_cups_ammount_query = "SELECT * FROM `users` WHERE `XXX` = %s FOR UPDATE;"          #Selects all values from row with user ID specified
                    user_cups_ammount_value = c1.execute(user_cups_ammount_query,(user_cups_query_variables,))
                    refreshed_user_data = c1.fetchone()
                    new_cups_in_account = math.floor(refreshed_user_data[2] / 3)
                    print("refreshed_data is: ", refreshed_user_data)
                    if new_cups_in_account >= screen_class.cups_in_user_account:
                        updated_cups_owned = refreshed_user_data[3] + screen_class.amount_of_RFID_Numbers_Registered
                        cost_to_user_account = screen_class.Value_of_order - float(screen_class.Beandrop_payment_value)   #Value to be deducted from user account funds
                        print("cost to user account with rounding function is: ", cost_to_user_account)
                        new_variables = (cost_to_user_account, updated_cups_owned, screen_class.user_account_number)
                        bluehost_update_user_from_order = "UPDATE `users` SET `funds`= `funds` - %s, `cups`= %s WHERE `XXX` = %s;"
                        c1.execute(bluehost_update_user_from_order,(new_variables))
                    else:
                        print("Insufficient Funds / Different funding; re-assess payment value")
                        return("Funding Issue")
                        raise Exception
            except mysql.connector.Error as err:
                return("Error adding new user to database: ", err)
            else:
                try:
                    # Updating old customer / owner / cafe
                    old_user_variables = (screen_class.Beandrop_payment_value, screen_class.amount_of_RFID_Numbers_Registered, cafe_class.cafe_id)
                    bluehost_update_user_from_order = "UPDATE `users` SET `funds`= `funds` + %s, `cups`= `cups` - %s WHERE `XXX` = %s;"
                    c1.execute(bluehost_update_user_from_order,(old_user_variables))
                except mysql.connector.Error as err:
                    return("Error adding new user to database: ", err)
                    
                else:
                    try:
                        # Adding order to order_history_db
                        blue_host_order_history_variables = (20, cafe_class.cafe_id, screen_class.user_account_number, screen_class.amount_of_RFID_Numbers_Registered, screen_class.RFIDCups_minus_account_cups, screen_class.RFIDCups_minus_account_washes, screen_class.Value_of_order, screen_class.Beandrop_payment_value, variables[0])
                        bluehost_add_order_history = ("INSERT INTO order_history "
                                                    "(order_id_cafe, cafe_id, owner_id, cups_registered, cup_deposits_taken, cup_cleaning_taken, value, value_taken, datetime) "
                                                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
                        c1.execute(bluehost_add_order_history,(blue_host_order_history_variables))
                    except mysql.connector.Error as err:
                        return("Error adding order history to database: ", err)
                    else:
                        try:
                            #Updating both cup database and cup history database for each RFID/cup
                            return_order_history_variables = (screen_class.user_account_number[0:40], str(variables[0]))
                            print(return_order_history_variables)
                            recent_order_history_query = "SELECT * FROM `order_history` WHERE `owner_id` = %s AND `datetime` = %s;"          #Selects all values from row with user ID specified  AND `ORDERH_datetime` = %s
                            c1.execute(recent_order_history_query,(return_order_history_variables))
                            global_order_id_bluehost =c1.fetchone()
                            print(global_order_id_bluehost[0])
                            for i in range(1, variables[2]+1):
                                try:
                                    print(rfid_dictionary[i])
                                    new_order_history_variables = (global_order_id_bluehost[0], cafe_class.cafe_id ,screen_class.user_account_number,variables[0], rfid_dictionary[i]) 
                                    new_cup_data_variables = (screen_class.user_account_number, variables[0], rfid_dictionary[i])
                                    bluehost_add_cup_history_query = ("INSERT INTO cup_history "
                                                                        "(order_id_global, original_owner_id, new_owner_id, transfer_datetime, cup_rfid_uid) "
                                                                        "VALUES (%s, %s, %s, %s, %s)")
                                    c1.execute(bluehost_add_cup_history_query,(new_order_history_variables))
                                    update_cup_data_query="UPDATE `cup` SET `OWNER_ID`= %s,`Number_of_uses`=`Number_of_uses`+1 ,`Last_use`=%s WHERE `RFID_UID` = %s;"
                                    c1.execute(update_cup_data_query,(new_cup_data_variables)) #variables only work with turples, this uses mutiliple values and so second row does not need to be shown to be empty
                                except Exception as e:
                                    print(e)
                            #rfid_dictionary.clear()
                            conn.commit()
                            return True
                        except mysql.connector.Error as err:
                            return("Error updating cup database and cup history database is: ", err)
        finally:
            c1.close
            conn.close()
            
    def admin_new_customer_order(self, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX, XXX):
        """This function aims to complete an entire order processing in the following method
        New Method:
        Generate new user or check returning customer account for relavent funds to take correct deposit
        Generate new order history entry
        For each cup in order
            check original ownership
            transfer ownership to cafe if not already registered with cafe
                add to cup transfer history
                update cafe account funds
            transfer ownership of cup from cafe to customer and make cup condition unclean
                add to cup transer history
                add to counter of funds transfer for both customer and cafe accounts
        Final updates of returning user and cafe....
        """
        
        return_dict = {}
        return_dict[0] = False
        return_dict[1] = False
        
        step_reached = ""
        
        conn = mysql.connector.connect(**self.connection_config) # Running mySQL on database
        c1 = conn.cursor()
        
        try:
            c1.execute("USE {}".format(self.DB_Name))
            print("Connection made")
        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(self.DB_Name))
            print("actual err was: ",err)
        else:
            try:
                # Creating a new user
                if new_user_bool == True:
                    bluehost_add_new_user = ("INSERT INTO users "
                                            "(XXX, XXX, XXX, XXX, XXX) "
                                            "VALUES (%s, %s, %s, %s, %s);")
                    c1.execute(bluehost_add_new_user,(XXX, XXX, XXX, XXX, XXX))
                    return_dict[1] = "added new user"
                    
                else:
                    return_dict[1] = "user in local found, about to find on database"
                    retrieve_returning_user_querry = "SELECT * FROM `users` WHERE `XXX` = %s FOR UPDATE;"          #Selects all values from row with user ID specified
                    user_cups_ammount_value = c1.execute(retrieve_returning_user_querry,(XXX,))
                    refreshed_user_data = c1.fetchone()
                    return_dict[1] = "user found on database"
                    print("refreshed user data is: ", refreshed_user_data)
                    print(refreshed_user_data[2])
                    required_deposit = (float(number_of_rfids_registered) * float(current_cup_deposit_value)) - float(deposit_value_taken)
                    print("required deposit is: ",required_deposit)
                    if float(required_deposit) > float(refreshed_user_data[2]):
                        print("User does not have enough funds to match deposit being taken")
                        raise Exception
                    else:
                        updated_cups_owned = refreshed_user_data[3] + number_of_rfids_registered
                        print("cost to user account with rounding function is: ", required_deposit)
                        
                #Insert new order history
                customer_account_deposits_value_used = (float(number_of_rfids_registered)*float(current_cup_deposit_value))-float(deposit_value_taken)
                cleaning_charge_to_cafe = float(number_of_rfids_registered)*float(current_clean_cup_charge)
                add_order_history = ("INSERT INTO order_history "
                                            "(cafe_id, owner_id, cups_registered, customer_account_deposit_value_used, new_deposit_value_collected, cleaning_charge_to_cafe, datetime) "
                                            "VALUES (%s, %s, %s, %s, %s, %s, %s);")
                c1.execute(add_order_history,(cafe_id, XXX, number_of_rfids_registered, customer_account_deposits_value_used, deposit_value_taken, cleaning_charge_to_cafe, order_datetime))
                return_dict[1] = "inserted into new order history"
                return_last_order_history_id_querry = "SELECT MAX(order_id_global) FROM order_history;"
                c1.execute(return_last_order_history_id_querry)
                new_global_history_order_id = c1.fetchone()[0]
                return_dict[1] = "returned max oreder history number"
                    
                for cup_value in cups_used_dictionary:
                    print("cup dictionary is",cups_used_dictionary)
                    print("cup value is", cup_value)
                    
                    cup_rfid = cups_used_dictionary[cup_value]
                    return_dict[1] = "about to check cup ownership...."
                    #Check cup original ownership
                    check_ownership_querry = "SELECT `OWNER_ID` FROM `cup` WHERE `RFID` = %s;"
                    c1.execute(check_ownership_querry, (cup_rfid,))
                    cup_owner = c1.fetchone()
                    return_dict[1] = ("cup ownership is: ", cup_owner, "cup value used in querry to database", cup_rfid)
                    if cup_owner[0] != cafe_id: #cup not currently registered with cafe and needs transfering to cafe
                        print("Cup not registered with current cafe, checking registration amongst other cafes initially")
                        cafe_list_querry = "SELECT user_id_global FROM cafe_locations;"
                        c1.execute(cafe_list_querry)
                        cafe_list = c1.fetchall()[0]
                        return_dict[1] = ("cafe list is: ", cafe_list)
                        if cup_owner[0] in cafe_list:
                            #Transfer cups form one cafe to another
                            print("Cup is currently registered with another cafe")
                            transfer_cup_in_cup_history_querry = "INSERT INTO cup_history(XXX, new_owner_id, transfer_datetime, XXX) VALUES (%s, %s, %s, %s);"
                            c1.execute(transfer_cup_in_cup_history_querry, (XXX, cafe_id, order_datetime, XXX))
                            update_old_cafe_ownership = "UPDATE users SET cups = (cups - 1) WHERE XXX = %s;"
                            c1.execute(update_old_cafe_ownership, (XXX,))
                            update_new_cafe_ownership = "UPDATE users SET cups = (cups + 1) WHERE XXX = %s;"
                            c1.execute(update_new_cafe_ownership, (cafe_id,))
                        else:
                            #Check if cup is owned by Bean Drop
                            return_dict[1] = ("about to check bd centre list")
                            check_bean_drop_cup_ownership = "SELECT XXX FROM bd_centres;"
                            c1.execute(check_bean_drop_cup_ownership)
                            bean_drop_centres = c1.fetchall()[0]
                            return_dict[1] = ("bd centre list is: ", bean_drop_centres)
                            if cup_owner[0] in bean_drop_centres:
                                #Transfer cup from bd centre to cafe
                                print("Cup is currently registered with a bean drop centre, transfering to cafe before being sold to a customer")
                                transfer_cup_in_cup_history_querry = "INSERT INTO cup_history(XXX, new_owner_id, transfer_datetime, XXX) VALUES (%s, %s, %s, %s);"
                                c1.execute(transfer_cup_in_cup_history_querry, (XXX, cafe_id, order_datetime, XXX))
                                print("added into cup history...")
                                update_old_cafe_ownership = "UPDATE users SET cups = (cups - 1) WHERE XXX = %s;"
                                c1.execute(update_old_cafe_ownership, (XXX,))
                                print("updated old cafe....")
                                update_new_cafe_ownership = "UPDATE users_db SET cups = (cups + 1) WHERE XXX = %s;"
                                c1.execute(update_new_cafe_ownership, (XXX,))
                                print("updated new cafe...")
                            else:
                                # First transfer from old customer back to Bean Drop 
                                return_local_bean_drop_centre_id_querry = "SELECT XXX FROM bd_centres;"
                                c1.execute(return_local_bean_drop_centre_id_querry)
                                local_bd_centre_id = c1.fetchone()
                                #Transfer cup from old customer to BD Centre
                                print("Cup is currently registered with another customer, transfering to bean drop station before being transfered to the cafe and then from the cafe to the new customer")
                                transfer_cup_in_cup_history_querry = "INSERT INTO cup_history(XXX, new_owner_id, transfer_datetime, XXX) VALUES (%s, %s, %s, %s);"
                                c1.execute(transfer_cup_in_cup_history_querry, (XXX, local_bd_centre_id[0], order_datetime, XXX))
                                print("added into cup history...")
                                update_old_cafe_ownership = "UPDATE users SET cups = (cups - 1), funds = (funds + %s) WHERE XXX = %s;"
                                c1.execute(update_old_cafe_ownership, (float(current_cup_deposit_value), XXX))
                                print("updated old customer....")
                                update_new_cafe_ownership = "UPDATE users SET cups = (cups + 1), funds = (funds - %s) WHERE XXX = %s;"
                                c1.execute(update_new_cafe_ownership, (float(current_cup_deposit_value), XXX))
                                print("transfered cup ownership from old customer to BD centre")
                                print("Cup is not currently registered with another cafe or Bean Drop centre, raising Exception")
                                
                                #Transfer cup from bd centre to cafe
                                print("Cup is currently registered with a bean drop centre, transfering to cafe before being sold to a customer")
                                transfer_cup_in_cup_history_querry = "INSERT INTO cup_history_db(CUPH_original_owner_id, CUPH_new_owner_id, CUPH_transfer_datetime, CUPH_cup_rfid_uid) VALUES (%s, %s, %s, %s);"
                                c1.execute(transfer_cup_in_cup_history_querry, (local_bd_centre_id[0], cafe_id, order_datetime, cup_rfid))
                                print("added into cup history...")
                                update_old_cafe_ownership = "UPDATE users_db SET cups_owned = (cups_owned - 1) WHERE QR_generator = %s;"
                                c1.execute(update_old_cafe_ownership, (local_bd_centre_id[0],))
                                print("updated newly used bd centre for quick transfer....")
                                update_new_cafe_ownership = "UPDATE users_db SET cups_owned = (cups_owned + 1) WHERE QR_generator = %s;"
                                c1.execute(update_new_cafe_ownership, (cafe_id,))
                                print("updated new cafe...")
                                #return_dict[1] = "CUP NOT REGISTERED WITH CAFE OR BEANDROP"
                                #raise Exception

                    #Cup is correctly regustered with the cafe
                    #Transfer from cafe to new owner
                    step_reached = ("about to add to cup history and update owner and cafe")
                    transfer_cup_in_cup_history_querry = "INSERT INTO cup_history(XXX, CUPH_original_owner_id, XXX, CUPH_transfer_datetime, XXX) VALUES (%s, %s, %s, %s, %s);"
                    c1.execute(transfer_cup_in_cup_history_querry, (XXX, cafe_id, XXX, order_datetime, XXX))
                    update_old_cafe_ownership = "UPDATE users SET cups = (cups - 1) WHERE XXX = %s;"
                    c1.execute(update_old_cafe_ownership, (cafe_id,))
                    update_new_cafe_ownership = "UPDATE users SET cups = (cups + 1) WHERE XXX = %s;"
                    c1.execute(update_new_cafe_ownership, (XXX,))
                    #Update cup_db
                    update_cup_db_querry = "UPDATE cup SET ID = %s, Number_of_uses = (Number_of_uses + 1), Last_use = %s, Clean_condition = %s WHERE UID = %s;"
                    c1.execute(update_cup_db_querry, (XXX, order_datetime, 0, XXX))
                    #Remove cup from delivery box if registered in one
                    try:
                        remove_cup_from_delivery_box_compositions_querry = "DELETE FROM delivery_box_compositions WHERE cup_rfid = %s;"
                        c1.execute(remove_cup_from_delivery_box_compositions_querry, (cup_rfid,))
                    except Exception as e:
                        print("Exception occurred when trying to remove cup from delivery box in new customer order",e)
                        
                #update funds
                step_reached = ("about to add to update funds")
                update_user_funds = "UPDATE `users` SET `funds`= (`funds` - %s) WHERE `XXX` = %s;"
                c1.execute(update_user_funds,(customer_account_deposits_value_used, XXX))
                update_cafe_funds = "UPDATE `users` SET `funds`= (`funds` + %s) WHERE `XXX` = %s;"
                c1.execute(update_cafe_funds,(deposit_value_taken, cafe_id))
                conn.commit()
                return_dict[0] = True
                return_dict[1] = True
            except mysql.connector.Error as err:
                return_dict[2] = ("Error occurred durring checking new customer order processing. Error is: ", err, "step reached is: ",step_reached)
                return return_dict
            except Exception as e:
                return_dict[2] = ("Error occurred durring checking new customer order processing. Error is: ", e, "step reached is: ",step_reached)
                return return_dict
        
        finally:
            c1.close
            conn.close()
            return return_dict
    
    def return_cup_ownership_for_refunds(self, selected_offset_order_class, rfid_dictionary, rfid_dictionary_length, updated_rfid_dictionary):
        """This function aims to update an order for a refund and determine if any partial refunds have already been issued
        -
        looks up original order and cup transfer history
        checks user ownership from order"""
                            
    
    def refund_order_bluehost(self, selected_offset_order_class, rfid_dictionary, cafe_class, Bean_drop_centre, number_of_cups_scanned_to_refund, Bean_drop_sales_charges_class, datetime_of_refund):
        """This function aims to complete an entire refund processing in the following method
        -
        checks ownership of cups to be refunded
        updates original user database
        updates cafe database
        updates new_owner database
        updates cups ownership database
        -
        The variables are: N/A """
        
            
    def return_order_history_totals(self, cafe_id, start_date, end_date):
        """This function aims to find the number of cups sold, number of deposits taken and value of deposits taken between two dates
        -
        looks up all orders from cafes and counts totals collected
        returns three values: cups sold, deposits collected and value of deposits collected minus deposits refunded"""

    
    def admin_recall_cafe_dictionary(self):
        """This function aims create a dictionary of cafe accounts which are not allowed to purchase cups from the POS system
        -
        The variables are: N/A """
        
            
    def admin_recall_cafe_details(self):
        """This function aims create a dictionary of cafe accounts which are not allowed to purchase cups from the POS system
        -
        The variables are: N/A """
            
    def admin_recall_cafe_database_name_id(self):
        """This function aims return all the information cafe accounts
        -
        The variables are: N/A """
            
    def admin_recall_customer_company_database_name_id(self):
        """This function aims return id and name for customer companies in use with bean drop and their links to cafes
        -
        The variables are: N/A """
            
    def admin_recall_bean_drop_station_dictionary(self):
        """This function aims create a dictionary of Bean Drop Stations which are restricted in certain transactions as users
        -
        The variables are: N/A """
            
    def admin_recall_bean_drop_station_dictionary_details(self):
        """This function returns all the details of all of the Bean Drop Staions
        -
        The variables are: N/A """
        
            
    def admin_empty_delivery_vehicle(self, delivery_vehicle, current_time):
        """This function aims to select a bean drop delivery vehicle and empty boxes and any bds_delivery_box_bags and the cups in them
        into a processing centre""" 
            
    def admin_empty_and_remove_BDS_delivery_box_bags_from_delivery_vehicle(self, delivery_vehicle, current_datetime):
        """This function aims to select a bean drop delivery vehicle and empty any bds_delivery_box_bags and the cups in them
        into a processing centre"""   
                
                
    def admin_collect_cups_from_bean_drop_station(self, bean_drop_station, beandrop_station_bag, delivery_vehicle, current_time):
        """This function aims to select a bean drop station and transfer all of the cups in the station into a delivery vehicle for 
            collection and transportation back to a processing centre"""
            
    def admin_collect_cups_from_bean_drop_station_rollback(self, bean_drop_station, beandrop_station_bag, delivery_vehicle, transaction_datetime):
        """This function aims to rollback the admin_collect_cups_from_bean_drop_station function"""                
                
    
    def alter_user_db_user_type_column(self, XXX, new_user_type):
        """This function is used to update and modify the newly added 'user_type' column in the users_db.
        This is to help with the sorting of cafes, bean drop stations, customers, companies, cleaning centres and bean drop centres who may own a cup"""   
                
                
    def cup_returned_to_bean_drop_station_simple(self, beandrop_station_id, rfid, current_datetime, refund_value):
        """This is a simplified version of the beandrop cup return to the Bean Drop Station using the new 'user_type' column field in the users_db table.
        This no longer requires the dictionary of restricted cafes as had previoulsy required"""

            
    def cup_returned_to_bean_drop_station_simple_mqtt_send(self, beandrop_station_id, rfid, current_datetime, refund_value, return_code):
        """This is a simplified version of the beandrop cup return to the Bean Drop Station using the new 'user_type' column field in the users_db table.
        This no longer requires the dictionary of restricted cafes as had previoulsy required"""
 
                
    def cup_returned_to_bean_drop_station(self, bean_drop_station_id, rfid, restricted_users_dictionary, current_datetime, Bean_drop_sales_charges_class, restricted_bean_drop_stations):
        """This function aims return a cup to a beandrop_station
        -
        checks ownership of cup being returned
        finds last order id
        adds return history
        updates cup_db
        updates old owner users_db
        updates new bean drop station owner users_db
        -
        The variables are: N/A """
            
    def admin_wash_cup(self, washer, bd_centre, current_datetime, rfid):
        """This function aims register that a cup has been washed and is clean in the database """
    
    
    def admin_rfid_registered_checker(self, rfid):
        "This method checks all rfid values in all tables throughout database to check if the rfid is in current use"
        
    
    def admin_cup_rfid_ownership_check(self, rfid):
        """This looks up the rfid_uid in the database, returning  its ownership only.
        -
        checks cup_db"""
    
            
    def super_admin_reset_all_cups_and_funds(self):
        """ This function resets all users cups owned and funds to 0. Single time use for reset database""" 
            
    def super_admin_return_all_bean_drop_cups_to_bd_station(self, beandrop_station_id, rfid, current_datetime, refund_value):
        """ This function transfers all cups on the database back into Bean Drop ownership and slots into admin server functions seamlessly for a one time use""" 
            
    def admin_return_cup_clean_condition(self, rfid):
        """ This function looks up the rfid uid in the cup wash condition database and returns a true or false value for how clean the cup is"""
        
    
    def admin_return_rfid_uid_owner(self, rfid, bean_drop_station_list, cafe_list):
        """This looks up the rfid_uid in the database, returning  what it is along with its ownership.
        -
        checks cup_db
        checks delivery_box_db
        -
        The variables are: N/A """

            
    def admin_return_delivery_vehicle_details(self, rfid):
        """This looks up the rfid_uid in the database, returning  what it is along with its ownership.
        -
        checks delivery_vehicle_db
        checks delivery_box_db
        -
        The variables are: N/A """
            
    def admin_return_delivery_vehicle_composition_details(self, rfid):
        """This looks up the rfid_uid in the database, returning  the composition of boxes in the delivery vehicle.
        -
        checks delivery_vehicle_composition_db
        -
        The variables are: N/A """
        
            
    def admin_add_box_to_delivery_vehicle(self, box_rfid , bike_rfid, current_time):
        """This function is used by an admin to add a Bean Drop box to a delivery vehicle and simultaneously updates the delivery vehicle composition history."""

            
    def admin_remove_box_from_delivery_bike(self, box_rfid, current_time):
        """This function is used by an admin to rollback a Bean Drop box to a delivery vehicle and simultaneously updates the delivery vehicle composition history."""
            
    def admin_rollback_remove_box_from_delivery_bike(self, box_rfid, original_transaction_time):
        """This function is used by an admin to rollback a Bean Drop box to a delivery vehicle and simultaneously updates the delivery vehicle composition history."""
            
    def admin_tranfer_delivery_box_ownership(self, box_rfid, new_owner, current_time, seal_value):
        """This function is used by an admin to transfer a Bean Drop box to a new owner, simultaneously updates the delivery box history."""
    
    def admin_rollback_cafe_box_delivery(self, current_box_scanned_list, original_transfer_datetime):
        """This function is used by an admin to transfer a Bean Drop box to a new owner, simultaneously updates the delivery box history."""
                    
    
    def admin_return_box_rfid_uid_details(self, rfid):
        """This looks up the rfid_uid in the database, returning  what it is along with its ownership.
        -
        checks delivery_box
        - """
                        
            
    def admin_verified_cups_added_to_delivery_box(self, delivery_box_rfid, rfid, current_datetime, verfification_employee):
        """This function adds a cup to a delivery box or container.
        -
        checks ownership of cup being returned
        finds last order id
        adds return history
        updates cup_db
        updates old owner users_db
        updates new bean drop station owner users_db
        -
        The variables are: N/A """
    
    
        
    def admin_return_total_cups_in_cafes(self):
        """This looks up the cafe id's and then returns the number of cups owned by those id's
        -
        checks cafe_locations_db
        checks cup_db
        -
        The variables are: N/A """
        
            
    def admin_return_total_cups_in_bd_processing_centres(self):
        """This looks up the bd centre id's and then returns the number of cups owned by those id's
        -
        checks cafe_locations_db
        checks cup_db
        -"""
        
    
    def admin_return_total_cups_in_circulation(self):
        """This looks up the bd centre id's and then returns the number of cups owned by those id's
        -
        checks cafe_locations_db
        checks cup_db
        -
        The variables are: N/A """
    
    
    def __str__(self):
        return 'Host: %s , Port: %s, User: %s' % (self.host, self.port, self.user)
    

# conn = mysql.connector.connect(host = '162.241.252.101', port='3306', user="beandrop_RaspiPiDemo", password="bluehostdemo1!") # Running mySQL on bluehost database
# c1 = conn.cursor()
# DB_Name = 'beandrop_WPIED'

def making_database_connection():
    conn = mysql.connector.connect(host = '162.241.252.101', port='3306', user="beandrop_RaspiPiDemo", password="bluehostdemo1!") # Running mySQL on bluehost database
    print(conn)

    c1 = conn.cursor() #object which communicates with entire MySQL server.
    DB_Name = 'beandrop_WPIED' #Name of Database you want to access; this is currently the name of the bluehost database i would like to access

    try:
        c1.execute("USE {}".format(DB_Name))
        print("Connection made")
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_Name))
        print("making database connection err is: ", err)
        
TABLES_BH = {}

# #NOTE: TABLES_BH have been removed to protect the database architecture
#  an example has been constructed below to show how they are constructed.
# There are over 30 tables as part of the database


                                
TABLES_BH['delivery_vehicle_db'] = ("""CREATE TABLE delivery_vehicle_db (
                                id_global INT AUTO_INCREMENT,
                                current_user_id_global VARCHAR(40) NULL,
                                total_trips INT,
                                last_trip_datetime DATETIME,
                                last_clean DATETIME,
                                clean_freqency_trips INT,
                                last_maintenance DATETIME,
                                maintenance_frequency_trips INT,
                                replacement_value DECIMAL(19,2),
                                condition VARCHAR(20),
                                bike_description VARCHAR(255),
                                rfid_uid VARCHAR(40) UNIQUE,
                                FOREIGN KEY (DELIVERYVEHICLEDB_rfid_uid) REFERENCES vehicle_db(VEHICLEDB_rfid_uid),
                                PRIMARY KEY (DELIVERYVEHICLEDB_id_global)
                                )""")
                                



if __name__ == "__main__":
    from certs.program_connection_details import * #importing the local connection details file
    server1 = server_connection_details(local_con_details.host, local_con_details.port, local_con_details.user, local_con_details.pwd, local_con_details.DB_Name, local_con_details.ssl_ca, local_con_details.ssl_cert, local_con_details.ssl_key)
    current_date_time = datetime_formatted()

    #server1.admin_create_table(TABLES_BH)  
    
    
    #-------------------------------------------------------------------------------
    # Adding new cup wash condition table and retrospectively adding the old cups into it with their wash conditions
    
    # rfid_values = server1.admin_return_all_cup_rfid_values()
    # print(rfid_values)
    # for rfid in rfid_values:
        # print(rfid[0])
        # server1.admin_add_bean_drop_cups_to_cup_wash_condition(rfid[0])
    
    #-------------------------------------------------------------------------------
