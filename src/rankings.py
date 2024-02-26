from games import *

@bot.command(name="play")
@bot.dm_command
@bot.colocataire_command
@bot.read_dollar_vars
async def play_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if len(args) > 2 :
		game_list = []
		for category in games_categories :
			game_list += list(bot.games[category].keys())
		if not(str(args[0]) in game_list) :
			await author.dm_channel.send(f"Le jeu {args[0]} n'est pas présent dans ma base de données")
			return
		for i,player in enumerate(args[1:]) :
			if not(str(player) in bot.members) :
				await author.dm_channel.send(f"Le pseudo {player} n'appartient à aucun joueur du serveur")
				return
			other_players = list(args[1:])
			other_players.pop(i)
			if str(player) in other_players :
				await author.dm_channel.send(f"J'ai détecté un doublon dans la liste des joueurs")
				return
		if not(str(args[0]) in bot.rankings["parties"]) :
			bot.rankings["parties"][str(args[0])] = {}
		for player in args[1:] :
			if not(str(player) in bot.rankings["parties"][str(args[0])]) :
				bot.rankings["parties"][str(args[0])][str(player)] = []
			bot.rankings["parties"][str(args[0])][str(player)].append([args.index(str(player)),len(args)-1])
		bot.write_json(bot.rankings, bot.rankings_file)
		await author.dm_channel.send("Partie enregistrée avec succès !")

	else :
		await author.dm_channel.send("Utilisation : !play jeu joueur1 joueur2 ...")

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

	# remplir les scores
	if len(args) > 0 :
		results = bot.find_games_by_name(str(args[0]))
		if len(results) > 1 :
			await author.dm_channel.send(f"Plusieurs jeux contiennent \"{args[1]}\" dans leur titre")
		elif len(results) == 1 :
			if str(args[0] in parties):
				for player in parties[str(args[0])] :
					players[player] = 0
					for partie in parties[str(args[0])][player] :
						players[player] += int(partie[1])+1-int(partie[0])
			elif all_time:
				await author.dm_channel.send(f"Aucune partie du jeu {args[0]} n'a jamais été enregistrée")
			else:
				await author.dm_channel.send(f"Aucune partie du jeu {args[0]} n'a été enregistrée ce mois-ci")
		else :
			await author.dm_channel.send(f"Aucun jeu ne contient \"{args[1]}\" dans son titre")
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
