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

async def sync_poll(poll_id) :
	channel = bot.guild.get_channel(bot.polls[str(poll_id)]["channel_id"])
	message = await channel.fetch_message(bot.polls[str(poll_id)]["msg_id"])
	for reaction_name in bot.polls[str(poll_id)]["reactions"] :
		reactors = await get_reactors(message, reaction_name)
		reactors_message = [f"{reactor.name}#{reactor.discriminator}" for reactor in reactors]
		reactors_bot = bot.polls[str(poll_id)]["results"][reaction_name]
		for member in reactors_message :
			if member not in reactors_bot :
				bot.polls[str(poll_id)]["results"][reaction_name].append(member)
		for member in reactors_bot :
			if member not in reactors_message :
				bot.polls[str(poll_id)]["results"][reaction_name].remove(member)
	bot.write_json(bot.polls, bot.polls_file)

def poll_results(poll_id) :
	labels = range(1, len(bot.polls[str(poll_id)]['reactions'])+1)
	data = [len(bot.polls[str(poll_id)]['results'][option]) for option in bot.polls[str(poll_id)]['reactions']]
	fig, ax = plt.subplots()
	bars = ax.bar(labels, data, color="blue")
	ax.set_xlabel('Options')
	ax.set_ylabel('Nombre de réponses')
	ax.set_title('Résultats du sondage')
	for bar in bars :
		yval = bar.get_height()
		ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 1), ha='center', va='bottom')
	plt.savefig(f"poll_{poll_id}.png")