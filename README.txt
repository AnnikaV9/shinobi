Chat logger for hack.chat instances.


Setup:

$ pip install -r requirements.txt
$ vim config.yml
$ python shinobi


Notes:

- Log files are created in logs/ and named according to the channel they are deployed to.

- Setting the 'nick' option to 'RANDOM' will tell the logger to generate a random numerical nickname.

- Shinobi will restart itself on exceptions after a delay of 10 seconds (Unless it's a KeyboardInterrupt)
