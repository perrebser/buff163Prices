import asyncio
import json

from classes.BuffPricesManager import BuffPricesManager


def main():
    with open("config.json", "r") as f:
        config = json.load(f)
    prices_manager = BuffPricesManager(config["Cookies"])
    asyncio.run(prices_manager.run())


if __name__ == "__main__":
    main()
