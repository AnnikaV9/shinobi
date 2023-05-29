Chat logger for hack.chat instances.


Setup:

$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
- Edit config.yml with your preferred editor


Start:

$ source .venv/bin/activate
(.venv) $ python shinobi


Notes:

- Log files are created in logs/ and named according to the channel deployed to.
- Setting the 'nick' option to 'RANDOM' will tell the logger to generate a random numerical nickname.
- Shinobi will restart itself on exceptions after a delay of 10 seconds (Unless it's a KeyboardInterrupt)
- Linebreaks in messages are replaced with '<LB>'


Example log:

$ cat logs/testchannel.log
2023-05-29 11:00:51,006 | Online: carrot, anakin, 6758
2023-05-29 11:00:57,870 | [ttttoe][carrot] Hello World
2023-05-29 11:01:17,334 | [NOTRIP][anakin] @anakin is gonna sleep
2023-05-29 11:01:29,676 | anakin left
2023-05-29 11:01:34,218 | toe joined
2023-05-29 11:01:40,774 | Connection closed: KeyboardInterrupt
