from helpers import *

@bot.event
async def on_ready():

	bot.guild = bot.get_guild(bot_guild_id)
	bot.channels["bienvenue"] = bot.guild.get_channel(bienvenue_channel_id)
	bot.channels["roles"]     = bot.guild.get_channel(roles_channel_id)
	bot.channels["colocation"] = bot.guild.get_channel(colocation_channel_id)
	bot.channels["général-annonces"] = bot.guild.get_channel(general_annonces_channel_id)
	bot.channels["test"] = bot.guild.get_channel(test_channel_id)

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
	with open(bot.games_file, "rt") as f :
		bot.games = json.load(f)
	with open(bot.rankings_file, "rt") as f :
		bot.rankings = json.load(f)
	with open(bot.polls_file, "rt") as f :
		bot.polls = json.load(f)

	bot.news = {}
	bot.write_json(bot.news, bot.news_file)

	for elt in ["msgid_to_eventid"] :
		if not(elt in bot.vars) :
			bot.vars[elt] = {}
	bot.write_json(bot.vars, bot.vars_file)

	for elt in ["parties", "old_parties"] :
		if not(elt in bot.rankings) :
			bot.rankings[elt] = {}
	bot.write_json(bot.rankings, bot.rankings_file)

	for category in games_categories :
		if not(category in bot.games) :
			bot.games[category] = {}
	bot.write_json(bot.games, bot.games_file)

	bot.roles["roles_ids"] = await bot.fetch_roles_ids()
	bot.write_json(bot.roles, bot.roles_file)

	# envoi/récupération du message des rôles
	await bot.send_or_retreive_roles_msg()

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
		await bot.remove_member_from_all_events(member)
		await bot.channels["colocation"].send(f"{member} est parti(e), il faut aller retirer ses réactions au message des rôles svp.")
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
			bot.members[f"{member.name}#{member.discriminator}"]["game_being_created"] = 0
			bot.members[f"{member.name}#{member.discriminator}"]["poll_being_created"] = 0
			bot.members[f"{member.name}#{member.discriminator}"]["news_being_created"] = 0
			bot.members[f"{member.name}#{member.discriminator}"]["questionned_event_creation"] = False
			bot.members[f"{member.name}#{member.discriminator}"]["questionned_game_creation"] = False
			bot.members[f"{member.name}#{member.discriminator}"]["questionned_poll_creation"] = False
			bot.members[f"{member.name}#{member.discriminator}"]["questionned_news_creation"] = False
			bot.members[f"{member.name}#{member.discriminator}"]["questions"] = []
	bot.write_json(bot.members, bot.members_file)

	# suppression des soirées/jeux/sondages pas créés entièrement
	await bot.delete_unfinished_events()
	bot.delete_unfinished_games()
	bot.delete_unfinished_polls()

	# synchronisation des roles (comparaison entre les membres ayant réagi et ceux ayant le rôle)
	for role_name in bot.roles["roles_dic"] :
		await sync_role(role_name)

	# synchronisation des résultats des sondages
	for poll_id in bot.polls :
		await sync_poll(poll_id)

	game_list = []
	for category in games_categories :
		game_list += list(bot.games[category].keys())
	game = random.choice(game_list)
	await bot.change_presence(activity=discord.Game(f"{game}"))

	now = dt.datetime.now().strftime('%d/%m/%y %H:%M')
	date = now.split()[0]
	time = now.split()[1]

	day = date.split('/')[0]
	month = date.split('/')[1]
	year = date.split('/')[2]

	hours = time.split(':')[0]
	minutes = time.split(':')[1]

	if (int(hours)+int(bot.vars['clock_hour_offset'])) > 23 :
		hours = str((int(hours)+int(bot.vars['clock_hour_offset']))%24)
		if len(hours) < 2 :
			hours = f"0{hours}"
		day = str(int(day)+1)
		if len(day) < 2 :
			day = f"0{day}"
		if int(day) > int(calendar.monthrange(int(year), int(month))[1]) :
			day = "01"
			month = str(int(month)+1)
			if len(month) < 2 :
				month = f"0{month}"
			if int(month) > 12 :
				month = "01"
				year = str(int(year)+1)

	time = f"{hours}:{minutes}"

	try :
		os.makedirs(f"logs/20{year}/{month}")
	except :
		pass

	formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
	handler = logging.FileHandler(f"logs/20{year}/{month}/{day}.log")
	handler.setFormatter(formatter)
	logging.getLogger().handlers = [handler]

	bot.log(f"{bot.user.display_name} est prêt.")
	print(f"{bot.user.display_name} est prêt.")

	clock.start()

