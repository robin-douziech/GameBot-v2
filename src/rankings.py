from games import *

@bot.command(name="play")
@bot.dm_command
@bot.colocataire_command
@bot.read_dollar_vars
async def play_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if len(args) > 2 :

		game_name = str(args[0])
		results = bot.find_games_by_name(game_name)

		if len(results) > 1 :
			await author.dm_channel.send(f"Plusieurs jeux contiennent \"{game_name}\" dans leur titre")
			return

		elif len(results) == 1 :

			game = results[list(results.keys())[0]]

			# on cherche les pseudo inconnus et les pseudos en double
			for i,player in enumerate(args[1:]) :
				if not(str(player) in bot.members) :
					await author.dm_channel.send(f"Le pseudo {player} n'appartient à aucun joueur du serveur")
					return
				other_players = list(args[1:])
				other_players.pop(i)
				if str(player) in other_players :
					await author.dm_channel.send(f"J'ai détecté un doublon dans la liste des joueurs")
					return

			if not(game["name"] in bot.rankings["parties"]) :
				bot.rankings["parties"][game["name"]] = {}

			for player in args[1:] :

				if not(str(player) in bot.rankings["parties"][game["name"]]) :
					bot.rankings["parties"][game["name"]][str(player)] = []

				bot.rankings["parties"][game["name"]][str(player)].append([args.index(str(player)),len(args)-1])
				bot.write_json(bot.rankings, bot.rankings_file)
				await author.dm_channel.send("Partie enregistrée avec succès !")

		else :
			await author.dm_channel.send(f"Aucun jeu ne contient \"{game_name}\" dans son titre")
			return

	else :
		await author.dm_channel.send("Utilisation : !play [jeu] [joueur1] [joueur2] ...")

@bot.command(name="ranking")
@bot.dm_command
async def ranking_gamebot(ctx, *args, **kwargs) :
	
	author = bot.guild.get_member(ctx.author.id)
	parties = copy.deepcopy(bot.rankings["parties"])
	players = {}
	all_time = False

	# déterminer l'ensemble des parties (tout ou juste ce mois-ci)
	if len(args) > 0 and args[0] == "-alltime":
		all_time = True
		for game in bot.rankings["old_parties"] :
			if not(game in parties) :
				parties[game] = {}
			for player in bot.rankings["old_parties"][game] :
				if not(player in parties[game]) :
					parties[game][player] = []
				parties[game][player] += bot.rankings["old_parties"][game][player]
		args = list(args)
		args.pop(0)

	### Remplir les scores des jeux concernés

	# si un jeu est précisé on ne fait le classement que pour ce jeu
	if len(args) > 0 :
		game_name = str(args[0])
		results = bot.find_games_by_name(game_name)
		if len(results) > 1 :
			await author.dm_channel.send(f"Plusieurs jeux contiennent \"{game_name}\" dans leur titre")
			return
		elif len(results) == 1 :
			game = results[list(results.keys())[0]]
			if game["name"] in parties:
				for player in parties[game["name"]] :
					players[player] = 0
					for partie in parties[game["name"]][player] :
						players[player] += int(partie[1])+1-int(partie[0])
			elif all_time:
				await author.dm_channel.send(f"Aucune partie du jeu {game['name']} n'a jamais été enregistrée")
				return
			else:
				await author.dm_channel.send(f"Aucune partie du jeu {game['name']} n'a été enregistrée ce mois-ci")
				return
		else :
			await author.dm_channel.send(f"Aucun jeu ne contient \"{game_name}\" dans son titre")
			return

	# sinon on fait le classement tous jeux confondus
	else :
		for game in parties :
			for player in parties[game] :
				if not(player in players) :
					players[player] = 0
				for partie in parties[game][player] :
					players[player] += int(partie[1])+1-int(partie[0])

	# trier
	players_tuples = [(player, players[player]) for player in players]
	ranking = sorted(players_tuples, key=lambda x: x[1])[::-1]

	if all_time :
		if len(args) > 0 :
			msg = f"Voici le classement du jeu {args[0]} prenant en compte toutes les parties jouées depuis le début :\n"
		else :
			msg = f"Voici le classement tous jeux confondus, prenant en compte toutes les parties jouées depuis le début :\n"
	else :
		if len(args) > 0 :
			msg = f"Voici le classement de ce mois-ci pour le jeu {args[0]} :\n"
		else :
			msg = f"Voici le classement de ce mois-ci, tous jeux confondus :\n"

	for i,player in enumerate(ranking) :
		if i == 0 :
			msg += f":first_place: : {player[0]} ({player[1]} point{'s' if player[1]>1 else ''})\n"
		elif i == 1 :
			msg += f":second_place: : {player[0]} ({player[1]} point{'s' if player[1]>1 else ''})\n"
		elif i == 2 :
			msg += f":third_place: : {player[0]} ({player[1]} point{'s' if player[1]>1 else ''})\n"
		else :
			msg += f"{i+1} : {player[0]} ({player[1]} point{'s' if player[1]>1 else ''})\n"

	msg_list = bot.divide_message(msg)
	for msg in msg_list :
		await author.dm_channel.send(msg)
