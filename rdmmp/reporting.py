# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
Created on Tue Mar 12 12:22:59 2019

Script file to generate reports and send them vie email

@authors: Radia, David, Martial, Maxence, Philippe B
"""

def create_report():
    """
    This is an example of Google style.

    Args:
        param1: This is the first param.
        param2: This is a second param.

    Returns:
        This is a description of what is returned.

    Raises:
        KeyError: Raises an exception.
    """
    pass

def send_report():
    """
    This is an example of Google style.

    Args:
        param1: This is the first param.
        param2: This is a second param.

    Returns:
        This is a description of what is returned.

    Raises:
        KeyError: Raises an exception.
    """
    
    import smtplib
    import shutil
    import os
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email import encoders
    
    To="boivin_philippe@orange.fr"
    Subject="mail through code"
    Text="Hai!"
    mail_sender="rdmmp@gmail.com"
    mail_passwd="rdmmp"
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo
    server.login(mail_sender,mail_passwd)
    BODY='\r\n' .join(['To: %s' % To,'From: %s' % mail_sender,'Subject: %s' % Subject,'',Text])
    try:
        server.sendmail(mail_sender,[To],BODY)
        print("email sent")
    except:
        print("error sending email")
        server.quit()

def report(jobs_df):
    """
    'Main' function of the module, starting point to create and send a report on the job market.

    Args:
        jobs_df: Dataframe of jobs postings.
    """
    create_report()
    
    send_report()
