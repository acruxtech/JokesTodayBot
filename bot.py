from pickle import GET
import telebot
import random

from config import TOKEN, HELP

import sqlite3
from db.request import GET_AMOUNT_JOKES

bot = telebot.TeleBot(TOKEN)
command = 0           # 0-нет, 1-lifetimeBegin, 2-lifetimeEnd, 3-interval, 4-suggest

@bot.message_handler(commands=["start"])
def start(message, res=False):
  bot.send_message(message.chat.id, 'JokesToday на связи) Пишите /help, чтобы узнать больше о командах')

@bot.message_handler(commands=["help"])
def help(message, res=False):
  bot.send_message(message.chat.id, HELP)

@bot.message_handler(commands=["random"])
def random_joke(message, res=False):
  id = 0
  amount = 0
  try:
    sqlite_connection = sqlite3.connect('db/database.db')
    cursor = sqlite_connection.cursor()
    amount = cursor.execute(GET_AMOUNT_JOKES).fetchone()
    bot.send_message(message.chat.id, amount)

    while True:
      id = random.randint(1, amount)
      read_id = cursor.execute(GET_AMOUNT_JOKES).fetchone()
    cursor.close()

  except sqlite3.Error as error:
    bot.send_message(message.chat.id, "Ошибка при подключении к базе данных :(", error)
  finally:
    if (sqlite_connection):
      sqlite_connection.close()

@bot.message_handler(content_types=["text"])
def handle_command(message):
  global command
  if command == 0:
    bot.send_message(message.chat.id, 'Неизвестная команда! /help')
    return
  elif command == 1:
    bot.send_message(message.chat.id, 'lifetime begin')
    command = 0
    return
  elif command == 2:
    bot.send_message(message.chat.id, 'lifetime end')
    command = 0
    return
  elif command == 3:
    bot.send_message(message.chat.id, 'interval')
    command = 0
    return
  elif command == 4:
    bot.send_message(message.chat.id, 'suggest')
    command = 0
    return
  #bot.send_message(message.chat.id, 'Вы написали: ' + message.text)

bot.polling(none_stop=True, interval=0)