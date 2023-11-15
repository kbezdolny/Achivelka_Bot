from telebot import TeleBot, types
from telebot import logger as tbLogger
from typing import Final

import logging
import os
import additions
import app_logger
import database as db
import re
from exceptions.AchievementAlreadyExists import AchievementAlreadyExists


ALLOWED_GROUP_ID: Final[int] = int(os.getenv("allowed_group_id"))
TOKEN: Final[str] = os.getenv("bot_token")

bot = TeleBot(TOKEN)
tbLogger.setLevel(logging.INFO)
app_logger.createFileHandler()
additions.createRanks()


@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.leave_chat(message.chat.id)
        return

    if message.chat.id != ALLOWED_GROUP_ID:
        print(f"Failed to connect to a new group with ID: {message.chat.id}")
        bot.leave_chat(message.chat.id)
        return

    print(f"Success connected to a new group with ID: {message.chat.id}")


@bot.message_handler(commands=['start', 'lobby'])
def handle_menu(message):
    if message.chat.type == 'private' and additions.checkUserInGroup(bot, message.from_user.id, ALLOWED_GROUP_ID):
        messageText = f"*Доброго дня, солдат! Бачу ти не зовсім розібрався)*\n\n"\
                     f"Я той хто видаватиме тобі нашивки та підраховуватиму твій ранг. Можна сказати займаюсь буголтерією.\n"\
                     f"\n🛠\n\n"\
                     f"• *Щоб подивитися ранг /rank_look*\n"\
                     f"• *Які є звання? /ranks*\n"\
                     f"• *Як підвищити собі звання? /level_up*\n"\
                     f"• *Щоб подивитися які у тебе є ачівки /achiev_show*\n"\
                     f"• *Що таке ачівки?? OwO /what_it_is*\n"\
                     f"• *Всі ачівки та як їх отримати? /look_achiev*\n"\
                     f"• *Щоб звернутися в меню /lobby*\n"\
                     f"\n🛠\n\n"\

        if additions.isAdmin(bot, message.from_user.username, ALLOWED_GROUP_ID):
            messageText += f"Для адмінів\n"\
                           f"• *Щоб створити нову ачівку:\n/create_achiev Текст ачівки*\n"\
                           f"• *Щоб додати ачівку користовачу:\n/add_achiev @username*\n"\
                           f"• *Щоб видалити ачівку:\n/delete_achiev*\n"\
                           f"\n🛠\n\n"

        messageText += f"_Якщо у вас виникли проблеми, обов'язково звертайтеся до нашої адміністрації та ми обов'язково вирішимо цю проблему!_"
        bot.send_message(message.chat.id,
                         messageText,
                         parse_mode='Markdown')


@bot.message_handler(commands=['create_achiev'])
def handle_create_achievement(message):
    if message.chat.type == 'private' and additions.checkUserInGroup(bot, message.from_user.id, ALLOWED_GROUP_ID):
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.reply_to(message, "*Щоб створити нову ачвіку:\n/create_achiev Текст ачівки*", parse_mode='Markdown')
            return

        command, achievement_name = parts
        username = message.from_user.username
        if not additions.isAdmin(bot, username, ALLOWED_GROUP_ID):
            bot.send_message(chat_id=message.chat.id,
                             text=f"*Ви не маєте права на виконання цієї операції!*",
                             parse_mode='Markdown',
                             reply_markup=None)
            return

        achievement_exists = db.checkAchievementExists(achievement_name)
        if achievement_exists:
            bot.send_message(
                chat_id=message.chat.id,
                text=f"Така ачівка вже існує",
                parse_mode='Markdown',
                reply_markup=None
            )
            return

        bot.send_message(
            chat_id=message.chat.id,
            text=f"Ачівки не існує. Будь ласка, надішліть зображення для ачівки або введіть `скасувати`",
            parse_mode='Markdown',
            reply_markup=None
        )
        bot.register_next_step_handler(message, processAchievementImage, achievement_name=achievement_name)