@bot.event
async def on_member_join(member) :
	complete_pseudo = f"{member.name}#{member.discriminator}"
	if member in bot.guild.members and not(complete_pseudo in bot.members) :
		await bot.send_welcome_message_in_dm(member)

@bot.event
async def on_member_remove(member) :
	complete_pseudo = f"{member.name}#{member.discriminator}"
	if complete_pseudo in bot.members and not(member in bot.guild.members) :
		await bot.channels["colocation"].send(f"{member} est parti(e), il faut aller retirer ses réactions au message des rôles svp.")
		await bot.remove_member_from_all_events(f"{member.name}#{member.discriminator}")
		bot.members.pop(complete_pseudo)
		bot.write_json(bot.members, bot.members_file)

@bot.event
async def on_raw_reaction_add(payload) :
	channel = bot.get_channel(payload.channel_id)
	message = await channel.fetch_message(payload.message_id)
	author = bot.guild.get_member(payload.user_id)

	role_colocataire = bot.guild.get_role(bot.roles["roles_ids"]["colocataire"])

	if not(author.bot) :

		if message.author.bot :

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
						if not(f"{author.name}#{author.discriminator}" in bot.events[str(event_id)]["membres présents"]+bot.events[str(event_id)]["liste d'attente"]) :
							bot.events[str(event_id)]["liste d'attente"].append(f"{author.name}#{author.discriminator}")
							bot.write_json(bot.events, bot.events_file)
							await bot.update_invitations_roles(event_id)
					except :
						await author.dm_channel.send("Je n'arrive plus à trouver cette soirée jeux, elle a sûrement été supprimée")

			elif channel == author.dm_channel :
				if message.content == dm_welcome_msg and payload.emoji.name == chr(0x1F197) :
					await bot.send_welcome_message_in_channel(author)
				elif message.content.startswith(member_invitation_msg_start) :
					if payload.emoji.name in [chr(0x2705), chr(0x274C)] :
						try :
							event_id = bot.members[f"{author.name}#{author.discriminator}"]["msgid_to_eventid"][str(message.id)]
							event = bot.events[str(event_id)]		
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
						except :
							await author.dm_channel.send("Je n'arrive plus à trouver cette soirée jeux, elle a sûrement été supprimée")
			
			else :
				for poll_id in bot.polls :
					if message.id == bot.polls[poll_id]["msg_id"] and payload.emoji.name in bot.polls[poll_id]["reactions"] :
						bot.polls[poll_id]["results"][payload.emoji.name].append(f"{author.name}#{author.discriminator}")
						bot.write_json(bot.polls, bot.polls_file)

		else :
			if channel == author.dm_channel :
				if author.get_role(role_colocataire.id) != None :
					for poll_id in bot.polls :
						if message.id == bot.polls[poll_id]["dm_msg_id"] and not(bot.polls[poll_id]["creation_finished"]) :
							bot.polls[poll_id]["reactions"].append(payload.emoji.name)
							bot.polls[poll_id]["results"][payload.emoji.name] = []
							bot.write_json(bot.polls, bot.polls_file)

