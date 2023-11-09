from PIL import Image
import json
import uuid
import os
import database as db
from app_logger import logger


def isAdmin(bot, username, chat_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.username == username:
                return True
        return False

    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False


def saveImage(downloaded_file, file_extension):
    try:
        filename = f"{uuid.uuid4()}.{file_extension}"
        dir_path = 'resources/achievements_images'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_path = os.path.join(dir_path, filename)

        with open(file_path, 'wb') as file:
            file.write(downloaded_file)

        logger.info(f"File \"{filename}\" saved successfully")
        return {"file_path": file_path, "filename": filename}

    except Exception as e:
        logger.error(f"Error saving image: {e}")
        return None


def saveTempData(data):
    try:
        filename = f"{uuid.uuid4()}.json"
        dir_path = 'temp'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_path = os.path.join(dir_path, filename)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        logger.info(f"TempData file \"temp\\{filename}\" created successfully")
        return file_path

    except Exception as e:
        logger.error(f"Error create TempData file: {e}")
        return None


def loadTempData(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"File \"{filename}\" read successfully")
        return data

    except FileNotFoundError as e:
        logger.error(f"TempData file not found \"{filename}\": {e}")
        return None

    except Exception as e:
        logger.error(f"Error loading TempData file \"{filename}\": {e}")
        return None


def deleteTempData(filename):
    try:
        os.remove(filename)
        logger.info(f"TempData file \"{filename}\" deleted successfully")

    except FileNotFoundError as e:
        logger.error(f"TempData file not found \"{filename}\": {e}")
        return None

    except Exception as e:
        logger.error(f"Error deleting TempData file \"{filename}\": {e}")
        return None


def editTempData(filename, updated_data):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        data.update(updated_data)
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        logger.info(f"TempData file \"{filename}\" edited successfully")
        return True

    except FileNotFoundError as e:
        logger.error(f"TempData file not found \"{filename}\": {e}")
        return False

    except Exception as e:
        logger.error(f"Error editing TempData file \"{filename}\": {e}")
        return False


def getAllRanks():
    try:
        with open("resources/ranks.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data

    except FileNotFoundError as e:
        logger.error(f"File of ranks not found: {e}")

    except Exception as e:
        logger.error(f"Get all ranks error: {e}")


def getRankByNumber(number: int or None):
    data = getAllRanks()
    if not number:
        return data["0"]

    lastKey = int(list(data)[-1])
    if number >= lastKey:
        return data[str(lastKey)]

    return data[str(number)]


def listGroups(message):
    groups = db.getAllChats()
    if not groups:
        bot.send_message(message.chat.id, "Групи не знайдені.")
        return

    return groups
