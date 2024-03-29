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

		game_name = str(args[0])
		keyword = str(args[1])
		results = bot.find_games_by_name(game_name)

		if len(results) > 1 :
			await author.dm_channel.send(f"Plusieurs jeux contiennent \"{game_name}\" dans leur titre")
			return
			
		elif len(results) == 1 :
			game = results[list(results.keys())[0]]
			if not(keyword in keywords):
				await author.dm_channel.send(f"Je ne connais pas le mot-clé {keyword}.")
				return
			if bot.games[game['category']][game['name']]["keywords"] == "None" :
				bot.games[game['category']][game['name']]["keywords"] = keyword
				bot.write_json(bot.games, bot.games_file)
			else :
				bot.games[game['category']][game['name']]["keywords"] += f";{keyword}"
				bot.write_json(bot.games, bot.games_file)

			await author.dm_channel.send(f"Le mot-clé {keyword} a été ajouté au jeu {game['name']}.")

		else :
			await author.dm_channel.send(f"Aucun jeu ne contient \"{game_name}\" dans son titre")
			return

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
		if str(args[0]) in ["events", "members", "news", "polls", "rankings", "roles", "vars"] :
			try :
				with open(f"json/{args[0]}.json", "rt") as f :
					json_msg = f.read()
				msg_list = bot.divide_message(json_msg, wrappers=('```json\n', '\n```'))
				for msg in msg_list :
					await author.dm_channel.send(msg)
			except :
				pass
	else :
		await author.dm_channel.send("Tu dois préciser le fichier json à lire")

@bot.command(name="logs")
@bot.dm_command
@bot.colocataire_command
async def logs_gamebot(ctx, nb_lines=10, *args, **kwargs) :
	author = bot.guild.get_member(ctx.author.id)

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

	try :
		with open(f"logs/20{year}/{month}/{day}.log", "rt") as f :
			msg = f.read().split('\n')
			if len(msg) > int(nb_lines) :
				msg = msg[-int(nb_lines):]
			txt = ""
			for line in msg :
				txt += f"{line}\n"
		msg_list = bot.divide_message(txt, wrappers=('```', '```'))
		for msg in msg_list :
			await author.dm_channel.send(msg)
	except :
		pass

@bot.command(name="test")
@bot.dm_command
@bot.colocataire_command
async def test_gamebot(ctx) :
	author = bot.guild.get_member(ctx.author.id)
	msg = ""
	for event_id in bot.events :
		msg += f"soirée n°{event_id} : {'PASSÉ' if bot.event_is_over(event_id) else 'FUTUR'}\n"
	await author.dm_channel.send(msg)

@bot.command(name="kill")
@bot.dm_command
@bot.colocataire_command
async def kill_gamebot(ctx, *args, **kwargs) :
	sys.exit()

@bot.command(name="var")
@bot.dm_command
@bot.colocataire_command
async def var_gamebot(ctx, *args, **kwargs):
	author = bot.guild.get_member(ctx.author.id)
	if len(args) > 0 :
		try :
			var = getattr(bot, args[0])
			msg = str(var)
			msg_list = bot.divide_message(msg)
			for msg in msg_list:
				await author.dm_channel.send(msg)
		except Exception as e :
			await author.dm_channel.send(f"Exception: {e}")
	else:
		await author.dm_channel.send("Utilisation: !var [varname]")


bot.run(os.getenv("TOKEN"))