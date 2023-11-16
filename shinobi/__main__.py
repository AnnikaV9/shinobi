# author: AnnikaV9
# description: chat logger for hack.chat instances
# license: Unlicense, see LICENSE for more details

# import modules
import asyncio
import uvloop
import websockets
import json
import yaml
import logging
import time
import random
import atexit

# set uvloop as asyncio event loop policy
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# load and return configuration
def load_config() -> dict:
    with open("config.yml", "r", encoding="utf-8") as config_file:
        config: dict = yaml.safe_load(config_file)

    config["nick"]: str = str(random.randint(1000, 9999)) if config["nick"] == "RANDOM" else config["nick"]
    config["nick"]: str = "{}#{}".format(config["nick"], config["password"]) if config["password"] else config["nick"]
    return config

# create and return logger objects
def create_logger(name: str, log_file: str) -> object:
    formatter: object = logging.Formatter("%(asctime)s | %(message)s")
    handler: object = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger: object = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

# run connection() coroutine for each channel
async def main(nick: str, channels: list, server: list) -> None:
    await asyncio.gather(*[connection(nick, channel, channels.index(channel) , server) for channel in channels])

# connect to server and start ping() and receive() coroutines
async def connection(nick: str, channel: str, channel_no: int, server: str) -> None:
    logger: object = create_logger(channel, f"logs/{channel}.log")
    logger_objects.append(logger)
    await asyncio.sleep(channel_no * config["join_delay"]) if channel_no != 0 else None
    async with websockets.connect(server) as ws:
        await ws.send(json.dumps({"cmd": "join", "channel": channel, "nick": nick}))
        await asyncio.gather(ping_loop(ws), receive_loop(ws, logger))

# send ping every 60 seconds
async def ping_loop(ws: object) -> None:
    while True:
        await asyncio.sleep(60)
        await ws.send(json.dumps({"cmd": "ping"}))

# receive messages and log them
async def receive_loop(ws: object, logger: object) -> None:
    while True:
        resp: str = await ws.recv()
        resp: dict = json.loads(resp)
        if "cmd" in resp:
            match resp["cmd"]:
                case "chat":
                    resp["trip"] = "NOTRIP" if len(resp.get("trip", "")) < 6 else resp.get("trip", "")
                    logger.info("[{}][{}] {}".format(resp["trip"], resp["nick"], resp["text"].replace("\n", "<LB>")))

                case "info":
                    logger.info(resp["text"].replace("\n", "<LB>"))

                case "emote":
                    resp["trip"] = "NOTRIP" if len(resp.get("trip", "")) < 6 else resp.get("trip", "")
                    logger.info("[{}][{}] {}".format(resp["trip"], resp["nick"], resp["text"].replace("\n", "<LB>")))

                case "onlineAdd":
                    logger.info("{} joined".format(resp["nick"]))

                case "onlineRemove":
                    logger.info("{} left".format(resp["nick"]))

                case "onlineSet":
                    logger.info("Online: {}".format(", ".join(resp["nicks"])))
                    print("Connected to channel: {}".format(resp["channel"]))

# run main()
if __name__ == "__main__":
    config: dict = load_config()
    logging.basicConfig(filemode="a")
    logger_objects: list = []

    # register exit handler
    atexit.register(lambda: [logger.info("Connection closed") for logger in logger_objects])

    try:
        asyncio.run(main(config["nick"], list(dict.fromkeys(config["channels"])), config["server"]))

    except KeyboardInterrupt:
        raise SystemExit
