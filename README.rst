Outbox.py: SMTP Client for Humans
=================================

This is simplest SMTP client you'll ever see. It's 100% synchronous...

Usage
-----

Give your app an outbox easily::

    from outbox import Outbox, Email, Attachment

    # io.StringIO for Python 3 folks
    from StringIO import StringIO

    attachments = [
        Attachment('kittens.jpg', fileobj=open('ducks.jpg', 'rb')),
        Attachment('my-transient-file.bin', fileobj=StringIO('some raw data')),
    ]

    outbox = Outbox(username='username', password='password',
            server='server', port=1234, mode='SSL')

    outbox.send(Email(subject='my subject', body='some nice sentiment',
            recipients=['nathan@getoffmalawn.com']), attachments=attachments)

    # html email with attachments
    outbox.send(Email(subject='my subject', html_body='<b>SOME REALLY NICE SENTIMENT</b>',
            recipients=['nathan@getoffmalawn.com']), attachments=attachments)

This method will log in to the server each time `send()` is called.

Alternatively, you can use Outbox as a context manager::

    with Outbox(username='username', password='password',
            server='server', port=1234, mode='SSL') as outbox:

        outbox.send(Email(subject='my subject', body='some nice sentiment',
                recipients=['nathan@getoffmalawn.com']), attachments=attachments)

        # html email with attachments
        outbox.send(Email(subject='my subject', html_body='<b>SOME REALLY NICE SENTIMENT</b>',
                recipients=['nathan@getoffmalawn.com']), attachments=attachments)

Using Outbox as a context manager has the added benefit of performing a single login to send all emails.

Installation
------------

Installing Outbox.py is simple::

    $ pip install outbox

Change History
--------------

0.1.3 (3rd July 2012)
    - Made a few lines of code a bit easier to follow. No functional changes.
    - Updated the license to actually hold copyright in my name, instead of Kenneth Reitz. Does this mean he owned copyright on the library up until now? Can I even change the license? I'm unsure.
0.1.2 (2nd June 2012)
    - Made Outbox a context manager, so it can be used with the `with` statement.
      As noted in the example, this has the added benefit of performing a single login to send all emails, you should get better performance using a with statement.
    - Removed raw and filepath arguments to Attachment. They were both begging to point to a file-like object, so that's what you have now - an argument called `fileobj`
    - Fixed annoying encoding error when trying to send binary attachments.
    - The Email object does not have a `type` argument anymore. Instead, there is `body` and `html_body`, so you can send an email with both html and plain-text bodies.

0.1.1 (27th May 2012)
    - Initial release
