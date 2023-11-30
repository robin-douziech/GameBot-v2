from GameBot import *

bot = GameBot(vars_json, members_json, roles_json, events_json)
bot.remove_command("help")