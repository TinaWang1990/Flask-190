import smtplib

from email.mime.text import MIMEText

def send_mail(username):
    port = 2525
    smtp_server = 'smtp.mailtrap.io'
    login = ''
    password = ''