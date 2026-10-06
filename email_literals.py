# Imports and literals used by email

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header

from email.message import EmailMessage

smtp_port=465
smtp_server = "smtp.gmail.com"
sender_email = "yc.chatdemo@gmail.com"
#default_email = "chatdemo@gmail.com"
root_email = "@youthfulcities.com"
app_id = "yc.chatdemo"
msg_subject = "Hi from YC Summit Chat"
msg_body = "The text from your chat is attached in a file. Enjoy!"
