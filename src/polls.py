from rankings import *

@bot.command(name="poll")
@bot.dm_command
@bot.colocataire_command
async def poll_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if bot.members[f"{author.name}#{author.discriminator}"]["questions"] == [] :
		id_number = 1
		while str(id_number) in bot.polls :
			id_number += 1
		bot.polls[str(id_number)] = {
			"text_poll": "",
			"end_date": "",
			"confirmation": "",

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