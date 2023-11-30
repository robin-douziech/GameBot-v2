import os, sys, random
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

@bot.command(name="kill")
@bot.dm_command
@bot.colocataire_command
async def kill_gamebot(ctx, *args, **kwargs) :
	sys.exit()

bot.run(os.getenv("TOKEN"))