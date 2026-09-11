import os, smtplib
from email.message import EmailMessage
def send_email(to, subject, body):
    host=os.getenv("SMTP_HOST"); port=int(os.getenv("SMTP_PORT","587"))
    user=os.getenv("SMTP_USER"); password=os.getenv("SMTP_PASSWORD"); sender=os.getenv("SMTP_FROM",user or "")
    if not host or not user or not password or not to: return False
    msg=EmailMessage(); msg["From"]=sender; msg["To"]=to; msg["Subject"]=subject; msg.set_content(body)
    with smtplib.SMTP(host,port,timeout=15) as s:
        s.starttls(); s.login(user,password); s.send_message(msg)
    return True
