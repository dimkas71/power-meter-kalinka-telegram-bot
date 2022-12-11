import logging

from aiogram.utils.executor import start_polling

from loader import dp


async def on_startup(app):
    pass


async def on_shutdown(app):
    logging.warning("Shutting down...")

    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning("Bye....")


if __name__ == '__main__':
    start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )
