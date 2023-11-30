import discord, json

from helpers import *

@bot.event
async def on_ready():

	bot.guild = bot.get_guild(bot_guild_id)
	bot.channels["bienvenue"] = bot.guild.get_channel(bienvenue_channel_id)
	bot.channels["roles"]     = bot.guild.get_channel(roles_channel_id)
	bot.channels["colocation"] = bot.guild.get_channel(colocation_channel_id)
	bot.channels["général-annonces"] = bot.guild.get_channel(general_annonces_channel_id)

	for role in role_to_channel :
		bot.channels[role] = bot.guild.get_channel(role_to_channel[role])

	with open(bot.vars_file, "rt") as f :
		bot.vars = json.load(f)
	with open(bot.members_file, "rt") as f :
		bot.members = json.load(f)
	with open(bot.roles_file, "rt") as f :
		bot.roles = json.load(f)
	with open(bot.events_file, "rt") as f :
		bot.events = json.load(f)

	for elt in ["msgid_to_eventid"] :
		if not(elt in bot.vars) :
			bot.vars[elt] = {}
	bot.write_json(bot.vars, bot.vars_file)

	bot.roles["roles_ids"] = await bot.fetch_roles_ids()
	bot.write_json(bot.roles, bot.roles_file)

	default_member_value = {
		"name": "",
		"id": "",
		"msgid_to_eventid": {}
	}

	# synchronisation des membres
	guild_members = []
	for member in bot.guild.members :
		if not(member.bot) :
			guild_members.append(f"{member.name}#{member.discriminator}")
			if member.dm_channel == None :
				await member.create_dm()
	for member in guild_members :
		if member not in bot.members :
			await bot.send_welcome_message_in_dm(member)
	members_to_remove = []
	for member in bot.members :
		if member not in guild_members :
			members_to_remove.append(member)
	for member in members_to_remove :
		bot.members.pop(member)
	for member in bot.members :
		for default_value in default_member_value :
			if not(default_value in bot.members[member]) :
				bot.members[member][default_value] = default_member_value[default_value]
	for member in bot.members :
		msgid_to_remove = []
		for msg_id in bot.members[member]["msgid_to_eventid"] :
			if bot.members[member]["msgid_to_eventid"][msg_id] not in bot.events :
				msgid_to_remove.append(msg_id)
		for msg_id in msgid_to_remove :
			bot.members[member]["msgid_to_eventid"].pop(msg_id)
	bot.write_json(bot.members, bot.members_file)

	role = await bot.get_role("colocataire")
	for member in bot.guild.members :
		if member.get_role(role.id) != None :
			bot.members[f"{member.name}#{member.discriminator}"]["event_being_created"] = 0
			bot.members[f"{member.name}#{member.discriminator}"]["questionned_event_creation"] = False
			bot.members[f"{member.name}#{member.discriminator}"]["questions"] = []
	bot.write_json(bot.members, bot.members_file)

	# suppression des soirées pas créées entièrement
	await bot.delete_unfinished_events()

	# envoi/récupération du message des rôles
	await bot.send_or_retreive_roles_msg()

	# synchronisation des roles (comparaison entre les membres ayant réagi et ceux ayant le rôle)
	for role_name in bot.roles["roles_dic"] :
		await sync_role(role_name)

	bot.log(f"{bot.user.display_name} est prêt.")

@bot.event
async def on_member_join(member) :
	complete_pseudo = f"{member.name}#{member.discriminator}"
	if member in bot.guild.members and not(complete_pseudo in bot.members) :
		await bot.send_welcome_message_in_dm(member)

@bot.event
async def on_member_remove(member) :
	complete_pseudo = f"{member.name}#{member.discriminator}"
	if complete_pseudo in bot.members and not(member in bot.guild.members) :
		for reaction in bot.roles_msg.reactions :
			await reaction.remove(member)
		bot.members.pop(complete_pseudo)
		bot.write_json(bot.members, bot.members_file)

