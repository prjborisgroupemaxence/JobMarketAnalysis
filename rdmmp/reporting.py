# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
Created on Tue Mar 12 12:22:59 2019

Script file to generate reports and send them vie email

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import collections
import contextlib
import email.encoders
import email.mime.application
import email.mime.audio
import email.mime.base
import email.mime.image
import email.mime.multipart
import email.mime.text
import email.utils
import mimetypes
import pathlib
import smtplib
import string
import tempfile
import uuid
import zipfile
import datetime

import rdmmp.misc as misc

# %% Create the report


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

# %% Send the report


# email source
FROM = 'Groupe Maxence', misc.CFG.email
# email subject, will date later in the code
SUBJECT = 'Dev & data job market analysis – '
# email destination
TO = [
    ('Philippe BOIVIN', 'boivin_philippe@orange.fr'),
    #('Boris FIEVET', 'bbflevet.ext@simplon.co'),
]
# email attachment name
FILE_PATHS = [
    'Job Market Analysis.pdf',
]
# basic message
PLAIN_MESSAGE = '''\
Bonjour, le groupe Maxence (Radia, David, Martial, Maxence et Philippe B)
vous présente son analyse hebdomadaire du marché du travail en pièce jointe !
'''
# html template for the message
HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta http-equiv="Content-Type" content="${content_type}">
    <title>${title}</title>
    <style type="text/css" media="all">
        .key {
            color: #0066AA;
            font-family: sans-serif;
            font-size: 14px;
            font-weight: bold;
        }
        .value {
            color: #000000;
            font-family: monospace;
            font-size: 12px;
            font-weight: normal;
        }
    </style>
</head>
<body>
<div class="value">
    <span class="key">${header}</span>
${message}
</div>
<div class="value">
    <span class="key">File Manifest</span>
${manifest}
</div>
</body>
</html>'''
# html message text itself
HTML_MESSAGE = [
    'Le groupe Maxence (Radia, David, Martial, Maxence et Philippe B) '
    'vous présente son analyse hebdomadaire du marché du travail en pièce jointe !',
]


def make_message_id():
    """
    Create a unique id for the email
    """
    return email.utils.make_msgid(str(uuid.uuid4()))


@contextlib.contextmanager
def create_temp_zip_file(directory):
    """
    Unused, create a zip file from a directory

    Args:
        directory: path of the directory to zip
    """
    paths_to_zip = collections.deque([directory])
    with tempfile.TemporaryDirectory() as root:
        handle = pathlib.Path(root) / f'{directory.name}.zip'
        with zipfile.ZipFile(handle, 'x') as file:
            while paths_to_zip:
                path = paths_to_zip.popleft()
                if path.is_dir():
                    paths_to_zip.extend(path.iterdir())
                elif path.is_file():
                    file.write(path, path.relative_to(directory))
        yield handle


def make_html_list(iterable, kind, indent=0, space=' ' * 4):
    """
    To create the html code for the lists
    """
    prefix = space * indent
    elements = [f'{prefix}<{kind}l>']
    elements.extend(f'{prefix}{space}<li>{item}</li>' for item in iterable)
    elements.append(f'{prefix}</{kind}l>')
    return '\n'.join(elements)


def attach_html_text(message):
    """
    Attach the html to the message

    Args:
        message: Message to attach the html to
    """
    mapping = dict(content_type='', title=message['Subject'], header=message['Subject'], message=make_html_list(HTML_MESSAGE, 'o', 1), manifest=make_html_list(FILE_PATHS, 'u', 1))
    template = string.Template(HTML_TEMPLATE)
    mime = email.mime.text.MIMEText(template.substitute(mapping), 'html')
    mapping['content_type'] = mime['Content-Type'].replace('"', '')
    mime = email.mime.text.MIMEText(template.substitute(mapping), 'html')
    message.attach(mime)


def create_attachment(path):
    """
    Create an attachment  from a file

    Args:
        path: path of a file
    """
    if path.is_dir():
        with create_temp_zip_file(path) as handle:
            return create_attachment(handle)
    kind, encoding = mimetypes.guess_type(str(path))
    if kind is None:
        kind = 'application/octet-stream'
    main_type, sub_type = kind.split('/')
    if main_type == 'application':
        with path.open('rb') as file:
            mime = email.mime.application.MIMEApplication(file.read(), sub_type)
    elif main_type == 'audio':
        with path.open('rb') as file:
            audio_data = file.read()
        try:
            mime = email.mime.audio.MIMEAudio(audio_data)
        except TypeError:
            mime = email.mime.audio.MIMEAudio(audio_data, sub_type)
    elif main_type == 'image':
        with path.open('rb') as file:
            image_data = file.read()
        try:
            mime = email.mime.image.MIMEImage(image_data)
        except TypeError:
            mime = email.mime.image.MIMEImage(image_data, sub_type)
    # elif main_type == 'message':
    #     attachment = email.mime.message.MIMEMessage()
    elif main_type == 'text':
        with path.open('rt') as file:
            mime = email.mime.text.MIMEText(file.read(), sub_type)
    else:
        mime = email.mime.base.MIMEBase(main_type, sub_type)
        with path.open('rb') as file:
            mime.set_payload(file.read())
        email.encoders.encode_base64(mime)
    mime.add_header('Content-Disposition', 'attachment', filename=path.name)
    content_id = make_message_id()
    mime.add_header('Content-ID', content_id)
    handle = f'"cid:{content_id.strip("<>")}"'
    return mime, handle


def create_multipart():
    """
    Create the basic message
    """
    message = email.mime.multipart.MIMEMultipart('html')
    message['Message-ID'] = make_message_id()
    message['From'] = email.utils.formataddr(FROM)
    message['Date'] = email.utils.formatdate(localtime=True)
    message['Subject'] = SUBJECT + datetime.datetime.today().strftime('%d/%m/%Y')
    message['To'] = email.utils.COMMASPACE.join(map(email.utils.formataddr, TO))
    return message


def send_report():
    """
    Send an email with attachments
    """
    # Create message frame
    message = create_multipart()

    # Go through the list of files/folders
    for path in FILE_PATHS:
        # Create the attachment and attach it to the message
        mime, handle = create_attachment(misc.CFG.report_dir.joinpath(path))
        message.attach(mime)

    # Attach the plain, non-html message
    # message.attach(email.mime.text.MIMEText(PLAIN_MESSAGE, 'plain'))

    # Attach the html message
    attach_html_text(message)

    # Create SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        # Log in
        server.starttls()
        server.login(misc.CFG.smtp_user, misc.CFG.smtp_pwd)

        # Send the message
        server.send_message(message)


def report(jobs_df):
    """
    'Main' function of the module, starting point to create and send a report on the job market.

    Args:
        jobs_df: Dataframe of jobs postings.
    """
    create_report()

    send_report()
