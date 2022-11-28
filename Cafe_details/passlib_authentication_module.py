#Program to test capabilities of PassLib

#import the CryptContext class, used to handle all Hashing...

from passlib.context import CryptContext


#Defining hasing and verifying using the context manager
def hash_pwd(password):
    test_pwd_context = CryptContext(schemes=["bcrypt","md5_crypt"]) #First instance is used as default (eg bcrypt)
    return test_pwd_context.hash(password)	

def verify_pwd(password, hash):
    test_pwd_context = CryptContext(schemes=["bcrypt","md5_crypt"]) #First instance is used as default (eg bcrypt)
    return test_pwd_context.verify(password,hash)
    
def combined_variables_hash(variables):
    variable_context = CryptContext(schemes=["bcrypt","md5_crypt"]) #First instance is used as default (eg bcrypt)
    variable_to_hash = ("".join(variables))
    return variable_context.hash(variable_to_hash)



if __name__ == "__main__":

    #Testing --------------------------------------------------------
