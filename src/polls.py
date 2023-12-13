from rankings import *

@bot.command(name="poll")
@bot.dm_command
@bot.colocataire_command
async def poll_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if len(args) > 0 :

		if str(args[0]) == "create" :

			if bot.members[f"{author.name}#{author.discriminator}"]["questions"] == [] :
				id_number = 1
				while str(id_number) in bot.polls :
					id_number += 1
				bot.polls[str(id_number)] = {
					"text_poll": "",
					"soirée?": "",
					"end_date": "",
					"confirmation": "",

					"channel_id": 0,
					"reactions": [],
					"results": {},
					"msg_id": 0,
					"dm_msg_id": 0,
					"creation_finished": False
				}
				bot.write_json(bot.polls, bot.polls_file)
				bot.members[f"{author.name}#{author.discriminator}"]["poll_being_created"] = id_number
				bot.members[f"{author.name}#{author.discriminator}"]["questions"] = ["", *list(poll_creation_questions.keys())]
				bot.members[f"{author.name}#{author.discriminator}"]["questionned_poll_creation"] = True
				bot.write_json(bot.members, bot.members_file)

				await bot.send_next_question(author, poll_creation_questions)

			else :
				await author.dm_channel.send("Finis de répondre à mes questions avant.")

		elif str(args[0]) == "read" :
			if len(args) > 1 :
				if str(args[1]) in bot.polls :
					poll_id = str(args[1])
					msg = f"Voici les résultats du sondage :"
					x = [len(bot.polls[poll_id]['results'][option]) for option in bot.polls[poll_id]["reactions"]]
					plt.hist(x)
					plt.savefig('fig.png')
					discord.File('fig.png')
					await bot.channels["colocation"].send(msg, file=file)

				else :
					await author.dm_channel.send("Aucun sondage ne porte cet identifiant")

			else :
				await author.dm_channel.send(f"Voici les identifiants des sondages en cours : "+';'.join(list(bot.polls.keys())))

		elif str(args[0]) == "delete" :
			if len(args) > 1 :
				if str(args[1]) in bot.polls :
					bot.polls.pop(str(args[1]))
					bot.write_json(bot.polls, bot.polls_file)
					await author.dm_channel.send("Sondage supprimé avec succès !")

				else :
					await author.dm_channel.send("Aucun sondage ne porte cet identifiant")

			else :
				await author.dm_channel.send("Tu dois préciser l'identifiant du sondage à supprimer")

		else :
			await author.dm_channel.send("Utilisation : !poll {create|read|delete}")			

	else :
		await author.dm_channel.send("Utilisation : !poll {create|read|delete}")