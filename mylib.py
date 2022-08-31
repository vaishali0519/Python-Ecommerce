import pymysql
from cryptography.fernet import Fernet
import smtplib, random



def connect_to_database():
    conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="", db="arbor", autocommit="True")
    cur = conn.cursor()
    return cur



def connect_to_bank():
    conn=pymysql.connect(host="localhost", port=3306, user="root", passwd="", db="banksystem")
    cur=conn.cursor()
    return cur



def write_key(x):
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    filename = "key/key"+str(x)+".key"
    with open(filename, "wb") as key_file:
        key_file.write(key)


def load_key(x):
    """
    Loads the key from the current directory
    """
    filename = "key/key" + str(x) + ".key"
    return open(filename, "rb").read()


def encrypt_password(password,x):
    # load the previously generated key
    key = load_key(x)
    message = password.encode()
    # initialize the Fernet class
    f = Fernet(key)
    # encrypt the message
    encrypted = f.encrypt(message)
    # print how it looks
    return encrypted


def decrypt_password(password,x):
    # load the previously generated key
    key = load_key(x)
    f = Fernet(key)
    decrypted_encrypted = f.decrypt(password)
    return decrypted_encrypted


def genrateotp():
    OTP = random.randint(1000, 9999)
    sendMail(OTP)
    return OTP



def sendMail(OTP):
    sender_email = "shaluvaisho24@gmail.com"
    rec_email = "shaluvaisho24@gmail.com"
    password = 'yukina2000'
    otp = str(OTP)
    message = "Hello, Your One Time OPT is " + otp

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    print("login sucess")
    server.sendmail(sender_email, rec_email, message)
    print("email has been sent to ", rec_email)



