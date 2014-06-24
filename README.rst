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

0.1.7 (24th June 2014)
    - Thanks to Hideaki Takahashi for submitting a MANIFEST, which allows `outbox` to be installed via pip again (broken in 0.1.6)
0.1.6 (24th June 2014)
    - Added `AnonymousOutbox`, a class for connecting to servers that don't perform authentication.
    - Fleshed out documentation for `outbox.Email`.
    - Fixed a bug when using Python 3 (calling iteritems on a dict).
    - Moved the project to Github.
0.1.5 (3rd March 2013)
    - Thanks to Peter Naudus for the following contributions!
    - Added debug argument to Outbox class, to switch smtplib's debugging.
    - Added fields argument to Email class, to allow additional email fields to be set.
    - Connection and disconnection are now exposed.
    - Internal cleanup of some of the connection code.
0.1.4 (29th October 2012)
    - Handle passing a single recipient as a string, instead of forcing the recipient to be a list.
    - Handle utf8 email properly. Thanks, Zhang Mingyuan!
      I doubt I've covered every use case, so the charset to use can be passed in when constructing an Email.
    - Added a sender_address method to the Outbox class, for when the username used for authentication isn't good enough.
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
