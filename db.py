import sqlite3


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('dailybot_db.db3', check_same_thread=False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def add_weight(self, user_id, weight):
        q = "insert into t_weight (user_id, weight) values (?, ?)"
        cur = self.conn.cursor()
        cur.execute(q, [user_id, weight])
        self.conn.commit()

    def get_weights_all(self):
        q = """
            select u.name, w.weight, w.dt
            from t_weight w
            join t_user u on u.id = w.user_id
            order by w.dt
        """
        cur = self.conn.cursor()
        cur.execute(q)

        rows = cur.fetchall()
        return rows
