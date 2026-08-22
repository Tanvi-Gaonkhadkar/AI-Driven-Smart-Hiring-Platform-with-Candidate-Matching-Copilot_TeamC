import smtplib
from email.mime.text import MIMEText

EMAIL = "tanvigaonkhadkar999@gmail.com"
PASSWORD = "mape zuje ndog xefp"


def send_email(receiver, subject, body):

    try:

        msg = MIMEText(body)

        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = receiver

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            EMAIL,
            PASSWORD
        )

        server.sendmail(
            EMAIL,
            receiver,
            msg.as_string()
        )

        server.quit()

        return True

    except Exception as e:

        return str(e)