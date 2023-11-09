import logging
from os import path

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def createFileHandler():
    folderPath = "resources/"
    if not path.exists(folderPath):
        os.makedirs(path)
    file_handler = logging.FileHandler(f'{folderPath}bot_logs.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
