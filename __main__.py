import asyncio
import uvloop

from CROUStillantAPI.app import app
from hypercorn.asyncio import serve
from hypercorn.config import Config
from dotenv import load_dotenv
from os import environ


load_dotenv(dotenv_path=f".env")


config = Config()
config.bind = [f"{environ.get('API_HOST', '0.0.0.0')}:{environ.get('API_PORT', 5000)}"]
config.workers = 1


uvloop.install()
asyncio.run(serve(app, config))
