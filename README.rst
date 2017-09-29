Voice keyboard
--------------
Just my toy project / attempt to use speech recognition on the iOS as a keyboard for my linux PC.

Use `Shelly SSH client <https://itunes.apple.com/us/app/shelly-ssh-client/id989642999?mt=8>`_ (yes, you have to use this, others use different buffering techniques so text can't be transported in realtime) on the phone to connect to your server and run

::

    stty -icanon && nc -l 10000 -k

Then run from your PC:

::

    ./voicekeyboard.py server.address 10000

Then just use voice recognition on the phone / SSH session and talk to the opened netcat.

Dependencies
^^^^^^^^^^^^

- xdotool
- python2.7