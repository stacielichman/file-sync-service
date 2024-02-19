import os

from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api
from loguru import logger

app = Flask(__name__)
api = Api(app)


load_dotenv()
OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")
SYNC_FOLDER_PATH = os.environ.get("SYNC_FOLDER_PATH")
CLOUD_DIR = os.environ.get("CLOUD_DIR")
API_HOST = os.environ.get("API_HOST")

logger.add(
    "../logs/log.log",
    rotation="3 days",
    compression="zip",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} {level} {message}.",
    backtrace=True,
    diagnose=True
)



