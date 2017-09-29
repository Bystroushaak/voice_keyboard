Voice keyboard
--------------

Just my toy project / attempt to use speech recognition on the iOS as a keyboard for my linux PC.

Use Shelly SSH client on the phone to connect to your server and run

::

    stty -icanon && nc -l 10000 -k

Then run from your PC:

::

    ./voicekeyboard.py server.address 10000

Dependencies
^^^^^^^^^^^^

- xdotool
- python2.7