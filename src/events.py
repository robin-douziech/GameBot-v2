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
		id_number = 1
		while str(id_number) in bot.events :
			id_number += 1
		role_soirees_jeux = await bot.get_role("soirées jeux")
		role_colocataire = await bot.get_role("colocataire")
		category = discord.utils.get(bot.guild.categories, id=soirees_jeux_cat_id)
		#role_tmp = await bot.guild.create_role(name=str(id_number))
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
			"membres en attente": [], # les membres invité qui ont pas encore répondu
			"membres présents": [], # les membres invités qui ont répondu "oui"
			"rôles invités": [],

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

		await bot.send_next_question(author)

	elif crud == "read" :
		if event_id == None :
			msg = ""
			for event_id in bot.events :
				msg += f"{event_id} : {bot.events[event_id]['name']}\n"
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
		await author.dm_channel.send("pas encore implémenté")

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
				if bot.events[str(event_id)]["type_invités"] == "membres" :
					if str(arg) in bot.members :
						role_soirees_jeux = await bot.get_role("soirées jeux")
						Member = bot.fetch_member(str(arg))
						if Member.get_role(role_soirees_jeux.id) != None :
							bot.events[str(event_id)]["liste d'attente"].append(str(arg))
							bot.write_json(bot.events, bot.events_file)
							await bot.update_invitations_members(event_id)
						else :
							await author.dm_channel.send(f"{arg} ne possède pas le rôle \"soirées jeux\".")
					else :
						raise ValueError("Membre introuvable")
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