@bot.event
async def on_raw_reaction_remove(payload) :
	channel = bot.get_channel(payload.channel_id)
	message = await channel.fetch_message(payload.message_id)
	try :
		author = bot.guild.get_member(payload.user_id)
	except :
		return

	role_colocataire = bot.guild.get_role(bot.roles["roles_ids"]["colocataire"])

	if not(author.bot) :

		if message.author.bot :

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
					except :
						await author.dm_channel.send("Je n'arrive plus à trouver cette soirée jeux, elle a sûrement été supprimée")

			else: 
				for poll_id in bot.polls :
					if message.id == bot.polls[poll_id]["msg_id"] and payload.emoji.name in bot.polls[poll_id]["reactions"] :
						bot.polls[poll_id]["results"].pop(f"{author.name}#{author.discriminator}")
						bot.write_json(bot.polls, bot.polls_file)


		else :
			if channel == author.dm_channel :
				if author.get_role(role_colocataire.id) != None :
					for poll_id in bot.polls :
						if message.id == bot.polls[poll_id]["dm_msg_id"] and not(bot.polls[poll_id]["creation_finished"]) :
							bot.polls[poll_id]["reactions"].remove(payload.emoji.name)
							bot.polls[poll_id]["results"].pop(payload.emoji.name)
							bot.write_json(bot.polls, bot.polls_file)

@bot.event
async def on_message(message) :
	author = bot.guild.get_member(message.author.id)
	if not(author.bot) and message.channel == author.dm_channel :
		bot.log(f"DM message from {author.name}#{author.discriminator} : {message.content}")
	if message.content.startswith(bot.command_prefix) :
		await bot.process_commands(message)
	else :
		await bot.process_msg(message)

@tasks.loop(seconds = 60)
async def clock() :

	now = dt.datetime.now().strftime('%d/%m/%y %H:%M')
	date = now.split()[0]
	time = now.split()[1]

	day = date.split('/')[0]
	month = date.split('/')[1]
	year = date.split('/')[2]

	hours = time.split(':')[0]
	minutes = time.split(':')[1]
	
	if (int(hours)+int(bot.vars['clock_hour_offset'])) > 23 :
		day = str(int(day)+1)
		if len(day) < 2 :
			day = f"0{day}"
		if int(day) > int(calendar.monthrange(int(year), int(month))[1]) :
			day = "01"
			month = str(int(month)+1)
			if len(month) < 2 :
				month = f"0{month}"
			if int(month) > 12 :
				month = "01"
				year = str(int(year)+1)

	hours = str((int(hours)+int(bot.vars['clock_hour_offset']))%24)
	if len(hours) < 2 :
		hours = f"0{hours}"

	time = f"{hours}:{minutes}"

	if (hours in ['22', '23', '24', '00'] and minutes in ['00', '15', '30', '45']) or (hours=='23' and int(minutes)>50) or (hours in ['24', '00'] and int(minutes)<10) :
		await bot.channels["test"].send(f"Nous sommes le {day}/{month}/{year} et il est {time}")

	if day == "01" and time == "00:00": 
		bot.archive_rankings()
		bot.log("Classements archivés")
		await bot.channels["test"].send("Classements archivés")

	if minutes == "00" :
		game_list = []
		for category in games_categories :
			game_list += list(bot.games[category].keys())
		game = random.choice(game_list)
		await bot.change_presence(activity=discord.Game(f"{game}"))

	if time == "00:00" :
		await bot.channels["test"].send("Changement de jour")
		bot.log(f"Nouveau jour : nous sommes le {day}/{month}/{year}")
		if int(day) == 1 :
			await bot.channels["test"].send("Changement de mois")
			if int(month) == 1 :
				await bot.channels["test"].send("Changement d'année")
				try :
					os.makedirs(f"logs/20{year}")
				except :
					await bot.channels["test"].send("error 1")
			try :
				os.makedirs(f"logs/20{year}/{month}")
			except :
				await bot.channels["test"].send("error 2")
		formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
		handler = logging.FileHandler(f"logs/20{year}/{month}/{day}.log")
		handler.setFormatter(formatter)
		logging.getLogger().handlers = [handler]
