import sqlite3


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('dailybot_db.db3', check_same_thread=False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def upsert_weight(self, user_id, weight, week, year):
        cur = self.conn.cursor()

        q = "select * from t_weight where user_id = ? and week = ? and year = ?"
        cur.execute(q, [user_id, week, year])
        row = cur.fetchall()

        if row:
            q = "update t_weight set weight = ? where user_id = ? and week = ? and year = ?"
            cur.execute(q, [weight, user_id, week, year])
            self.conn.commit()
        else:
            q = "insert into t_weight (user_id, weight, week, year) values (?, ?, ?, ?)"
            cur.execute(q, [user_id, weight, week, year])
            self.conn.commit()


    def get_weights_all(self, year):
        q = """
            select u.name, w.weight, w.week, w.year
            from t_weight w
            join t_user u on u.id = w.user_id
            where w.year = ?
            order by w.week
        """
        cur = self.conn.cursor()
        cur.execute(q, [year])

        rows = cur.fetchall()
        return rows
