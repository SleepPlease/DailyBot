class BotModule(object):
    def __init__(self, title, bot):
        self.title = title
        self.bot = bot
        self.menu_markup = None

        self.callbacks = {}

    def add_menu_markup(self, menu_markup):
        self.menu_markup = menu_markup


class Callback(object):
    def __init__(self, module, name, text, func):
        self.name = module.lower() + "." + name
        self.text = text
        self.func = func
        self.children = []

    def add_child(self, cb):
        self.children.append(cb)
