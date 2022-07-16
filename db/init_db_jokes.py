import sqlite3

from request import CREATE_JOKES

try:
  sqlite_connection = sqlite3.connect('jokes.db')
  cursor = sqlite_connection.cursor()
  print("База данных подключена к SQLite")
  cursor.execute(CREATE_JOKES)
  sqlite_connection.commit()
  print("Таблица SQLite создана")
  cursor.close()

except sqlite3.Error as error:
  print("Ошибка при подключении к sqlite", error)
  
finally:
  if (sqlite_connection):
    sqlite_connection.close()
    print("Соединение с SQLite закрыто")