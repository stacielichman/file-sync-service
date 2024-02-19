from loguru import logger

from service.connector import main
from service.routes import SYNC_FOLDER_PATH


if __name__ == '__main__':
    logger.info(
        f"Программа синхронизации файлов начинает "
        f"работу с директорией {SYNC_FOLDER_PATH}.")
    main()