@bot.event
async def on_raw_reaction_add(payload) :
	channel = bot.get_channel(payload.channel_id)
	message = await channel.fetch_message(payload.message_id)
	author = bot.guild.get_member(payload.user_id)

	if not(author.bot) :

		if message == bot.roles_msg :
			for role_name in bot.roles["roles_dic"] :
				if bot.roles["roles_dic"][role_name]["reaction_name"] == payload.emoji.name :
					role = await bot.get_role(role_name)
					await author.add_roles(role)

		elif message.content.endswith(role_invitation_msg_end) :
			if payload.emoji.name == chr(0x1F44D) :
				try :
					event_id = bot.vars["msgid_to_eventid"][str(message.id)]
					event = bot.events[str(event_id)]
				except :
					return
				if not(f"{author.name}#{author.discriminator}" in bot.events[str(event_id)]["membres présents"]+bot.events[str(event_id)]["liste d'attente"]) :
					bot.events[str(event_id)]["liste d'attente"].append(f"{author.name}#{author.discriminator}")
					bot.write_json(bot.events, bot.events_file)
					await bot.update_invitations_roles(event_id)

		elif channel == author.dm_channel :
			if message.content == dm_welcome_msg and payload.emoji.name == chr(0x1F197) :
				await bot.send_welcome_message_in_channel(author)
			elif message.content.startswith(member_invitation_msg_start) :
				try :
					event_id = bot.members[f"{author.name}#{author.discriminator}"]["msgid_to_eventid"][str(message.id)]
					event = bot.events[str(event_id)]
				except :
					return					
				if payload.emoji.name == chr(0x2705) : # accepter
					bot.events[str(event_id)]["membres présents"].append(f"{author.name}#{author.discriminator}")
					bot.events[str(event_id)]["membres en attente"].remove(f"{author.name}#{author.discriminator}")
					role = bot.guild.get_role(bot.events[str(event_id)]["role_id"])
					await author.add_roles(role)
					await author.dm_channel.send("Génial ! Heureux de te savoir parmi nous lors de cette soirée :slight_smile:")
					await bot.channels["colocation"].send(f"{author.name} a accepté l'invitation à la soirée \"{bot.events[str(event_id)]['name']}\"")
				elif payload.emoji.name == chr(0x274C) : # refuser
					bot.events[str(event_id)]["membres en attente"].remove(f"{author.name}#{author.discriminator}")
					await bot.channels["colocation"].send(f"{author.name} a refusé l'invitation à la soirée \"{bot.events[str(event_id)]['name']}\"")
					await author.dm_channel.send("Très bien, peut-être une prochaine fois alors")
					await bot.update_invitations_members(event_id)
				event_id = bot.members[f"{author.name}#{author.discriminator}"]["msgid_to_eventid"].pop(str(message.id))
				bot.write_json(bot.members, bot.members_file)
				bot.write_json(bot.events, bot.events_file)

@bot.event
async def on_raw_reaction_remove(payload) :
	channel = bot.get_channel(payload.channel_id)
	message = await channel.fetch_message(payload.message_id)
	try :
		author = bot.guild.get_member(payload.user_id)
	except :
		return

	if not(author.bot) :

		if message == bot.roles_msg :
			for role_name in bot.roles["roles_dic"] :
				if bot.roles["roles_dic"][role_name]["reaction_name"] == payload.emoji.name :
					role = await bot.get_role(role_name)
					await author.remove_roles(role)

		elif message.content.endswith(role_invitation_msg_end) :
			if payload.emoji.name == chr(0x1F44D) :
				try :
					event_id = bot.vars["msgid_to_eventid"][str(message.id)]
					event = bot.events[str(event_id)]
				except :
					return
				role_colocataire = bot.guild.get_role(bot.roles["roles_ids"]["colocataire"])
				if author.get_role(role_colocataire.id) == None :
					if f"{author.name}#{author.discriminator}" in bot.events[str(event_id)]["liste d'attente"] :
						bot.events[str(event_id)]["liste d'attente"].remove(f"{author.name}#{author.discriminator}")
						bot.write_json(bot.events, bot.events_file)
						await author.dm_channel.send(f"Tu as été retiré(e) de la liste d'attente pour cette soirée.")
					elif f"{author.name}#{author.discriminator}" in bot.events[str(event_id)]["membres présents"] :
						role = bot.guild.get_role(bot.events[str(event_id)]["role_id"])
						await author.remove_roles(role)
						await author.dm_channel.send(f"Tu as été supprimé des personnes présentes à la soirée \"{bot.events[str(event_id)]['name']}\"")
						await bot.channels["colocation"].send(f"{author.name} as été supprimé des personnes présentes à la soirée \"{bot.events[str(event_id)]['name']}\"")
						bot.events[str(event_id)]["membres présents"].remove(f"{author.name}#{author.discriminator}")
						bot.write_json(bot.events, bot.events_file)
						await bot.update_invitations_roles(event_id)
					else :
						pass				

@bot.event
async def on_message(message) :
	bot.log(f"[{message.channel}] {message.content}")
	if message.content.startswith(bot.command_prefix) :
		await bot.process_commands(message)
	else :
		await bot.process_msg(message)