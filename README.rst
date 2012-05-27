Outbox.py: SMTP Client for Humans
================================

This is simplest SMTP client you'll ever see. It's 100% synchronous...

Usage
-----

Give your app an outbox easily::

    from outbox import Outbox, Email, Attachment

    outbox = Outbox(username='username', password='password', 
            server='server', port=1234, mode='SSL')

    outbox.send(Email(subject='my subject', body='some nice sentiment'), [
        Attachment('kittens.jpg', filepath='/path/to/kittens.jpg'),
        Attachment('my-transient-file.bin', raw='some raw data'),
    ])

    outbox.send(Email(subject='my subject', body='<b>SOME REALLY NICE SENTIMENT</b>', type='html'), [
        Attachment('kittens.jpg', filepath='/path/to/kittens.jpg'),
        Attachment('my-transient-file.bin', raw='some raw data'),
    ])

Installation
------------

Installing Outbox.py is simple::

    $ pip install outbox

