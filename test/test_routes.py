import os

from service.routes import CloudFiles, UploadFiles
from settings import CLOUD_DIR, SYNC_FOLDER_PATH


def test_headers():
    response = CloudFiles().get()
    assert response.headers["Content-Type"] == \
           "application/json; charset=utf-8"


def test_get_cloud_files():
    response = CloudFiles().get()
    assert response.status_code == 200
    assert response.json()["path"] == CLOUD_DIR


def test_delete_files():
    file = "file.txt"
    path = f"{SYNC_FOLDER_PATH}/{file}"
    if not os.path.exists(path):
        file = open(path, "a")
        file.close()
    UploadFiles().get(file)
    response = CloudFiles().delete(file)
    assert response.status_code == 204


def test_cannot_delete_files():
    file = "doesn't exist"
    response = CloudFiles().delete(file)
    assert response.status_code == 404


def test_upload_files():
    file = "file.txt"
    if not os.path.exists(SYNC_FOLDER_PATH):
        file = open(f"{SYNC_FOLDER_PATH}/{file}", "a")
        file.close()
    response = UploadFiles().get(file)
    assert response.status_code == 201
