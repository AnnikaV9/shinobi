# author: AnnikaV9
# description: chat logger for hack.chat instances

# import modules
import asyncio
import uvloop
import websockets
import json
import yaml
import logging
import time
import random
import sys

# use uvloop for faster event loop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# load configuration from config.yml
def load_config() -> dict:
    with open("config.yml", "r", encoding="utf-8") as config_file:
        config: dict = yaml.safe_load(config_file)

    if config["nick"] == "RANDOM":
        config["nick"]: str = str(random.randint(1000, 9999))

    config["nick"]: str = "{}#{}".format(config["nick"], config["password"]) if config["password"] else config["nick"]
    
    if len(sys.argv) < 2:
        print("Usage: python shinobi <channel>")
        raise SystemExit

    config["channel"]: str = sys.argv[1]
    return config

# connect to the server and start coroutines
async def main(nick: str, channel: str, server: str, logger: object) -> None:
    async with websockets.connect(server) as ws:
        await ws.send(json.dumps({"cmd": "join", "channel": channel, "nick": nick}))
        await asyncio.gather(ping_loop(ws), receive_loop(ws, logger))

# send a ping every 60 seconds
async def ping_loop(ws: object) -> None:
    while True:
        await asyncio.sleep(60)
        await ws.send(json.dumps({"cmd": "ping"}))

# receive messages and log them
async def receive_loop(ws: object, logger: object) -> None:
    while True:
        resp: str = await ws.recv()
        resp: dict = json.loads(resp)
        if resp["cmd"] == "chat":
            resp["trip"] = "NOTRIP" if len(resp.get("trip", "")) < 6 else resp.get("trip", "")
            logger.info("[{}][{}] {}".format(resp["trip"], resp["nick"], resp["text"].replace("\n", "<LB>")))

        elif resp["cmd"] == "emote":
            resp["trip"] = "NOTRIP" if len(resp.get("trip", "")) < 6 else resp.get("trip", "")
            logger.info("[{}][{}] {}".format(resp["trip"], resp["nick"], resp["text"].replace("\n", "<LB>")))

        elif resp["cmd"] == "onlineAdd":
            logger.info("{} joined".format(resp["nick"]))

        elif resp["cmd"] == "onlineRemove":
            logger.info("{} left".format(resp["nick"]))

        elif resp["cmd"] == "onlineSet":
            logger.info("Online: {}".format(", ".join(resp["nicks"])))
            print("Connected to channel: {}".format(resp["channel"]))

# initialize logger and start main coroutine
if __name__ == "__main__":
    config: dict = load_config()
    logging.basicConfig(
        format="%(asctime)s | %(message)s",
        filename="logs/{}.log".format(config["channel"]),
        filemode="a",
        level=logging.INFO
    )
    logger: object = logging.getLogger()

    while True:
        try:
            asyncio.run(main(config["nick"], config["channel"], config["server"], logger))

        except KeyboardInterrupt:
            logger.info("Connection closed: KeyboardInterrupt")
            raise SystemExit

        # reconnect on exception after 10 seconds
        except Exception as error:
            logger.exception(f"Connection closed: {error}")
            time.sleep(10)
            config: dict = load_config()
