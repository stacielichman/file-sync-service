from __future__ import annotations

import threading
import time

from loguru import logger
import os
from datetime import datetime
from os.path import getctime
from threading import Lock
from typing import Iterable

from service.routes import SYNC_FOLDER_PATH, CloudFiles, UploadFiles


LOCK: threading.Lock = Lock()
run_thread = True


def get_local_dir_files() -> dict:
    """
    Gets all files from the local directory
    :return: dict
    """
    try:
        dir_dict: dict = {
            file: datetime.fromtimestamp(
                getctime(SYNC_FOLDER_PATH + '/' + file))
            .strftime('%Y-%m-%dT%H:%M:34+00:00')
            for file in os.listdir(SYNC_FOLDER_PATH)}
    except FileNotFoundError as exc:
        logger.error(f'{type(exc).__name__}')
        global run_thread
        run_thread = False
    else:
        return dir_dict


def get_cloud_files() -> dict:
    """
    Gets all files from the cloud directory
    :return: dict
    """
    cloud_files = CloudFiles().get()
    if cloud_files.status_code != 200 or UnicodeEncodeError:
        logger.error(cloud_files.json()["message"])
        global run_thread
        run_thread = False
    else:
        cloud_files = cloud_files.json()
        file_path = cloud_files["_embedded"]["items"]
        cloud_dict: dict = {
            file["name"]: file["modified"]
            for file in file_path}
        return cloud_dict


def check_if_delete_file() -> None:
    """
    Compares and deletes extra files in the cloud directory
    :return: None
    """
    with LOCK:
        cloud_files = list(get_cloud_files().keys())
        dir_files = list(get_local_dir_files().keys())

        for file in dir_files:
            to_delete: Iterable = filter(lambda cloud_file: cloud_file != file, cloud_files)
            cloud_files = list(to_delete)
        files_to_delete: list = cloud_files

        if len(files_to_delete) == 0:
            return
        else:
            for i_file in files_to_delete:
                CloudFiles().delete(i_file)


def check_if_upload_file() -> None:
    """
    Compares and uploads files into cloud directory
    :return: None
    """
    with LOCK:
        cloud_files = list(get_cloud_files().keys())
        dir_files = list(get_local_dir_files().keys())

        for file in cloud_files:
            to_upload: Iterable = filter(lambda dir_file: dir_file != file, dir_files)
            dir_files = list(to_upload)
        files_to_upload = list(dir_files)

        if len(files_to_upload) == 0:
            return
        for i_file in files_to_upload:
            UploadFiles().get(i_file)


def check_if_reload_file() -> None:
    """
    Compares the time the files were modified
    and rewrites files into cloud directory
    :return: None
    """
    with LOCK:
        cloud_files: dict = get_cloud_files()
        dir_files: dict = get_local_dir_files()

        files_to_patch: list = []
        for filename, mod_time in dir_files.items():
            if filename in cloud_files:
                if cloud_files[filename] != mod_time:
                    files_to_patch.append(filename)

        for i_file in files_to_patch:
            UploadFiles().get(i_file)


def main():
    while run_thread:
        time.sleep(5)
        thread_1 = threading.Thread(target=check_if_delete_file)
        thread_2 = threading.Thread(target=check_if_upload_file)
        thread_3 = threading.Thread(target=check_if_reload_file)

        thread_1.start()
        thread_2.start()
        thread_3.start()

        thread_1.join()
        thread_2.join()
        thread_3.join()
