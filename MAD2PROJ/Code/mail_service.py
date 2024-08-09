# from smtplib import SMTP
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import os
# import sys
# from models import db, Sponcer,Influencer,AdRequest
# pending_requests = db.session.query(AdRequest).filter_by(status='Pending').all()

# SMTP_HOST= "localhost"
# SMTP_PORT="1025"
# SENDER_EMAIL = "athenamcgonagall7@gmail.com"
# SENDER_PASSWORD="hkvw dsmi bwxb uyjl"


# def send_message():
#     msg= MIMEMultipart()
#     msg["to"]=to
#     msg["subject"]=subject
#     msg["from"]=SENDER_EMAIL
#     msg.attach(MIMEText(content_body,'html'))
#     client = SMTP(host=SMTP_HOST,port=SMTP_PORT)
#     client.send_message()
    
    
    