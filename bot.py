import telebot
import datetime
import sqlite3

from config import TOKEN, HELP
from functions import random
from repeated_timer import RepeatedTimer

bot = telebot.TeleBot(TOKEN)
commands = {}                                       # 1-time, 2-suggest (chatId: command)
           
@bot.message_handler(commands=['start'])
def start(message, res=False):
  bot.send_message(message.chat.id, 'JokesToday на связи) Введите /help, чтобы узнать больше о командах')
  try:
    sqlite_connection = sqlite3.connect('information.db')
    cursor = sqlite_connection.cursor()
    chat = cursor.execute(f'SELECT * FROM Intervals WHERE ChatId={message.chat.id}').fetchone()
    if chat == None:
      cursor.execute(f'INSERT INTO Reads(ChatId, JokeId) VALUES ({message.chat.id}, 0)')
      hour = 10 
      step = 10 
      minute = 0

      while True:
        cursor.execute(
          f'INSERT INTO Intervals(ChatId, Hour, Minute) VALUES ({message.chat.id}, {hour}, {minute})')
        if hour >= 20:
          break
        if minute + step < 60:
          minute += step
        else: 
          hour += 1
          minute = 60 - (minute + step)
      
      sqlite_connection.commit()
    cursor.close()
  except sqlite3.Error as error:
    bot.send_message(message.chat.id, 'Ошибка при подключении к базе данных :(')
    bot.send_message(message.chat.id, error)
  finally:
    if (sqlite_connection):
      sqlite_connection.close()

@bot.message_handler(commands=['help'])
def help(message, res=False):
  bot.send_message(message.chat.id, HELP)

@bot.message_handler(commands=['random'])
def random_joke(message, res=False):
  bot.send_message(message.chat.id, random(message.chat.id))

@bot.message_handler(commands=['lifetime'])
def lifetime(message, res=False):
  global commands
  commands[message.chat.id] = 1

  try: 
    sqlite_connection = sqlite3.connect('information.db')
    cursor = sqlite_connection.cursor()

    times = cursor.execute(f'SELECT Hour FROM Intervals WHERE ChatId = {message.chat.id}').fetchall()
    min_hour, max_hour = times[0], times[-1]
    min_hour, max_hour = min_hour[0], max_hour[0]

    minutes = cursor.execute(f'SELECT Minute FROM Intervals WHERE ChatId = {message.chat.id} LIMIT 2').fetchall()
    first, second = minutes[0], minutes[1]
    first, second = first[0], second[0]
    interval = second - first

    cursor.close()
  except sqlite3.Error as error:
    bot.send_message(message.chat.id, 'Ошибка при подключении к базе данных :(')
    bot.send_message(message.chat.id, error)
  finally:
    if (sqlite_connection):
      sqlite_connection.close()

  bot.send_message(message.chat.id, f'Текущее время активности: с {min_hour} до {max_hour}\nИнтервал: {interval} мин')
  bot.send_message(message.chat.id, 'Если хотите отменить изменение, введите /cancel.\nДля продолжения введите данные в формате: начало_часы конец_часы интервал_минуты. Например:')
  bot.send_message(message.chat.id, '10 20 15')
  
@bot.message_handler(commands=['suggest'])
def suggest(message, res=False):
  global commands
  commands[message.chat.id] = 2
  bot.send_message(message.chat.id, 'Введите текст анекдота или шутки')

@bot.message_handler(commands=['cancel'])
def cancel(message, res=False):
  global commands
  commands.pop(message.chat.id, 'not command')
  bot.send_message(message.chat.id, 'Операция отменена')

@bot.message_handler(content_types=['text'])
def handle_message(message):
  global commands
  if commands.get(message.chat.id) == None:
    return
  if commands[message.chat.id] == 1:
    data = message.text.split(' ')
    begin, end, interval = int(data[0]), int(data[1]), int(data[2])
    try:
      sqlite_connection = sqlite3.connect('information.db')
      cursor = sqlite_connection.cursor()
      cursor.execute(f'DELETE FROM Intervals WHERE ChatId = {message.chat.id}')
      hour = begin 
      step = interval 
      minute = 0

      while True:
        cursor.execute(
          f'INSERT INTO Intervals(ChatId, Hour, Minute) VALUES ({message.chat.id}, {hour}, {minute})')
        if hour >= end:
          break
        if minute + step < 60:
          minute += step
        else: 
          hour += 1
          minute = 60 - (minute + step)
        
        sqlite_connection.commit()
      cursor.close()

      bot.send_message(message.chat.id, 'Обновление прошло успешно!')
    except sqlite3.Error as error:
      bot.send_message(message.chat.id, 'Ошибка при подключении к базе данных :(')
      bot.send_message(message.chat.id, error)
    finally:
      if (sqlite_connection):
        sqlite_connection.close()
    
    del commands[message.chat.id]
    return
  elif commands[message.chat.id] == 2:
    try:
      sqlite_connection = sqlite3.connect('jokes.db')
      cursor = sqlite_connection.cursor()
      cursor.execute(f'INSERT INTO Jokes(Body) VALUES ("{message.text}");')
      sqlite_connection.commit()
      cursor.close()
      bot.send_message(message.chat.id, 'Добавление прошло успешно! Команда JokesToday выражает Вам благодарность!')
    except sqlite3.Error as error:
      bot.send_message(message.chat.id, 'Ошибка при подключении к базе данных :(')
      bot.send_message(message.chat.id, error)
    finally:
      if (sqlite_connection):
        sqlite_connection.close()
    del commands[message.chat.id]
    return

def every_minute():
  try:
    sqlite_connection = sqlite3.connect('information.db')
    cursor = sqlite_connection.cursor()
    now = datetime.datetime.now()
    ids = cursor.execute(f'SELECT ChatId FROM Intervals WHERE Hour = {now.hour} AND Minute = {now.minute}').fetchall()
    if ids == None:
      return
    for id in ids:
      bot.send_message(id[0], random(id[0]))
    cursor.close()
  except sqlite3.Error as error:
    return f'Ошибка при подключении к базе данных: {error}'
  finally:
    if (sqlite_connection):
      sqlite_connection.close()

rt = RepeatedTimer(60, every_minute)
bot.polling(none_stop=True, interval=0)