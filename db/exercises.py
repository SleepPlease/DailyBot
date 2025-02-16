from .db import DB


class ExercisesDB(DB):
    def __init__(self):
        super().__init__()

    # create table t_exercises_progress(
    #     user_id integer,
    #     type string,
    #     reps integer,
    #     day integer,
    #     year integer,
    #     primary key (user_id, type, day, year)
    # );

    def upsert_abs(self, user_id, value, day, year):
        self._upsert_exercises("abs", user_id, value, day, year)

    def upsert_arms(self, user_id, value, day, year):
        self._upsert_exercises("arms", user_id, value, day, year)

    def upsert_legs(self, user_id, value, day, year):
        self._upsert_exercises("legs", user_id, value, day, year)

    def _upsert_exercises(self, ex_type, user_id, value, day, year):
        cur = self.conn.cursor()

        q = f"select * from t_exercises_progress where user_id = {user_id} and type = '{ex_type}' and day = {day} and year = {year}"
        cur.execute(q)

        row = cur.fetchall()
        if row:
            q = f"update t_exercises_progress set reps = {value} where user_id = {user_id} and type = '{ex_type}' and day = {day} and year = {year}"
            cur.execute(q)
            self.conn.commit()
        else:
            q = f"insert into t_exercises_progress (user_id, type, reps, day, year) values ({user_id}, '{ex_type}', {value}, {day}, {year})"
            cur.execute(q)
            self.conn.commit()

    def get_abs(self, user_id, year):
        return self._get_exercises("abs", user_id, year)

    def get_arms(self, user_id, year):
        return self._get_exercises("arms", user_id, year)

    def get_legs(self, user_id, year):
        return self._get_exercises("legs", user_id, year)

    def _get_exercises(self, ex_type, user_id, year):
        cur = self.conn.cursor()

        q = f"""
            select ep.day, ep.reps from t_exercises_progress ep
            where ep.user_id = {user_id} and ep.type = '{ex_type}' and ep.year = {year}
            order by ep.reps desc
            limit 7
        """

        cur.execute(q)
        rows = cur.fetchall()
        return rows
