from .db import DB

class WeightDB(DB):
    def __init__(self):
        super().__init__()

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
            select u.name, w.weight, w.week
            from t_weight w
            join t_user u on u.id = w.user_id
            where w.year = ?
            order by w.week
        """
        cur = self.conn.cursor()
        cur.execute(q, [year])

        rows = cur.fetchall()
        return rows

    def upsert_weight_goal(self, user_id, goal, year):
        cur = self.conn.cursor()

        q = "select * from t_weight_goal where user_id = ? and year = ?"
        cur.execute(q, [user_id, year])
        row = cur.fetchall()

        if row:
            q = "update t_weight_goal set goal = ? where user_id = ? and year = ?"
            cur.execute(q, [goal, user_id, year])
            self.conn.commit()
        else:
            q = "insert into t_weight_goal (user_id, goal, year) values (?, ?, ?)"
            cur.execute(q, [user_id, goal, year])
            self.conn.commit()

    def get_weight_goals_all(self, year):
        q = """
            select u.name, wg.goal
            from t_weight_goal wg
            join t_user u on u.id = wg.user_id
            where wg.year = ?
                or wg.year = (select max(year) from t_weight_goal)
        """
        cur = self.conn.cursor()
        cur.execute(q, [year])

        rows = cur.fetchall()
        return rows
