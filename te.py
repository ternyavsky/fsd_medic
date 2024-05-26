import smtplib
from datetime import datetime

conn = smtplib.SMTP("smtp.gmail.com", 587)
conn.starttls()
conn.login(user="prerecovergroup@gmail.com", password="zcvq hrnp jtxd pfuu")
date = str(datetime.now())
msg = f"server reloaded, {date}"
headers = "From: From Person \r\n"
headers += "To: To Person \r\n"
headers += "Subject: \r\n"
headers += "\r\n"
msg = headers + msg
conn.sendmail(
    from_addr="prerecovergroup@gmail.com", to_addrs="pppoker2015@gmail.com", msg=msg
)
conn.close()
