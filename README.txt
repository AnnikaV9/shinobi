Chat logger for hack.chat instances.

Install dependencies:
    $ pip install -r requirements.txt

Modify configuration:
    $ vim config.yml

Run shinobi:
    $ python shinobi

Notes:
    - Log files are created in logs/ and named according to the channel they are deployed to.
    - Setting the 'nick' option to 'RANDOM' will tell the logger to generate a random numerical nickname.
    - Shinobi will restart itself on exceptions after a delay of 10 seconds (Unless it's a KeyboardInterrupt)

Example log:
      2023-05-28 22:10:34,497 | Online: 3948, AnnikaV9
      2023-05-28 22:10:56,408 | carrot joined
      2023-05-28 22:11:15,762 | [u3rwOv][carrot] Hello world!
      2023-05-28 22:11:29,315 | carrot left
      2023-05-28 22:11:34,627 | Connection closed: KeyboardInterrupt
