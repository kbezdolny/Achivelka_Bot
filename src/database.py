import sqlite3
import os
from exceptions import AchievementAlreadyExists
from app_logger import logger


def createDatabase():
    connection = createConnection()
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            image_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            username TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            user_id INTEGER,
            achievement_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (achievement_id) REFERENCES achievements(achievement_id),
            PRIMARY KEY (user_id, achievement_id)
        )
    ''')

    connection.commit()
    connection.close()


def createConnection():
    dbPath = "../resources/botDb.db"
    if not os.path.exists("resources"):
        os.makedirs("resources")

    try:
        connection = sqlite3.connect(dbPath)
        return connection
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None


def checkAchievementExists(achievement_name):
    connection = createConnection()
    if not connection:
        return

    cursor = connection.cursor()
    cursor.execute('SELECT achievement_id FROM achievements WHERE name = ?', (achievement_name,))
    achievement_row = cursor.fetchone()
    connection.close()

    return achievement_row is not None


def createAchievement(achievement_name, image_name):
    connection = createConnection()
    if not connection:
        return

    cursor = connection.cursor()
    cursor.execute('INSERT INTO achievements (name, image_name) VALUES (?, ?)', (achievement_name, image_name))
    connection.commit()
    cursor.close()
    logger.info("Created a new achievement")


def addAchievement(username, achievement_id):
    connection = createConnection()
    if not connection:
        return

    cursor = connection.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_row = cursor.fetchone()
    if user_row is None:
        cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
        user_id = cursor.lastrowid
    else:
        user_id = user_row[0]

    cursor.execute('SELECT * FROM user_achievements WHERE user_id = ? AND achievement_id = ?', (user_id, achievement_id))
    relation_row = cursor.fetchone()
    if relation_row is None:
        cursor.execute('INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, ?)', (user_id, achievement_id))
    else:
        raise AchievementAlreadyExists.AchievementAlreadyExists()

    connection.commit()
    connection.close()
    logger.info(f"Added a new achievement to the user: @{username}")


def getMyAchievements(username):
    connection = createConnection()
    if not connection:
        return

    cursor = connection.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_row = cursor.fetchone()

    data = None
    if user_row is not None:
        user_id = user_row[0]

        cursor.execute('''
            SELECT a.name, a.image_name
            FROM achievements a
            INNER JOIN user_achievements ua ON a.achievement_id = ua.achievement_id
            WHERE ua.user_id = ?
        ''', (user_id,))

        data = cursor.fetchall()

    connection.close()
    return data


def getAllAchievements():
    connection = createConnection()
    if not connection:
        return

    cursor = connection.cursor()
    cursor.execute('SELECT name, achievement_id, image_name FROM achievements')
    rows = cursor.fetchall()
    connection.close()
    return rows


def getMyRank(username):
    connection = createConnection()
    if not connection:
        return

    cursor = connection.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_row = cursor.fetchone()

    data = None
    if user_row is not None:
        user_id = user_row[0]

        cursor.execute('''
            SELECT COUNT(ua.achievement_id)
            FROM user_achievements ua
            WHERE ua.user_id = ?
        ''', (user_id,))

        data = cursor.fetchone()[0] // 3

    connection.close()
    return data
