from games import *

@bot.command(name="help")
@bot.dm_command
async def help_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)
	role_colocataire = bot.guild.get_role(bot.roles["roles_ids"]["colocataire"])
	role_soirees_jeux = bot.guild.get_role(bot.roles["roles_ids"]["soirées jeux"])

	msg = f"Voici tout ce que je peux faire pour toi :\n\n"
	msg += f"(attention : toutes les commandes doivent m'être envoyées en message privé)\n\n"

	if author.get_role(role_colocataire.id) != None :

		msg += f"**Gestion des soirées jeux :**\n\n"
		msg += f"- !event create : créer une soirée jeux (je vais te poser les questions nécessaires, laisse-toi guider ;) )\n"
		msg += f"- !event read : obtenir la liste des soirées jeux existantes\n"
		msg += f"- !event read [event_id] : obtenir des informations sur une soirée jeux en particulier\n"
		msg += f"- !event delete [event_id] : supprimer une soirée jeux\n"
		msg += f"- !invite [event_id] [role] : inviter un role à une soirée jeux (le paramètre \"type_invités\" de la soiée jeux doit valoir \"roles\")\n"
		msg += f"- !invite [event_id] [pseudo] : inviter un membre à une soirée jeux (le paramètre \"type_invités\" de la soiée jeux doit valoir \"membres\")\n"
		msg += f"- !invite [event_id] [pseudo] delete : supprimer un membres des membres présents à une soirée\n"
		msg += f"\n"

	msg += f"**Jeux présents dans ma base de données :**\n\n"
	if author.get_role(role_colocataire.id) != None :
		msg += f"- !game create : ajouter un jeu à la base de données (je vais te poser les questions nécessaires, laisse-toi guider ;) )\n"
		msg += f"- !game delete [name] : supprimer un jeu de la base de données\n"
	msg += f"- !game -cat [category] : obtenir la liste des jeux d'une catégorie (les différenres catégories sont : "+", ".join(games_categories[:-1])+f" et {games_categories[-1]})\n"
	msg += f"- !game -kw [keyword(s)] : rechercher les jeux possédant certains mots-clé. Tu recevra la liste des jeux possédant tous les mots-clé renseignés.\n"
	msg += f"  Les différents mots-clé existant sont : {' - '.join(keywords)}\n"
	msg += f"- !game [name] : rechercher les jeux dont le nom commence par \"name\". Si plusieurs jeux sont trouvé, tu obtiendras la liste de leurs noms. Si un seul jeu correspond, tu obtiendras davantage d'informations sur ce jeu\n"
	msg += f"- !game : obtenir la liste complète des jeux présents dans ma base de données\n"

	msg += "\n"

	msg += f"**Commandes diverses :**\n\n"
	if author.get_role(role_colocataire.id) != None :
		msg += f"- !set [varname] [value] : enregistrer une variable pour le bot\n"
		msg += f"- !kill : éteindre le bot\n"
	msg += f"- !dé [n] : lancer un dé à n faces\n"

	msg_list = bot.divide_message(msg)
	for msg in msg_list :
		await author.dm_channel.send(msg)
