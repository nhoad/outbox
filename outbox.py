'''
File: outbox.py
Author: Nathan Hoad
Description: Simple wrapper around smtplib for sending an email.
'''

import os
import smtplib
import sys

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

string_type = basestring if sys.version_info[0] == 2 else str

class Email(object):
    def __init__(self, recipients, subject, body=None, html_body=None):
        if not recipients:
            raise ValueError("At least one recipient must be specified!")

        iter(recipients)

        for r in recipients:
            if not isinstance(r, string_type):
                raise TypeError("Recipient not a string: %s" % r)

        if body is None and html_body is None:
            raise ValueError("No body set")

        self.recipients = recipients
        self.subject = subject
        self.body = body
        self.html_body = html_body


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
        if mode not in ('SSL', 'TLS', None):
            raise ValueError("Mode must be one of TLS, SSL, or None")

        self.username = username
        self.password = password
        self.connection_details = (server, port, mode)
        self._conn = None

    def __enter__(self):
        self._conn = self._login()
        return self

    def __exit__(self, type, value, traceback):
        self._conn.quit()

    def _login(self):
        '''Login to the SMTP server specified at instantiation'

        Returns an authenticated SMTP instance.
        '''
        server, port, mode = self.connection_details

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
        msg = MIMEMultipart('alternative')
        msg['From'] = self.username
        msg['To'] = ', '.join(email.recipients)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = email.subject

        if email.body:
            msg.attach(MIMEText(email.body, 'plain'))

        if email.html_body:
            msg.attach(MIMEText(email.html_body, 'html'))

        for f in attachments:
            if not isinstance(f, Attachment):
                raise TypeError("attachment must be of type Attachment")
            add_attachment(msg, f)

        if self._conn:
            self._conn.sendmail(self.username, email.recipients, msg.as_string())
        else:
            smtp = self._login()
            smtp.sendmail(self.username, email.recipients, msg.as_string())
            smtp.quit()

def add_attachment(message, attachment):
    '''Attach an attachment to a message as a side effect.

    Arguments:
        message: MIMEMultipart instance.
        attachment: Attachment instance.
    '''
    data = attachment.read().encode('ascii')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=attachment.name)

    message.attach(part)
