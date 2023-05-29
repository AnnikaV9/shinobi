# author: AnnikaV9
# description: chat logger for hack.chat instances

import asyncio
import uvloop
import websockets
import json
import yaml
import logging
import time
import random
import atexit

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def load_config() -> dict:
    with open("config.yml", "r", encoding="utf-8") as config_file:
        config: dict = yaml.safe_load(config_file)

    if config["nick"] == "RANDOM":
        config["nick"]: str = str(random.randint(1000, 9999))

    config["nick"]: str = "{}#{}".format(config["nick"], config["password"]) if config["password"] else config["nick"]
    
    return config

def create_logger(name, log_file) -> object:
    formatter: object = logging.Formatter("%(asctime)s | %(message)s")
    handler: object = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)
    logger: object = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

async def connection(nick: str, channel: str, channel_no: int, server: str) -> None:
    logger: object = create_logger(channel, f"logs/{channel}.log")
    logger_objects.append(logger)

    if channel_no != 0:
        await asyncio.sleep(channel_no * config["join_delay"])

    async with websockets.connect(server) as ws:
        await ws.send(json.dumps({"cmd": "join", "channel": channel, "nick": nick}))
        await asyncio.gather(ping_loop(ws), receive_loop(ws, logger))
        
async def main(nick: str, channels: str, server: list) -> None:
    await asyncio.gather(*[connection(nick, channel, channels.index(channel) , server) for channel in channels])

async def ping_loop(ws: object) -> None:
    while True:
        await asyncio.sleep(60)
        await ws.send(json.dumps({"cmd": "ping"}))

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

if __name__ == "__main__":
    config: dict = load_config()
    logging.basicConfig(filemode="a")
    logger_objects: list = []
    atexit.register(lambda: [logger.info("Connection closed") for logger in logger_objects])

    try:
        asyncio.run(main(config["nick"], config["channels"], config["server"]))
    
    except KeyboardInterrupt:
        raise SystemExit