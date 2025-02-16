import sqlite3


# TODO: АККУРАТНО ВЫПИЛИТЬ БД ИЗ РЕПОЗИТОРИЯ ЧТОБЫ НЕ СЛОМАТЬ БОТИКА
class DB:
    def __init__(self):
        self.conn = sqlite3.connect('dailybot_db.db3', check_same_thread=False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
