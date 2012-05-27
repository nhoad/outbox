#!/usr/bin/env python2

import mox

from outbox import Outbox, Attachment, Email

def test_attachment_raw_data():
    attachment = Attachment('my filename', raw='this is some data')

    assert attachment.name == 'my filename'
    assert attachment.raw == 'this is some data'
    assert attachment.filepath == None

def test_attachment_file():
    attachment = Attachment('my filename', filepath=__file__)

    assert attachment.name == 'my filename'
    assert attachment.raw == None
    assert attachment.filepath == __file__
    assert attachment.read() == open(__file__).read()

    attachment = Attachment('my filename', raw='foo data')

    assert attachment.name == 'my filename'
    assert attachment.raw == 'foo data'
    assert attachment.filepath == None
    assert attachment.read() == 'foo data'

def test_attachment_errors():
    test_args = [
        dict(),
        dict(raw=None),
        dict(filepath='asdfasdf'),
        dict(filepath=''),
        dict(filepath='foo', raw='foo'),
    ]

    for f in test_args:
        try:
            Attachment('my filename', **f)
        except (ValueError, OSError):
            pass
        else:
            assert False, "Broken on args %r" % f

def test_email_errors():
    test_args = [
        (None, '', ''),
        ([], '', ''),
        (5, '', ''),
        ([5], '', ''),
    ]

    for f in test_args:
        try:
            Email(*f)
        except (ValueError, TypeError):
            pass
        else:
            assert False, "No recipients should be stopped"

def test_email():
    e = Email(recipients=['nathan@getoffmalawn.com'], subject='subject',
            body='body')

    assert e.body == 'body'
    assert e.subject == 'subject'
    assert e.recipients == ['nathan@getoffmalawn.com']


def test_outbox_attributes():
    o = Outbox('username', 'password', 'server', 1234)

    assert o.username == 'username'
    assert o.password == 'password'
    assert o.connection_details == ('server', 1234, True)


def test_outbox_login():
    m = mox.Mox()

    import smtplib

    smtplib.SMTP = m.CreateMockAnything()
    smtp = m.CreateMockAnything()
    smtplib.SMTP('server',1234).AndReturn(smtp)
    smtp.starttls()
    smtp.login('username', 'password')

    m.ReplayAll()

    o = Outbox('username', 'password', 'server', 1234)
    o._login()

    m.VerifyAll()
    m.UnsetStubs()

def test_outbox_send():
    m = mox.Mox()
    message = Email(['nathan@getoffmalawn.com'], 'subject', 'body')

    import smtplib, email.mime.multipart

    email.mime.multipart.MIMEMultipart.as_string = lambda self: 'foo'
    smtplib.SMTP = m.CreateMockAnything()
    smtp = m.CreateMockAnything()

    smtplib.SMTP('server',1234).AndReturn(smtp)

    smtp.starttls()
    smtp.login('username', 'password')
    smtp.sendmail('username', message.recipients, 'foo')

    m.ReplayAll()

    o = Outbox('username', 'password', 'server', 1234)
    o.send(message, [Attachment('foo', raw='foo')])

    m.VerifyAll()
    m.UnsetStubs()
