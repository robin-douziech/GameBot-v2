from events import *

@bot.command(name="game")
@bot.dm_command
async def game_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)
	role_colocataire = bot.guild.get_role(bot.roles["roles_ids"]["colocataire"])

	if len(args) > 0 :

		if args[0] == "create" :

			if author.get_role(role_colocataire.id) != None :
				if bot.members[f"{author.name}#{author.discriminator}"]["questions"] == [] :
					id_number = 1
					while str(id_number) in bot.games :
						id_number += 1
					bot.games[str(id_number)] = {
						"name": "",
						"description": "",
						"players_min": "",
						"players_max": "",
						"category": "",
						"duration": "",
						"keywords": "",
						"rules": "",
						"videos": "",

						"creation_finished": False
					}
					bot.write_json(bot.games, bot.games_file)
					bot.members[f"{author.name}#{author.discriminator}"]["game_being_created"] = id_number
					bot.members[f"{author.name}#{author.discriminator}"]["questions"] = ["", *list(game_creation_questions.keys())]
					bot.members[f"{author.name}#{author.discriminator}"]["questionned_game_creation"] = True
					bot.write_json(bot.members, bot.members_file)

					await bot.send_next_question(author, game_creation_questions)

				else :
					await author.dm_channel.send("Finis de répondre à mes questions avant de créer un nouveau jeu")
			else :
				await author.dm_channel.send("Seuls les @colocataires peuvent ajouter des jeux à ma liste")

		elif args[0] == "delete" :

			if author.get_role(role_colocataire.id) != None :
				if len(args) > 1 :
					if bot.delete_game(str(args[1])) :
						await author.dm_channel.send("Jeu supprimé avec succès !")
					else :
						await author.dm_channel.send("Je ne connais pas ce jeu")
				else :
					await author.dm_channel.send("Tu dois préciser le nom du jeu à supprimer")
			else :
				await author.dm_channel.send("Seuls les @colocataires peuvent supprimer des jeux de ma liste")

		elif args[0] == "grade" :

			if len(args) > 1 :
				results = bot.find_games_by_name(str(args[1]))
				if len(results) > 1 :
					await author.dm_channel.send(f"Plusieurs jeux contiennent \"{args[1]}\" dans leur titre")
				elif len(results) == 1:
					game = results[list(results.keys())[0]]
					if len(args) > 2 :
						if re.match(r"^([0-9]|10)$", args[2]):
							if not "grades" in bot.games[game["category"]][game["name"]] :
								bot.games[game["category"]][game["name"]]["grades"] = {}
							bot.games[game["category"]][game["name"]]["grades"][f"{author.name}#{author.discriminator}"] = int(args[2])
							bot.write_json(bot.games, bot.games_file)
							await author.dm_channel.send("Note enregistrée avec succès")
						else :
							await author.dm_channel.send(f"\"{args[2]}\" n'est pas une note valide")
					else :
						await author.dm_channel.send("Tu dois préciser la note que tu souhaite donner au jeu (entre 0 et 10 inclus)")
				else :
					await author.dm_channel.send(f"Aucun jeu ne contient \"{args[1]}\" dans son titre")
			else :
				await author.dm_channel.send("Tu dois préciser le nom du jeu à noter")

		elif args[0] == "-cat" : # recherche de jeux par catégorie (retourne liste des jeux de la catégorie renseignée)
			if len(args) > 1: 
				if args[1] in games_categories :
					if len(bot.games[str(args[1])]) > 0 :
						game_dic = bot.sort_games(bot.games[str(args[1])])
						msg = f"Voici les jeux de la catégorie {args[1]} :\n"
						for game in game_dic :
							msg += f"- {game}\n"
						msg_list = bot.divide_message(msg)
						for msg in msg_list :
							await author.dm_channel.send(msg)
					else :
						await author.dm_channel.send(f"Aucun jeu n'est enregistré dans la catégorie {args[1]} pour le moment.")
				else :
					await author.dm_channel.send(f"La catégorie {args[1]} n'existe pas")
			else :
				await author.dm_channel.send("Utilisation : !game -cat [category_name]")

		elif args[0] == "-kw" : # recherche de jeux par mots-clé (retourne tous les jeux possédant tous les mots-clés renseignés)
			if len(args) > 1 :
				games_dic = bot.find_games_by_keywords(args[1:])
				if len(games_dic) == 0 :
					msg = f"Aucun jeu ne possède le{'s' if len(args)>2 else ''} mot{'s' if len(args)>2 else ''}-clé " + ", ".join(args[1:-1]) + f" {'et ' if len(args)>2 else ''}{args[-1]}.\n"
					msg += f"Pense à vérifier l'orthographe des mots-clé renseignés. Voici la liste des mots-clé existant :\n{' - '.join(keywords)}\n"
				else :
					if len(games_dic) == 1 :
						msg = f"Voici le seul jeu possédant le{'s' if len(args)>2 else ''} mot{'s' if len(args)>2 else ''}-clé " + ", ".join(args[1:-1]) + f" {'et ' if len(args)>2 else ''}{args[-1]} :\n"
					else :
						msg = f"Voici tous les jeux possédant le{'s' if len(args)>2 else ''} mot{'s' if len(args)>2 else ''}-clé " + ", ".join(args[1:-1]) + f" {'et ' if len(args)>2 else ''}{args[-1]} :\n"
					for game in games_dic :
						msg += f"- {game}\n"
				msg_list = bot.divide_message(msg)
				for msg in msg_list :
					await author.dm_channel.send(msg)
			else :
				await author.dm_channel.send("Utilisation : !game -kw keyword [keyword]*")

		else : # recherche de jeux par le début du nom (si plusieurs jeux matchent : liste des noms / si un seul jeu match : toutes les infos)
			games_dic = bot.find_games_by_name(str(args[0]))
			if len(games_dic) == 0 :
				msg = f"Je n'ai trouvé aucun jeu dont le nom contient \"{args[0]}\". Vérifie l'orthographe du nom du jeu que tu cherches et fais bien attention à mettre des guillemets si le nom contient des espaces.\n"
			else :
				if len(games_dic) == 1 :
					game = games_dic[list(games_dic.keys())[0]]
					msg = f"J'ai trouvé le jeu que tu cherche ! Voici quelques informations sur ce jeu :\n"
					msg += f"__Nom du jeu__ : {game['name']}\n"
					if "grades" in bot.games[game["category"]][game["name"]] :
						grade = 0
						for member in bot.games[game["category"]][game["name"]]["grades"] :
							grade += int(bot.games[game["category"]][game["name"]]["grades"][member])
						grade /= len(bot.games[game["category"]][game["name"]]["grades"])
						grade = round(grade, 2)
						msg += f"__Note__ : {grade}/10\n"
					msg += f"__Description__ :\n{game['description']}\n"
					msg += f"__Nombre de joueurs__ : {game['players_min']} - {game['players_max']}\n"
					msg += f"__Durée d'une partie__ : {game['duration']}\n"
					msg += f"__Catégorie__ : {game['category']}\n"
					if game['keywords'] != "None" :
						msg += f"__Mots-clés__ : {' - '.join(game['keywords'].split(';'))}\n"
					msg += f"__Règles du jeu__ : {game['rules']}\n"
					if "videos" in game and len(game["videos"]) != 0 :
						msg += f"__Vidéos à propos du jeu__ :\n{game['videos']}\n"
				else :
					msg = f"J'ai trouvé plusieurs jeux dont le nom contient \"{args[0]}\" :\n"
					for game in games_dic :
						msg += f"- {game}\n"
			msg_list = bot.divide_message(msg)
			for msg in msg_list :
				await author.dm_channel.send(msg)

	else :
		msg = f"Voici la liste complète des jeux présents dans ma base de données :\n\n"
		for category in games_categories :
			games_dic = bot.sort_games(bot.games[category])
			msg += f"**Catégorie {category} :**\n"
			for game in games_dic :
				msg += f"- {game}\n"
			msg += "\n"
		msg_list = bot.divide_message(msg)
		for msg in msg_list :
			await author.dm_channel.send(msg)

