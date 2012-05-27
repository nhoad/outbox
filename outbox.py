'''
File: outbox.py
Author: Nathan Hoad
Description: Simple wrapper around smtplib for sending an email.
'''

import os
import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

class Email(object):
    def __init__(self, recipients, subject, body, type='text'):
        if not recipients:
            raise ValueError("At least one recipient must be specified!")

        iter(recipients)

        for r in recipients:
            if not isinstance(r, basestring):
                raise TypeError("Recipient not a string: %s" % r)

        self.recipients = recipients
        self.subject = subject
        self.body = body
        self.type = type


class Attachment(object):
    '''Attachment for an email'''

    def __init__(self, name, filepath=None, raw=None):
        if filepath and raw:
            raise ValueError("filepath and raw can't both be set.")

        if not filepath and raw is None:
            raise ValueError("one of filepath or raw must be set.")

        if filepath and not os.path.isfile(filepath):
            raise OSError("File does not exist: %s" % filepath)

        self.name = name
        self.filepath = filepath
        self.raw = raw

    def read(self):
        if self.raw:
            return self.raw

        with open(self.filepath) as f:
            return f.read()

class Outbox(object):
    '''Thin wrapper around smtplib.(SMTP|SMTP_SSL)'''

    def __init__(self, username, password, server, port, mode='TLS'):
        self.username = username
        self.password = password
        self.connection_details = (server, port, mode)

    def _login(self):
        '''Login to the SMTP server specified at instantiation'

        Returns an authenticated SMTP instance.
        '''
        server, port, mode = self.connection_details

        if mode not in ('SSL', 'TLS', None):
            raise ValueError("Mode must be one of TLS, SSL, or None")

        if mode == 'SSL':
            smtp = smtplib.SMTP_SSL(server, port)
        else:
            smtp = smtplib.SMTP(server, port)

        if mode == 'TLS':
            smtp.starttls()

        smtp.login(self.username, self.password)
        return smtp

    def send(self, email, attachments=()):
        '''Send an email.

        Arguments:
            email: Email instance to send.
            attachments: iterable containing Attachment instances
        '''
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(email.recipients)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = email.subject

        msg.attach(MIMEText(email.body, email.type))

        for f in attachments:
            if not isinstance(f, Attachment):
                raise TypeError("attachment must be of type Attachment")
            add_attachment(msg, f)

        smtp = self._login()
        smtp.sendmail(self.username, email.recipients, msg.as_string())

def add_attachment(message, attachment):
    '''Attach an attachment to a message as a side effect.

    Arguments:
        message: MIMEMultipart instance.
        attachment: Attachment instance.
    '''
    data = attachment.read()
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="{}"'.
            format(attachment.name))

    message.attach(part)
