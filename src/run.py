import sys
from dotenv import load_dotenv
from commands import *

load_dotenv()

@bot.command(name="dé")
@bot.dm_command
@bot.read_dollar_vars
async def dé_gamebot(ctx, n=None, *args, **kwargs) :
	if n == None :
		await ctx.author.dm_channel.send("Tu dois préciser le nombre du faces que possède le dé que tu veux lancer :\nUtilisation : !dé [n]")
	else :
		try: 
			N = int(n)
			if N < 1 :
				raise ValueError("Nombre de faces incorrect")
			await ctx.author.dm_channel.send(str(random.randint(1,int(n))))
		except:
			await ctx.author.dm_channel.send("L'argument que tu as renseigné est incorrect")

@bot.command(name="set")
@bot.dm_command
@bot.colocataire_command
async def set_gamebot(ctx, varname=None, value=None, *args, **kwargs) :

	if varname != None and value != None :
		if not("tmp_vars" in bot.vars) :
			bot.vars["tmp_vars"] = {}
		bot.vars["tmp_vars"][varname] = value
		bot.write_json(bot.vars, bot.vars_file)
		await ctx.author.dm_channel.send("Variable enregistrée !")
	else :
		await ctx.author.dm_channel.send("Utilisation : !set [varname] [value]")

@bot.command(name="vars")
@bot.dm_command
@bot.colocataire_command
async def vars_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if len(args) > 0 and args[0] == "clean" :
		bot.vars["tmp_vars"] = {}
		bot.write_json(bot.vars, bot.vars_file)
		await author.send("C'est bon ! J'ai rangé ma chambre.")

	else :
		msg = "Voici les variables actuellement enregistrées :\n"
		for variable in bot.vars["tmp_vars"] :
			msg += f"{variable} : {bot.vars['tmp_vars'][variable]}\n"
		msg_list = bot.divide_message(msg)
		for msg in msg_list :
			await author.dm_channel.send(msg)

@bot.command(name="teams")
@bot.dm_command
@bot.colocataire_command
@bot.read_dollar_vars
async def teams_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if len(args) > 0 :
		try :
			list_teams_card = [int(x) for x in args[0].split(';')]
			nb_players = sum(list_teams_card)
			if len(args) > nb_players :

				# on  vérifie qu'on connais tous les pseudo et qu'il n'y a pas de doublon
				for i,player in enumerate(args[1:]) :
					if not(str(player) in bot.members) :
						await author.dm_channel.send(f"Le pseudo {player} n'appartient à aucun joueur du serveur")
						return
					other_players = list(args[1:])
					other_players.pop(i)
					if str(player) in other_players :
						await author.dm_channel.send(f"J'ai détecté un doublon dans la liste des joueurs")
						return

				players = list(args[1:])
				teams = []
				for card in list_teams_card :
					teams.append([])
					for i in range(card) :
						player = random.choice(players)
						teams[-1].append(player)
						players.remove(player)

				msg = f"Voici les équipes que j'ai constituées :\n"
				for i,team in enumerate(teams) :
					msg += f"Équipe {i+1} : {' / '.join(team)}\n"

				msg_list = bot.divide_message(msg)
				for msg in msg_list :
					await author.dm_channel.send(msg)

			else :
				await author.dm_channel.send("Tu n'as pas donné assez de joueurs pour faire les équipes")

		except :
			await author.dm_channel.send("Utilisation : !teams [repartition] [joueur1] [joueur2] ...")

	else :
		await author.dm_channel.send("Utilisation : !teams [repartition] [joueur1] [joueur2] ...")

@bot.command(name="kw")
@bot.dm_command
@bot.colocataire_command
async def kw_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if len(args) > 1 :
		game_list = []
		for category in games_categories :
			game_list += list(bot.games[category].keys())
			if str(args[0]) in bot.games[category] :
				game_cat = category
		if not(str(args[0]) in game_list) :
			await author.dm_channel.send(f"Le jeu {args[0]} n'est pas présent dans ma base de données")
			return
		if not(str(args[1]) in keywords) :
			await author.dm_channel.send(f"Je ne connais pas le mot-clé {args[1]}.")
			return
		if bot.games[game_cat][str(args[0])]["keywords"] == "None" :
			bot.games[game_cat][str(args[0])]["keywords"]
			bot.write_json(bot.games, bot.games_file)
		else :
			bot.games[game_cat][str(args[0])]["keywords"] += f";{args[1]}"
			bot.write_json(bot.games, bot.games_file)

		await author.dm_channel.send(f"Le mot-clé {args[1]} a été ajouté au jeu {args[0]}.")

	else :
		await author.dm_channel.send("Utilisation : !kw [jeu] [mot-clé]")

@bot.command(name="rankreset")
@bot.dm_command
@bot.colocataire_command
async def rankreset_gamebot(ctx, *args, **kwargs) :
	author = bot.guild.get_member(ctx.author.id)
	bot.archive_rankings()
	await author.dm_channel.send("C'est bon ! J'ai archivé les classements")

@bot.command(name="rankdelete")
@bot.dm_command
@bot.colocataire_command
async def rankdelete_gamebot(ctx, *args, **kwargs) :
	author = bot.guild.get_member(ctx.author.id)
	bot.rankings = {
		"parties": {},
		"old_parties": {}
	}
	bot.write_json(bot.rankings, bot.rankings_file)
	await author.dm_channel.send("C'est bon ! J'ai supprimé les classements.")

@bot.command(name="json")
@bot.dm_command
@bot.colocataire_command
async def json_gamebot(ctx, *args, **kwargs) :
	author = bot.guild.get_member(ctx.author.id)
	if len(args) > 0 :
		try :
			with open(f"json/{args[0]}.json", "rt") as f :
				json_msg = json.load(f)
			await author.dm_channel.send(f"```json\n{msg}\n```")
		except :
		pass
	else :
		await author.dm_channel.send("Tu dois préciser le fichier json à lire")	

@bot.command(name="clean")
@bot.dm_command
@bot.colocataire_command
async def clean_gamebot(ctx, *args, **kwargs) :
	for channel_name in ["bienvenue", "général-annonces", "colocation"] :
		await bot.channels[channel_name].purge()
	bot.polls = {}
	bot.write_json(bot.polls, bot.polls_file)

@bot.command(name="kill")
@bot.dm_command
@bot.colocataire_command
async def kill_gamebot(ctx, *args, **kwargs) :
	sys.exit()

bot.run(os.getenv("TOKEN"))