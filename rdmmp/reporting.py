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
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import pylab

from pylab import title, figure, xlabel, ylabel, xticks, bar, legend, axis, savefig
from fpdf import FPDF

import rdmmp.configvalues as cv


# %% Create the report

# pip install fpdf
class PDF(FPDF):
    
    def header(self):
        # Logo
        self.image('rdmmp/logo/ecole-ia-logo.png', 0, 0, 33)
        self.image('rdmmp/logo/simplon-logo.png', 175, 7, 33)        
        # Arial bold 15
        self.set_font('Arial', 'B', 20)
        # Move to the right (8cm to the right)
        self.cell(80)
        # Title
        self.cell(30, 10, 'Indeed Job Market Analysis', 0, 0, 'C')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Author 
        author = "Philippe - Maxence - Radia - Martial - David"
        self.cell(20, 10, author, align='L', ln=1)
        # Page number
        self.cell(0, 0, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, align='R')
        

def create_report(dataframe):
    """
    Create a pdf report named Job Market Analysis.pdf in the folder Report

    """
    data = dataframe['salaire_rbf'].dropna()
    plt.boxplot(data, sym='')

    #plt.xlim(data.min()-10000, data.max()+10000)
    plt.title('salaire_rbf')
    
    plt.savefig('D:/Dev/Prj/JobMarketAnalysis/Graph/salaire_rbf_BoxPlot.png')
    plt.show()
    
    data = dataframe['salaire_forest'].dropna()
    plt.boxplot(data, sym='')

    #plt.xlim(data.min()-10000, data.max()+10000)
    plt.title('salaire_forest')
    
    plt.savefig('D:/Dev/Prj/JobMarketAnalysis/Graph/salaire_forest_BoxPlot.png')
    plt.show()
    
    df = pd.DataFrame()
    df['Question'] = ["Q1", "Q2", "Q3", "Q4"]
    df['Charles'] = [3, 4, 5, 3]
    df['Mike'] = [3, 3, 4, 4]
    
    title("Professor Criss's Ratings by Users")
    xlabel('Question Number')
    ylabel('Score')
    
    c = [2.0, 4.0, 6.0, 8.0]
    m = [x - 0.5 for x in c]
    
    xticks(c, df['Question'])
    
    bar(m, df['Mike'], width=0.5, color="#91eb87", label="Mike")
    bar(c, df['Charles'], width=0.5, color="#eb879c", label="Charles")
    
    legend()
    axis([0, 10, 0, 8])
    savefig(cv.CFG.graph_dir.joinpath('barchart.png'))
    
    
    
#    data_01 = [1,2,3,4,5,6,7,8,9]
#    data_02 = [15,16,17,18,19,20,21,22,23,24,25]
#    data_03 = [5,6,7,8,9,10,11,12,13]
#    
#    BoxName = ['data 01','data 02','data 03']
#    
#    data = [data_01,data_02,data_03]
#    
#    plt.boxplot(data)
#    
#    plt.ylim(0,30)
#    
#    pylab.xticks([1,2,3], BoxName)
#    
#    plt.savefig('D:/Dev/Prj/JobMarketAnalysis/Graph/MultipleBoxPlot02.png')
 
 
    
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.image('D:/Dev/Prj/JobMarketAnalysis/Graph/salaire_rbf_BoxPlot.png', x = None, y = None, w = 0, h = 0, type = '', link = '')
    pdf.image('D:/Dev/Prj/JobMarketAnalysis/Graph/salaire_forest_BoxPlot.png', x = None, y = None, w = 0, h = 0, type = '', link = '')
    
    pdf.add_page()
    #pdf.set_xy(0, 0)
    pdf.set_font('arial', 'B', 12)
    pdf.cell(60)
    pdf.cell(75, 10, "A Tabular and Graphical Report of Professor Criss's Ratings by Users Charles and Mike", 0, 2, 'C')
    pdf.cell(90, 10, " ", 0, 2, 'C')
    pdf.cell(-40)
    pdf.cell(50, 10, 'Question', 1, 0, 'C')
    pdf.cell(40, 10, 'Charles', 1, 0, 'C')
    pdf.cell(40, 10, 'Mike', 1, 2, 'C')
    pdf.cell(-90)
    pdf.set_font('arial', '', 12)
    for i in range(0, len(df)):
        pdf.cell(50, 10, '%s' % (df['Question'].ix[i]), 1, 0, 'C')
        pdf.cell(40, 10, '%s' % (str(df.Mike.ix[i])), 1, 0, 'C')
        pdf.cell(40, 10, '%s' % (str(df.Charles.ix[i])), 1, 2, 'C')
        pdf.cell(-90)
    pdf.cell(90, 10, " ", 0, 2, 'C')
    pdf.cell(-30)
    pdf.image('D:/Dev/Prj/JobMarketAnalysis/Graph/barchart.png', x = None, y = None, w = 0, h = 0, type = '', link = '')
    pdf.output(cv.CFG.report_dir.joinpath('Job Market Analysis.pdf'), 'F')
    
         
"""
# Instantiation of inherited class
pdf = PDF()
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_font('Times', '', 12)
for i in range(1, 41):
    pdf.cell(0, 10, 'Printing line number ' + str(i), 0, 1)
pdf.output('tuto2.pdf', 'F')
"""   
    
    
# %% Send the report


# email source
FROM = 'Groupe Maxence', cv.CFG.email
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
        mime, handle = create_attachment(cv.CFG.report_dir.joinpath(path))
        message.attach(mime)

    # Attach the plain, non-html message
    # message.attach(email.mime.text.MIMEText(PLAIN_MESSAGE, 'plain'))

    # Attach the html message
    attach_html_text(message)

    # Create SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        # Log in
        server.starttls()
        server.login(cv.CFG.smtp_user, cv.CFG.smtp_pwd)

        # Send the message
        server.send_message(message)


def report(dataframe):
    """
    'Main' function of the module, starting point to create and send a report on the job market.

    Args:
        jobs_df: Dataframe of jobs postings.
    """
    create_report(dataframe)

    send_report()
