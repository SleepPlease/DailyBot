class BotModule(object):
    def __init__(self, title, bot):
        self.title = title
        self.bot = bot
        self.menu_markup = None

        self.callbacks = {}

    def add_menu_markup(self, menu_markup):
        self.menu_markup = menu_markup
