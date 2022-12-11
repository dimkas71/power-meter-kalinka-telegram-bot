import logging
import os
import ssl

from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web

import handlers
from loader import dp, bot

# webhook settings
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
WEBHOOK_PATH = os.environ.get('WEBHOOK_PATH')
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBHOOK_SSL_CERT = os.environ.get('WEBHOOK_SSL_CERT')
WEBHOOK_SSL_KEY = os.environ.get('WEBHOOK_SSL_KEY')

# webserver settings
WEBAPP_HOST = os.environ.get('WEBAPP_HOST') or 'localhost'
WEBAPP_PORT = os.environ.get('WEBAPP_PORT') or 443

dp.middleware.setup(LoggingMiddleware())

async def on_startup(app):
    dp.register_message_handler(handlers.start_cmd, commands="start")
    dp.register_message_handler(handlers.default_msg_handler)
    logging.warning(f"TOKEN: {bot}")
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        if not webhook_info.url:
            await bot.delete_webhook()
        await bot.set_webhook(WEBHOOK_URL, certificate=open(WEBHOOK_SSL_CERT, 'rb'))
    
async def on_shutdown(app):
    logging.warning("Shutting down...")
    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning("Bye....")

if __name__ == '__main__':
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_KEY)

    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT, ssl_context=context)
