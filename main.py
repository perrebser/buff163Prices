import asyncio

from classes.BuffPricesManager import BuffPricesManager


def main():
    prices_manager = BuffPricesManager()
    asyncio.run(prices_manager.run())


if __name__ == "__main__":
    main()