def processAchievementImage(message, achievement_name):
    if message.text:
        if message.text.lower() == "скасувати":
            bot.send_message(message.chat.id, f"✖ Створення ачівки скасовано.")
            return

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        file_info = bot.get_file(photo_file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_extension = file_info.file_path.split('.')[-1]
        if file_extension.lower() not in ['jpg', 'jpeg', 'png']:
            bot.reply_to(message, "Непідтримуваний формат зображення. Будь ласка, надішліть зображення у форматі JPEG або PNG.")
            return

        file_path = additions.saveImage(downloaded_file, file_extension)
        if file_path:
            db.createAchievement(achievement_name, file_path["filename"])
            bot.send_message(message.chat.id, f"Ачівка створена", parse_mode='html')
            return

        bot.reply_to(message, "Не вдалося зберегти зображення.")
        return

    bot.reply_to(message, "Будь ласка, надішліть дійсне зображення.")


@bot.message_handler(commands=['add_achiev'])
def handle_add_achievement(message):
    if message.chat.type == 'private' and additions.checkUserInGroup(bot, message.from_user.id, ALLOWED_GROUP_ID):
        match = re.match(r'/add_achiev\s+@(\w+)', message.text)
        if match is None:
            bot.reply_to(message,
                         "*Приклад використання:\n/add_achiev @username*",
                         parse_mode='Markdown')
            return

        if not additions.isAdmin(bot, message.from_user.username, ALLOWED_GROUP_ID):
            bot.send_message(chat_id=message.chat.id,
                             text=f"*Ви не маєте права на виконання цієї операції!*",
                             parse_mode='Markdown')
            return

        achievements = db.getAllAchievements()
        if len(achievements) <= 0:
            bot.send_message(chat_id=message.chat.id,
                             text=f"*Наразі ще створено жодної ачівки!*\n\n"
                                  f"_Щоб створити нову ачвіку:_\n"
                                  f"*/create_achiev Текст ачівки*",
                             parse_mode='Markdown')
            return

        tmpUrl = additions.saveTempData({"username": match.group(1)})
        markup = types.InlineKeyboardMarkup()
        achievementsTemp = {}
        for index, achievement in enumerate(achievements):
            button_text = achievement[0]
            textLen = 13
            if len(button_text) > textLen:
                button_text = f"{button_text[:textLen]}..."
            callback_data = f"select_achiev:{tmpUrl}:{index}"
            achievementsTemp.update({
                str(index): {
                    "id": achievement[1],
                    "name": achievement[0],
                    "image_name": achievement[2]
                }
            })
            markup.add(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))

        additions.editTempData(tmpUrl, {"achievements": achievementsTemp})
        bot.send_message(chat_id=message.chat.id,
                         text="Оберіть ачівку:",
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_achiev'))
def handle_achiev_selection(call):
    _, tmpUrl, achievementIndex = call.data.split(":")

    tmpData = additions.loadTempData(tmpUrl)
    additions.deleteTempData(tmpUrl)
    if not tmpData:
        print("tmpData is null")
        return

    username = tmpData["username"]
    achievement = tmpData["achievements"][achievementIndex]
    try:
        db.addAchievement(username, achievement["id"])
    except AchievementAlreadyExists as e:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              text=f"Така ачівка вже додана @{username}")
        return

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"Ачівка додана *@{username}*",
                          parse_mode='Markdown')

    dir_path = '../resources/achievements_images'
    file_path = os.path.join(dir_path, achievement["image_name"])
    with open(file_path, 'rb') as openedPhoto:
        bot.send_photo(chat_id=ALLOWED_GROUP_ID, photo=openedPhoto,
                       caption=f"<b>@{username}</b>\n\n{achievement['name']}",
                       parse_mode='html')
    return


@bot.message_handler(commands=['delete_achiev'])
def handle_add_achievement(message):
    if message.chat.type == 'private' and additions.checkUserInGroup(bot, message.from_user.id, ALLOWED_GROUP_ID):
        if not additions.isAdmin(bot, message.from_user.username, ALLOWED_GROUP_ID):
            bot.send_message(chat_id=message.chat.id,
                             text=f"*Ви не маєте права на виконання цієї операції!*",
                             parse_mode='Markdown')
            return

        achievements = db.getAllAchievements()
        if len(achievements) <= 0:
            bot.send_message(chat_id=message.chat.id,
                             text=f"*Наразі ще створено жодної ачівки!*\n\n"
                                  f"_Щоб створити нову ачвіку:_\n"
                                  f"*/create_achiev Текст ачівки*",
                             parse_mode='Markdown')
            return

        tmpUrl = additions.saveTempData({})
        markup = types.InlineKeyboardMarkup()
        achievementsTemp = {}
        for index, achievement in enumerate(achievements):
            button_text = achievement[0]
            textLen = 13
            if len(button_text) > textLen:
                button_text = f"{button_text[:textLen]}..."
            callback_data = f"delete_achiev:{tmpUrl}:{index}"
            achievementsTemp.update({
                str(index): {
                    "id": achievement[1],
                    "name": achievement[0],
                    "image_name": achievement[2]
                }
            })
            markup.add(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))

        additions.editTempData(tmpUrl, {"achievements": achievementsTemp})
        bot.send_message(chat_id=message.chat.id,
                         text="Оберіть ачівку:",
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_achiev'))
def handle_achiev_selection(call):
    _, tmpUrl, achievementIndex = call.data.split(":")

    tmpData = additions.loadTempData(tmpUrl)
    additions.deleteTempData(tmpUrl)
    if not tmpData:
        print("tmpData is null")
        return

    achievement = tmpData["achievements"][achievementIndex]
    try:
        db.deleteAchievement(achievement["id"])
    except Exception as e:
        print(e)
        return

    additions.deleteImage(achievement["image_name"])
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"*Ачівку видалено*",
                          parse_mode='Markdown')
    return