@bot.command(name="video")
@bot.dm_command
@bot.colocataire_command
async def video_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if len(args) > 0 :
		games = bot.find_games_by_name(args[0])
		if len(games) == 0 :
			await author.dm_channel.send(f"Je n'ai trouvé aucun jeu dont le nom contient \"{args[0]}\"")
			return
		elif len(games) == 1 :
			game = games[list(games.keys())[0]]
			category = game["category"]
			if len(args) > 1 :
				if args[1].startswith("https://") :
					if not("videos" in bot.games[category][game['name']]) :
						bot.games[category][game['name']]["videos"] = ""
					bot.games[category][game['name']]["videos"] += f"{args[1]}\n"
					bot.write_json(bot.games, bot.games_file)
					await author.dm_channel.send("La vidéo a été ajoutée avec succès !")
				elif args[1] == "clear" :
					bot.games[category][game['name']]["videos"] = ""
					bot.write_json(bot.games, bot.games_file)
					await author.dm_channel.send("Les vidéos ont été supprimées avec succès !")
				else :
					await author.dm_channel.send(f"\"{args[1]}\" n'est pas un lien.")
			else :
				await author.dm_channel.send("Vous devez spécifier l'URL d'une vidéo à ajouter")
		else :
			await author.dm_channel.send(f"Plusieurs jeux contiennent \"{args[0]}\" dans leur nom ({' - '.join(list(games.keys()))}).")
	else :
		await author.dm_channel.send("Vous devez préciser un jeu")