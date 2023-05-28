Chat logger for hack.chat instances.

Install dependencies:
    $ pip3 install -r requirements.txt

Modify configuration:
    $ vim config.yml

Run shinobi:
    $ python3 shinobi

Notes:
    - Log files are created in log/ and named
      according to the channel they are deployed
      to.
    - Setting the 'nick' option to 'RANDOM' will
      tell the logger to generate a random
      numerical nickname.
    - Shinobi will restart itself on exceptions 
      after a delay of 10 seconds
      (Unless it's a KeyboardInterrupt)
