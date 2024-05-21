from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import multiprocessing
import threading

import argparse
from argparse import ArgumentParser
import os
import json
import base64
import logging
import email, smtplib, ssl 
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr,formataddr

from email.header import Header

tts_logger = logging.getLogger("user_service")

def send_email(subject, receiver, body, sender, password, files=[]) :
    sender_email = sender
    sender_name = "VoiceTraingService"
    message = MIMEMultipart()
    message_from =  sender_name + "<" + sender_email + ">"
    message['From'] = message_from
    message["To"] = receiver
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    for path in files:
            part = MIMEBase('application', "octet-stream")
            with open(path, 'rb') as file:
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                'attachment; filename="{}"'.format(os.path.basename(path)))
                message.attach(part) 
    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver.split(','), message.as_string())
    tts_logger.INFO(f"An verification code email has been sent to {receiver}")