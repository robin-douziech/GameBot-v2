from bot_start import *

@bot.command(name="event")
@bot.dm_command
@bot.colocataire_command
async def event_gamebot(ctx, crud=None, event_id=None, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if crud == None :
		msg = f"Usage: !event [create|read|update|delete]"
		await ctx.author.dm_channel.send(msg)

	elif crud == "create" :
		if bot.members[f"{author.name}#{author.discriminator}"]["questions"] == [] :
			id_number = 1
			while str(id_number) in bot.events :
				id_number += 1
			role_soirees_jeux = await bot.get_role("soirées jeux")
			role_colocataire = await bot.get_role("colocataire")
			category = discord.utils.get(bot.guild.categories, id=soirees_jeux_cat_id)
			role_tmp = await bot.get_role(str(id_number))
			channel_tmp = await bot.guild.create_text_channel(name=str(id_number), category=category)
			await channel_tmp.set_permissions(role_tmp, read_messages=True, send_messages=True)
			await channel_tmp.set_permissions(role_soirees_jeux, read_messages=False, send_messages=False)
			bot.events[str(id_number)] = {
				"name": "",
				"date": "",
				"heure": "",
				"description": "",
				"nb_max_joueurs": "",
				"type_invités": "",

				"liste d'attente": [], # les membres pas encore invité
				"membres en attente": [], # les membres invité qui n'ont pas encore répondu
				"membres présents": [], # les membres invités qui ont répondu "oui"
				"rôles invités": [],
				"vips": [],

				"role_id": role_tmp.id,
				"channel_id": channel_tmp.id,
				"creation_finished": False
			}
			for member in bot.guild.members :
				if member.get_role(role_colocataire.id) != None :
					await member.add_roles(role_tmp)
					bot.events[str(id_number)]["membres présents"].append(f"{member.name}#{member.discriminator}")
			bot.write_json(bot.events, bot.events_file)

			bot.members[f"{author.name}#{author.discriminator}"]["event_being_created"] = id_number
			bot.members[f"{author.name}#{author.discriminator}"]["questions"] = ["", *list(event_creation_questions.keys())]
			bot.members[f"{author.name}#{author.discriminator}"]["questionned_event_creation"] = True
			bot.write_json(bot.members, bot.members_file)

			await bot.send_next_question(author, event_creation_questions)

		else :
			await author.dm_channel.send("Finis de répondre à mes questions avant de créer une nouvelle soirée")

	elif crud == "read" :
		if event_id == None :
			msg = ""
			for event_id in bot.events :
				if bot.events[event_id]["type_invités"] == "membres" :
					if bot.events[event_id]["nb_max_joueurs"] == "infinity" :
						msg += f"{event_id} : {bot.events[event_id]['name']} (présents:{len(bot.events[event_id]['membres présents'])} invités:{len(bot.events[event_id]['membres en attente'])})\n"
					else :
						msg += f"{event_id} : {bot.events[event_id]['name']} (présents:{len(bot.events[event_id]['membres présents'])}/{bot.events[event_id]['nb_max_joueurs']} invités:{len(bot.events[event_id]['membres en attente'])})\n"
				else :
					if bot.events[event_id]["nb_max_joueurs"] == "infinity" :
						msg += f"{event_id} : {bot.events[event_id]['name']} (présents:{len(bot.events[event_id]['membres présents'])})\n"
					else :
						msg += f"{event_id} : {bot.events[event_id]['name']} (présents:{len(bot.events[event_id]['membres présents'])}/{bot.events[event_id]['nb_max_joueurs']})\n"
			if msg == "" :
				await author.dm_channel.send("Aucune soirée de prévue pour le moment")
			else :
				await author.dm_channel.send(msg)
		else :
			try :
				msg = ""
				for info in bot.events[event_id] :
					msg += f"{info} : {bot.events[str(event_id)][str(info)]}\n"
				await author.dm_channel.send(msg)
			except :
				await author.dm_channel.send("L'identifiant de soirée que tu as renseigné est invalide.")

	elif crud == "update" :
		if event_id is not None :
			if len(args) > 0 :
				if args[0] == "-p":
					if bot.events[str(event_id)]["nb_max_joueurs"] != "infinity":
						if len(args) > 1 :
							if re.match(r"^([+-][1-9][0-9]*)$", args[1]) :
								if args[1][0] == "+":
									bot.events[str(event_id)]["nb_max_joueurs"] = str(int(bot.events[str(event_id)]["nb_max_joueurs"]) + int(args[1][1:]))
									bot.write_json(bot.events, bot.events_file)
									if bot.events[str(event_id)]["type_invités"] == "membres":
										await bot.update_invitations_members(str(event_id))
									else:
										await bot.update_invitations_roles(str(event_id))
									await author.dm_channel.send("Nombre maximum d'invités modifié avec succès")
								else :
									available_places = int(bot.events[str(event_id)]["nb_max_joueurs"]) - len(bot.events[str(event_id)]["membres présents"])
									if int(args[1][1:]) < available_places :
										bot.events[str(event_id)]["nb_max_joueurs"] = str(int(bot.events[str(event_id)]["nb_max_joueurs"]) - int(args[1][1:]))
										bot.write_json(bot.events, bot.events_file)
										await author.dm_channel.send("Nombre maximum d'invités modifié avec succès")
									else :
										await author.dm_channel.send("Tu ne peux pas retirer autant de places : il reste moins de places disponibles que ça")
							else :
								await author.dm_channel.send(f"Paramètre {args[1]} incorrect pour l'option -p")
						else :
							await author.dm_channel.send("Arguments insuffisants")
					else :
						await author.dm_channel.send("Tu ne peux pas modifier le nombre maximum d'invités pour cette soirée.")
				else :
					await author.dm_channel.send(f"Option {args[0]} inconue")
			else :
				await author.dm_channel.send("Arguments insuffisants")
		else :
			await author.dm_channel.send("Tu dois préciser l'identifiant de la soirée à modifier")

	elif crud == "delete" :
		if event_id == None :
			await author.dm_channel.send("Tu dois préciser l'identifiant de la soirée à supprimer.\nUtilisation : !event delete [event_id]")
		else :
			try :
				await bot.delete_event(event_id)
				await author.dm_channel.send("La soirée a bien été supprimée")
			except :
				await author.dm_channel.send("L'identifiant de soirée que tu as renseigné est invalide.")

@bot.command(name="invite")
@bot.dm_command
@bot.colocataire_command
async def invite_gamebot(ctx, event_id=None, arg=None, delete=None, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if event_id == None or arg == None :
		await author.dm_channel.send("Utilisation : !invit [event_id] [pseudo ou role]")
		return

	if delete == None :
		if str(event_id) in bot.events :
			try :

				# inviter un membre
				if bot.events[str(event_id)]["type_invités"] == "membres" :
					if str(arg) in bot.members :
						role_soirees_jeux = await bot.get_role("soirées jeux")
						Member = bot.fetch_member(str(arg))
						if Member.get_role(role_soirees_jeux.id) != None :
							if str(arg) not in bot.events[str(event_id)]["liste d'attente"]+bot.events[str(event_id)]["membres en attente"]+bot.events[str(event_id)]["membres présents"] :
								bot.events[str(event_id)]["liste d'attente"].append(str(arg))
								bot.write_json(bot.events, bot.events_file)
								#await bot.update_invitations_members(event_id)
							else :
								await author.dm_channel.send(f"{arg} est déjà invité(e) à cette soirée")
						else :
							await author.dm_channel.send(f"{arg} ne possède pas le rôle \"soirées jeux\".")
					else :
						raise ValueError("Membre introuvable")

				# inviter un rôle
				elif bot.events[str(event_id)]["type_invités"] == "roles":
					if str(arg) in bot.roles["roles_ids"] :
						if not(str(arg) in bot.events[str(event_id)]["rôles invités"]) :
							try :
								role = await bot.get_role(str(arg))
								await bot.invite_role_to_event(event_id, role)
							except :
								await author.dm_channel.send("Tu ne peux pas inviter ce rôle")
						else :
							await author.dm_channel.send(f"Le rôle {arg} est déjà invité.")
					else :
						await author.dm_channel.send(f"Le rôle {arg} n'existe pas.")

			except Exception as e :
				await author.dm_channel.send("Le pseudo ou le rôle que tu as renseigné est invalide.")
		else :
			await author.dm_channel.send("L'identifiant de soirée que tu as renseigné est invalide.")

	elif delete == "delete" :
		if str(event_id) in bot.events :
			if str(arg) in bot.members :
				try :
					Member = bot.fetch_member(str(arg))
					await bot.remove_guest_from_event_members(event_id, Member)
					await author.dm_channel.send("Participant retiré avec succès !")
				except :
					await author.dm_channel.send(f"{arg} ne fais pas partie des participants à cette soirée.")
			else :
				await author.dm_channel.send(f"{arg} n'est pas le pseudo d'un membre du serveur")
		else :
			await author.dm_channel.send("L'identifiant de soirée que tu as renseigné est invalide.")

	else: 
		await author.dm_channel.send("Utilisation : !invite event_id pseudo [delete]")

@bot.command(name="send")
@bot.dm_command
@bot.colocataire_command
async def send_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if len(args) > 0 :
		if str(args[0]) in bot.events :
			if bot.events[str(args[0])]["type_invités"] == "membres" :
				await bot.update_invitations_members(str(args[0]))
				await author.dm_channel.send(f"Invitations envoyées pour la soirée \"{bot.events[str(args[0])]['name']}\"")
			else :
				await author.dm_channel.send("Cette commande n'est nécessaire que pour les soirées auxquelles on invite des membres")
		else :
			await author.dm_channel.send("L'identifiant de soirée que tu as renseigné est invalide.")
	else :
		await author.dm_channel.send("Tu dois préciser l'identifiant de la soirée pour laquelle je dois envoyer les invitations")

@bot.command(name="vip")
@bot.dm_command
@bot.colocataire_command
async def vip_gamebot(ctx, *args, **kwargs):

	author = bot.guild.get_member(ctx.author.id)

	if len(args) > 1 :

		event_id = str(args[0])
		pseudo = str(args[1])

		if event_id in bot.events:

			if pseudo in bot.members :

				if bot.events[event_id]["type_invités"] == "roles" :

					if len(bot.events[event_id]["rôles invités"]) == 0 :

						if bot.events[event_id]["nb_max_joueurs"] != "infinity":
							if len(bot.events[event_id]["membres présents"]) >= int(bot.events[event_id]["nb_max_joueurs"]):
								await author.dm_channel.send("La soirée est déjà complète")
								return

						# on inscrit le VIP
						bot.events[event_id]["membres présents"].append(pseudo)
						bot.events[event_id]["vips"].append(pseudo)
						bot.write_json(bot.events, bot.events_file)

					else :
						await author.dm_channel.send("Il faut inscrire les VIPs avant d'inviter un rôle à la soirée")

				else :
					await author.dm_channel.send("On ne peut mettre des VIPs que dans les soirées pour lesquelles on invite des rôles")

			else :
				await author.dm_channel.send(f"Je ne connais pas le membre \"{pseudo}\"")

		else :
			await author.dm_channel.send(f"Aucune soirée ne possède l'identifiant \"{event_id}\"")

	else :
		await author.dm_channel.send("Utilisation: !vip [event_id] [pseudo]")