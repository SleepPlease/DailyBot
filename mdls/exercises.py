from .bot_utils import BotModule, Callback
from db import DB


class Exercises(BotModule):
    def __init__(self, bot):
        super(Exercises, self).__init__("Exercises", bot)
        self.db = DB()
        self.callbacks = [
            Callback(self.title, "abs", "Abs", self.kekw),
            Callback(self.title, "squat", "Squat", self.kekw),
            Callback(self.title, "push-up", "Push-up", self.kekw),
        ]

    def kekw(self):
        pass
# https://matplotlib.org/stable/gallery/statistics/histogram_multihist.html#sphx-glr-gallery-statistics-histogram-multihist-py
