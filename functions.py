import sqlite3
from db.request import GET_AMOUNT_JOKES

def random(chatId):
  try:
    jokes_connect = sqlite3.connect('jokes.db')
    jokes_cursor = jokes_connect.cursor()
    info_connect = sqlite3.connect('information.db')
    info_cursor = info_connect.cursor()

    amount = jokes_cursor.execute(GET_AMOUNT_JOKES).fetchone()
    amount = amount[0]
    read_id = info_cursor.execute(f'SELECT JokeId FROM Reads WHERE ChatId = {chatId}' ).fetchone()
    id = read_id[0]
    if id + 1 > amount:
      id = 1
    else:
      id += 1

    joke = jokes_cursor.execute(f'SELECT Body FROM Jokes WHERE Id = {id}').fetchone()
    info_cursor.execute(f'UPDATE Reads SET JokeId = {id} WHERE ChatId = {chatId}')
    info_connect.commit()

    info_cursor.close()
    jokes_cursor.close()
  except sqlite3.Error as error:
    return f'Ошибка при подключении к базе данных: {error}'
  finally:
    if (info_connect):
      info_connect.close()
    if (jokes_connect):
      jokes_connect.close()
    return joke[0]