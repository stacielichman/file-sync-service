import os

import requests
from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api, Resource
from loguru import logger


app = Flask(__name__)
api = Api(app)

load_dotenv()
OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")
SYNC_FOLDER_PATH = os.environ.get("SYNC_FOLDER_PATH")
CLOUD_DIR = os.environ.get("CLOUD_DIR")
API_HOST = os.environ.get("API_HOST")

logger.add(
    "logs/log.log",
    rotation="3 days",
    compression="zip",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} {level} {message}.",
    backtrace=True,
    diagnose=True
)


HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'OAuth {OAUTH_TOKEN}'
}
URL: str = f'https://{API_HOST}'


class CloudFiles(Resource):
    def get(self):
        """
        Gets meta-information about the directory
        :param: None
        :return: object
        """
        params = {
            "path": CLOUD_DIR,
        }
        response = requests.get(
            URL, params=params, headers=HEADERS, timeout=10)
        return response

    def delete(self, to_delete: list) -> None:
        """
        Deletes files
        :param to_delete: list
        :return: None
        """
        for filename in to_delete:
            params = {
                "path": f"{CLOUD_DIR}/{filename}"
            }

            r = requests.delete(URL, params=params, headers=HEADERS, timeout=10)
            if r.status_code == 204:
                logger.info(f"Файл {filename} успешно удален.")
            else:
                logger.error(f"Файл {filename} не удален. Ошибка соединения.")
        return


class UploadFiles(Resource):
    def get(self, to_upload):
        """
        Gets the link to upload the files into
        :param to_upload: list
        :return: None
        """
        for filename in to_upload:
            params = {
                "path": f'file-sync/{filename}',
                "overwrite": True
            }
            r_get = requests.get(f'{URL}/upload/',
                                 headers=HEADERS,
                                 params=params,
                                 timeout=10)
            if r_get.status_code == 200:
                href = r_get.json()["href"]
                files = {"file": open(f'{SYNC_FOLDER_PATH}/{filename}', 'rb')}
                r_post = requests.post(href, files=files, timeout=10)

                if r_post.status_code == 201:
                    logger.info(f"Файл {filename} успешно записан.")
                else:
                    logger.error(f"Файл {filename} не записан. Ошибка соединения.")


api.add_resource(CloudFiles, '/api/resources')
api.add_resource(UploadFiles, '/api/resources/upload')