@bot.message_handler(commands=['rank_look'])
def handle_get_rank(message):
    if message.chat.type == 'private' and additions.checkUserInGroup(bot, message.from_user.id, ALLOWED_GROUP_ID):
        rank = db.getMyRank(message.from_user.username.replace("@", ""))
        bot.send_message(message.chat.id,
                         f"🦾\n\n"
                         f"Твій ранг:\n*{additions.getRankByNumber(rank)}*\n"
                         f"\n🦾\n\n"
                         f"_Продовжуйте і далі зростати щоб отримати призи за подальше підвищення!_\n"
                         f"*З любов'ю Сашко*",
                         parse_mode='Markdown')


@bot.message_handler(commands=['ranks'])
def handle_ranks(message):
    if message.chat.type == 'private' and additions.checkUserInGroup(bot, message.from_user.id, ALLOWED_GROUP_ID):
        ranks = additions.getAllRanks()
        messageText = "🔥\n\n"
        messageText += "\n\n⬇️\n\n".join(map(lambda rank: f"*{rank}*", ranks.values()))
        messageText += "\n\n🔥\n\n" \
                       "*Полковник* _- найвищий ранг який дається в нашій групі,постарайтеся щоб його отримати!_ 🤭\n\n🔥"
        bot.send_message(message.chat.id, messageText, parse_mode='Markdown')


@bot.message_handler(commands=['achiev_show'])
def handle_get_achievements(message):
    if message.chat.type == 'private' and additions.checkUserInGroup(bot, message.from_user.id, ALLOWED_GROUP_ID):
        achievements = db.getMyAchievements(message.from_user.username.replace("@", ""))
        if not achievements:
            bot.send_message(message.chat.id,
                             f"*Друже, наразі у вас ще немає жодної ачівки!*\n"
                             f"*Тут ти можеш все прочитати ➡️  /look_achiev*",
                             parse_mode='Markdown')
            return

        achievementsList = ""
        media_group = []
        for achievement in achievements:
            name, image_name = achievement
            achievementsList += f"\n\n• *{name}*"
            photo = open(os.path.join('..\\resources\\achievements_images', image_name), 'rb')
            media_group.append(types.InputMediaPhoto(photo))

            if len(media_group) == 10 or achievement == achievements[-1]:
                bot.send_media_group(message.chat.id, media_group)
                for photo in media_group:
                    photo.media.close()
                media_group = []

        bot.send_message(message.chat.id, f"*Ваші ачівки:*{achievementsList}", parse_mode='Markdown')


@bot.message_handler(commands=['what_it_is'])
def handle_what_it_is(message):
    if message.chat.type == 'private' and additions.checkUserInGroup(bot, message.from_user.id, ALLOWED_GROUP_ID):
        bot.send_message(message.chat.id,
                         f"👁\n\n"
                         f"*Що таке ачівки? Це маленькі ачівки та за деяку кількість яких ви можете отримати нагороду та підвищити ранг⬆️*\n"
                         f"\n👁\n\n"
                         f"_Якщо виникло більше питань, яких немає в меню звертайтесь до адмінів:_ *@RodzillaArr*, *@Ikkateiro*",
                         parse_mode='Markdown')


@bot.message_handler(commands=['level_up'])
def handle_level_up(message):
    if message.chat.type == 'private' and additions.checkUserInGroup(bot, message.from_user.id, ALLOWED_GROUP_ID):
        bot.send_message(message.chat.id,
                         f"🤔\n\n"
                         f"*Звання можна підвищити за допомогою ачівок які видаються за дії 🤟*"
                         f"*За які дії? Тут ви можете все прочитати ➡️  /look_achiev*\n"
                         f"\n🤔",
                         parse_mode='Markdown')


@bot.message_handler(commands=['look_achiev'])
def handle_look_achiev(message):
    if message.chat.type == 'private' and additions.checkUserInGroup(bot, message.from_user.id, ALLOWED_GROUP_ID):
        achievements = db.getAllAchievements()
        messageText = "🐾\n\n_Всі ачівки і як їх отримати!_\n\n🐾\n\n"
        for achievement in achievements:
            messageText += f"*{achievement[0]}*\n\n🐾\n\n"
        bot.send_message(message.chat.id, messageText, parse_mode='Markdown')


if __name__ == '__main__':
    db.createDatabase()
    bot.infinity_polling()
    app_logger.logger.info("Bot stopped")
