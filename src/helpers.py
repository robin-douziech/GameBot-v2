from bot import *

async def get_reactors(message, emoji_name) :
	reactors = []
	for reaction in message.reactions :
		if reaction.emoji == emoji_name :
			async for user in reaction.users(limit=1000) :
				if not(user.bot) :
					reactors.append(user)
	return reactors

async def sync_role(role_name) :
	role = await bot.get_role(role_name)
	reaction_name = bot.roles["roles_dic"][role_name]["reaction_name"]
	reactors = await get_reactors(bot.roles_msg, reaction_name)
	role_owners = role.members
	for member in reactors :
		if member not in role_owners :
			await member.add_roles(role)
	for member in role_owners :
		if member not in reactors :
			await member.remove_roles(role)
	bot.roles["roles_dic"][role_name]["members"] = []
	for member in role.members :
		bot.roles["roles_dic"][role_name]["members"].append(f"{member.name}#{member.discriminator}")
	bot.write_json(bot.roles, bot.roles_file)