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
        config = yaml.safe_load(config_file)

    config["nick"] = str(random.randint(1000, 9999)) if config["nick"] == "RANDOM" else config["nick"]
    config["nick"] = f"{config['nick']}#{config['password']}" if config["password"] else config["nick"]
    return config

# create and return logger objects
def create_logger(name: str, log_file: str) -> object:
    formatter = logging.Formatter("%(asctime)s | %(message)s")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

# run connection() coroutine for each channel
async def main(config: dict) -> None:
    channels = list(dict.fromkeys(config["channels"]))
    nick, server, join_delay = config["nick"], config["server"], config["join_delay"]
    await asyncio.gather(*[connection(nick, channel, channels.index(channel) , server, join_delay) for channel in channels])

# connect to server and start ping() and receive() coroutines
async def connection(nick: str, channel: str, num_channels: int, server: str, join_delay: int) -> None:
    logger = create_logger(channel, f"logs/{channel}.log")
    global logger_objects
    logger_objects.append(logger)
    if num_channels != 0:
        await asyncio.sleep(num_channels * join_delay)

    async with websockets.connect(server, ping_timeout=None) as ws:
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
        resp = await ws.recv()
        resp = json.loads(resp)
        match resp["cmd"]:
            case "chat":
                resp["trip"] = "NOTRIP" if len(resp.get("trip", "")) < 6 else resp.get("trip", "")
                logger.info(f"[{resp['trip']}][{resp['nick']}] {resp['text'].replace('\n', '<LB>')}")

            case "info":
                logger.info(resp["text"].replace("\n", "<LB>"))

            case "emote":
                resp["trip"] = "NOTRIP" if len(resp.get("trip", "")) < 6 else resp.get("trip", "")
                logger.info(f"[{resp['trip']}][{resp['nick']}] {resp['text'].replace('\n', '<LB>')}")

            case "onlineAdd":
                logger.info(f"{resp['nick']} joined")

            case "onlineRemove":
                logger.info(f"{resp['nick']} left")

            case "onlineSet":
                logger.info(f"Online: {', '.join(resp['nicks'])}")
                print(f"Connected to channel: {resp['channel']}")

# run main()
if __name__ == "__main__":
    config = load_config()
    logging.basicConfig(filemode="a")
    logger_objects = []

    # register exit handler
    atexit.register(lambda: [logger.info("Connection closed") for logger in logger_objects])

    try:
        asyncio.run(main(config))

    except KeyboardInterrupt:
        raise SystemExit
