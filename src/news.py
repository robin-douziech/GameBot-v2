from polls import *

@bot.command(name="news")
@bot.dm_command
@bot.colocataire_command
async def news_gamebot(ctx, *args, **kwargs) :

	author = bot.guild.get_member(ctx.author.id)

	if bot.members[f"{author.name}#{author.discriminator}"]["questions"] == [] :
		id_number = 1 :
		while str(id_number) in bot.news :
			id_number += 1
		bot.news[str(id_number)] = {
			"news": "",
			"confirmation": ""
		}
		bot.write_json(bot.news, bot.news_file)
		bot.members[f"{author.name}#{author.discriminator}"]["news_being_created"] = id_number
		bot.members[f"{author.name}#{author.discriminator}"]["questions"] = ["", *list(news_creation_questions.keys())]
		bot.members[f"{author.name}#{author.discriminator}"]["questionned_news_creation"] = True
		bot.write_json(bot.members, bot.members_file)

		await bot.send_next_question(author, news_creation_questions)

	else :
		await author.dm_channel.send("Finis de répondre à mes questions avant.")