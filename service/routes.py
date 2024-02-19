import requests
from flask_restful import Resource
from loguru import logger

from settings import (
    OAUTH_TOKEN,
    API_HOST,
    CLOUD_DIR,
    SYNC_FOLDER_PATH,
    api
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

    def delete(self, to_delete: str):
        """
        Deletes files
        :param to_delete: list
        :return: None
        """

        params = {
            "path": f"{CLOUD_DIR}/{to_delete}"
        }
        response = requests.delete(URL, params=params, headers=HEADERS, timeout=10)
        if response.status_code == 204:
            logger.info(f"Файл {to_delete} успешно удален.")
        else:
            logger.error(f"Файл {to_delete} не удален. Ошибка соединения.")
        return response


class UploadFiles(Resource):
    def get(self, to_upload: str):
        """
        Gets the link to upload the files into
        :param to_upload: list
        :return: None
        """
        params = {
            "path": f'file-sync/{to_upload}',
            "overwrite": True
        }
        resp_get = requests.get(f'{URL}/upload/',
                                headers=HEADERS,
                                params=params,
                                timeout=10)
        href = resp_get.json()["href"]

        files = {"file": open(f'{SYNC_FOLDER_PATH}/{to_upload}', 'rb')}
        resp_post = requests.post(href, files=files, timeout=10)

        if resp_post.status_code == 201:
            logger.info(f"Файл {to_upload} успешно записан.")
        else:
            logger.error(f"Файл {to_upload} не записан. Ошибка соединения.")
        return resp_post


api.add_resource(CloudFiles, '/api/resources')
api.add_resource(UploadFiles, '/api/resources/upload')
