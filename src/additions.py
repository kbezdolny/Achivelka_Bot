from PIL import Image
import json
import uuid
import os
import database as db
from app_logger import logger
from telebot import apihelper


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


def checkUserInGroup(bot, user_id, group_id):
    try:
        member = bot.get_chat_member(group_id, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(e)
        logger.error(f"Error checking user in group: {e}")
        return False


def createRanks():
    filePath = "../resources/ranks.json"
    data = {
        "0": "Солдат",
        "1": "Старший солдат",
        "2": "Сержант",
        "3": "Старший сержант",
        "4": "Прапорщик",
        "5": "Старший прапорщик",
        "6": "Лейтенант",
        "7": "Старший лейтенант",
        "8": "Майор",
        "9": "Подполковник",
        "10": "Полковник"
    }
    if not os.path.exists(filePath):
        with open(filePath, 'w') as file:
            json.dump(data, file)
        logger.info(f"The file '{filePath}' has been created")
        return
    logger.info(f"The file '{filePath}' already exists")


def saveImage(downloaded_file, file_extension):
    try:
        filename = f"{uuid.uuid4()}.{file_extension}"
        dir_path = '../resources/achievements_images'
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


def deleteImage(image_name):
    dir_path = '../resources/achievements_images'
    file_path = os.path.join(dir_path, image_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
        logger.info(f"Image file {image_name} has been deleted.")
        return

    logger.info(f"No image file found for {image_name}.")


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
        with open("../resources/ranks.json", 'r', encoding='utf-8') as file:
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
