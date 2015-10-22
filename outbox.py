'''
File: outbox.py
Author: Nathan Hoad
Description: Simple wrapper around smtplib for sending an email.
'''

import smtplib
import sys

#import logging
import os
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.utils import formatdate


PY2 = sys.version_info[0] == 2

if PY2:
    string_type = basestring
    iteritems = lambda d: d.iteritems()
else:
    string_type = str
    iteritems = lambda d: d.items()


class Email(object):
    def __init__(self, recipients, subject, body=None, html_body=None,
                 charset='utf8', fields=None, rfc2231=True, embedded=None):
        """
        Object representation of an email. Contains a recipient, subject,
        conditionally a body or HTML body.

        Arguments:
            recipients - list of strings of the email addresses of the
                         recipients. May also be a string containing a single
                         email address.
            subject - Subject of the email.
            body - Plain-text body.
            html_body - Rich-text body.
            charset - charset to use for encoding the `body` and `html_body`
                      attributes.
            fields - any additional headers you want to add to the email message.
        """

        iter(recipients)

        if isinstance(recipients, string_type):
            recipients = [recipients]

        if not recipients:
            raise ValueError("At least one recipient must be specified!")

        for r in recipients:
            if not isinstance(r, string_type):
                raise TypeError("Recipient not a string: %s" % r)

        if body is None and html_body is None:
            raise ValueError("No body set")

        self.recipients = recipients
        self.subject = subject
        self.body = body
        self.html_body = html_body
        self.charset = charset
        self.fields = fields or {}
        self.rfc2231 = rfc2231
        self.embedded = embedded or []

    def as_mime(self, attachments=()):
        bodies = []
        if self.body:
            bodies.append(MIMEText(self.body, 'plain', self.charset))

        if self.html_body:
            bodies.append(MIMEText(self.html_body, 'html', self.charset))

        with_alternative = len(bodies) == 2
        have_embedded = len(self.embedded) > 0
        if with_alternative or attachments or have_embedded:
            if with_alternative:
                txt = MIMEMultipart('alternative')
                if attachments or have_embedded:
                    msg = MIMEMultipart('mixed')
                    msg.attach(txt)
                else:
                    msg = txt
            else:
                msg = txt = MIMEMultipart('mixed')
            for body in bodies:
                txt.attach(body)
        else:
            msg = bodies[0]

        msg['To'] = ', '.join(self.recipients)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = self.subject

        for key, value in iteritems(self.fields):
            msg[key] = value

        for f in attachments:
            if not isinstance(f, Attachment):
                raise TypeError("attachment must be of type Attachment")
            add_attachment(msg, f, self.rfc2231)

        #logging.info("## size images embedded --> %d" % len(self.embedded))
        for img in self.embedded:
            img_cid = img[0]
            path = img[1]
            #logging.info('## process path: %s' % path)
            if os.path.exists(path):
                file = open(path, 'rb')
                part = MIMEImage(file.read())
                file.close()
                part.add_header('Content-ID', '<%s>' % img_cid)

                #logging.info("## file was embedding --> %s" % img_cid)
                #logging.info("## size files embedded --> \n%s" % part.as_string())
                msg.attach(part)
            #else:
                #logging.info('## file doesn\'t exist --> %s' % path)

        return msg


class Attachment(object):
    '''Attachment for an email'''

    def __init__(self, name, fileobj):
        self.name = name
        self.raw = fileobj.read()

        if not isinstance(self.raw, bytes):
            self.raw = self.raw.encode()

    def read(self):
        return self.raw


class Outbox(object):
    '''Thin wrapper around the SMTP and SMTP_SSL classes from the smtplib module.'''

    def __init__(self, username, password, server, port, mode='TLS', debug=False):
        if mode not in ('SSL', 'TLS', None):
            raise ValueError("Mode must be one of TLS, SSL, or None")

        self.username = username
        self.password = password
        self.connection_details = (server, port, mode, debug)
        self._conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()

    def _login(self):
        '''Login to the SMTP server specified at instantiation

        Returns an authenticated SMTP instance.
        '''
        server, port, mode, debug = self.connection_details

        if mode == 'SSL':
            smtp_class = smtplib.SMTP_SSL
        else:
            smtp_class = smtplib.SMTP

        smtp = smtp_class(server, port)
        smtp.set_debuglevel(debug)

        if mode == 'TLS':
            smtp.starttls()

        self.authenticate(smtp)

        return smtp

    def connect(self):
        self._conn = self._login()

    def authenticate(self, smtp):
        """Perform login with the given smtplib.SMTP instance."""
        smtp.login(self.username, self.password)

    def disconnect(self):
        self._conn.quit()

    def send(self, email, attachments=()):
        '''Send an email. Connect/Disconnect if not already connected

        Arguments:
            email: Email instance to send.
            attachments: iterable containing Attachment instances
        '''

        msg = email.as_mime(attachments)

        if 'From' not in msg:
            msg['From'] = self.sender_address()

        if self._conn:
            self._conn.sendmail(self.username, email.recipients,
                                msg.as_string())
        else:
            with self:
                self._conn.sendmail(self.username, email.recipients,
                                    msg.as_string())

    def sender_address(self):
        '''Return the sender address.

        The default implementation is to use the username that is used for
        signing in.

        If you want pretty names, e.g. <Captain Awesome> foo@example.com,
        override this method to do what you want.
        '''
        return self.username


class AnonymousOutbox(Outbox):
    """Outbox subclass suitable for SMTP servers that do not (or will not)
    perform authentication.
    """
    def __init__(self, *args, **kwargs):
        super(AnonymousOutbox, self).__init__('', '', *args, **kwargs)

    def authenticate(self, smtp):
        """Perform no authentication as the server does not require it."""
        pass


def add_attachment(message, attachment, rfc2231=True):
    '''Attach an attachment to a message as a side effect.

    Arguments:
        message: MIMEMultipart instance.
        attachment: Attachment instance.
    '''
    data = attachment.read()

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(data)
    encoders.encode_base64(part)
    filename = attachment.name if rfc2231 else Header(attachment.name).encode()
    part.add_header('Content-Disposition', 'attachment',
                    filename=filename)

    message.attach(part)
