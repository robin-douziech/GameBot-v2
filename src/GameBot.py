from discord.ext import commands
import discord, json, logging, re

from variables import *

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename="gamebot.log"
)

class GameBot(commands.Bot):

	def __init__(self, vars_file, members_file, roles_file, events_file, *args, **kwargs):
		super(GameBot, self).__init__(command_prefix="!", intents=discord.Intents.all(), *args, **kwargs)

		self.guild = None
		self.channels = {}

		self.vars_file = vars_file
		self.vars = {}

		self.members_file = members_file
		self.members = {}

		self.roles_file = roles_file
		self.roles = {}
		self.roles_msg = None

		self.events_file = events_file
		self.events = {}

	def dm_command(self, function) :
		async def wrapper(ctx, *args, **kwargs) :
			author = self.guild.get_member(ctx.author.id)
			dm_channel = author.dm_channel
			if dm_channel == None :
				dm_channel = await author.create_dm()
			if ctx.channel == dm_channel :
				await function(ctx, *args, **kwargs)
			else :
				await dm_channel.send("Pour me demander ça, c'est ici que ça se passe")
		return wrapper

	def colocataire_command(self, function) :
		async def wrapper(ctx, *args, **kwargs) :
			author = self.guild.get_member(ctx.author.id)
			role = await self.get_role("colocataire")
			if author.get_role(role.id) != None :
				await function(ctx, *args, **kwargs)
			else :
				await author.dm_channel.send("Vous n'avez pas la permission d'utiliser cette commande")
		return wrapper

	def read_dollar_vars(self, function) :
		async def wrapper(ctx, *args, **kwargs) :
			new_args = []
			for i in range(len(args)) :
				if args[i].startswith('$') :
					try :
						new_args.append(self.vars["tmp_vars"][str(args[i][1:])])
					except Exception as e:
						new_args.append(args[i])
				else :
					new_args.append(args[i])
			new_args = tuple(new_args)
			await function(ctx, *new_args, **kwargs)
		return wrapper

	def log(self, message) :
		logging.info(message)

	def write_json(self, var, file) :
		json_object = json.dumps(var, indent=2)
		with open(file, "wt") as f :
			f.write(json_object)

	def fetch_member(self, pseudo) :
		for member in self.guild.members :
			if pseudo == f"{member.name}#{member.discriminator}" :
				return member
		return None

	async def fetch_roles_ids(self) :
		res = {}
		roles = await self.guild.fetch_roles()
		for role in roles :
			res[role.name] = role.id
		return res

	async def get_role(self, role_name) :
		try :
			return self.guild.get_role(self.roles["roles_ids"][role_name])
		except :
			role = await self.guild.create_role(name=role_name)
			self.roles["roles_ids"][role_name] = role.id
			self.write_json(self.roles, self.roles_file)
			return role

	async def send_or_retreive_roles_msg(self) :
		soirées_jeux = await self.get_role("soirées jeux")
		grenoble = await self.get_role("grenoble")
		novice = await self.get_role("novice")
		try :
			self.roles_msg = await self.channels["roles"].fetch_message(self.roles["roles_msgid"])
			if self.roles_msg.content != roles_msg.format(soirées_jeux=soirées_jeux.mention, grenoble=grenoble.mention, novice=novice.mention) :
				await self.send_roles_msg(soirées_jeux, grenoble, novice)
		except: 
			await self.send_roles_msg(soirées_jeux, grenoble, novice)

	async def send_roles_msg(self, soirées_jeux, grenoble, novice) :
		await self.channels["roles"].purge()
		self.roles_msg = await self.channels["roles"].send(roles_msg.format(soirées_jeux=soirées_jeux.mention, grenoble=grenoble.mention, novice=novice.mention))
		for role_name in self.roles["roles_dic"] :
			await self.roles_msg.add_reaction(self.roles["roles_dic"][role_name]["reaction_name"])
		self.roles["roles_msgid"] = self.roles_msg.id
		self.write_json(self.roles, self.roles_file)

	async def send_welcome_message_in_dm(self, member) :

		# ajouter le membre au json
		self.members[f"{member.name}#{member.discriminator}"] = {
			"name": member.name,
			"id":   member.discriminator
		}
		self.write_json(self.members, self.members_file)

		# envoyer le message en dm
		dm_channel = member.dm_channel
		if dm_channel == None :
			dm_channel = await member.create_dm()
		message = await dm_channel.send(dm_welcome_msg)
		await message.add_reaction(chr(0x1F197))

	async def send_welcome_message_in_channel(self, member) :
		role = await self.get_role("7tadellien(ne)")
		await member.add_roles(role)
		await self.channels["bienvenue"].send(welcome_msg.format(username=member.mention))

	def delete_invitation_messageid_for_event_member(self, event_id) :
		for member in self.members :
			msgid_to_remove = []
			for msg_id in self.members[member]["msgid_to_eventid"] :
				if self.members[member]["msgid_to_eventid"][msg_id] == str(event_id) :
					msgid_to_remove.append(msg_id)
			for msg_id in msgid_to_remove :
				self.members[member]["msgid_to_eventid"].pop(msg_id)
		self.write_json(self.members, self.members_file)

	def delete_invitation_messageid_for_event_role(self, event_id) :
		msgid_to_remove = []
		for msg_id in self.vars["msgid_to_eventid"] :
			if self.vars["msgid_to_eventid"][msg_id] == str(event_id) :
				msgid_to_remove.append(msg_id)
		for msg_id in msgid_to_remove :
			self.vars["msgid_to_eventid"].pop(msg_id)
		self.write_json(self.vars, self.vars_file)

	async def delete_unfinished_events(self) :
		events_to_delete = []
		for event_id in self.events :
			if not(self.events[event_id]["creation_finished"]) :
				events_to_delete.append(event_id)
				await self.guild.get_channel(self.events[event_id]["channel_id"]).delete()
				await self.guild.get_role(self.events[event_id]["role_id"]).delete()
				self.roles["roles_ids"].pop(str(event_id))
				self.delete_invitation_messageid_for_event_member(event_id)
				self.delete_invitation_messageid_for_event_role(event_id)
		for event_id in events_to_delete :
			self.events.pop(event_id)
		self.write_json(self.events, self.events_file)
		self.write_json(self.roles, self.roles_file)

	async def delete_event(self, event_id) :
		await self.guild.get_channel(self.events[str(event_id)]["channel_id"]).delete()
		await self.guild.get_role(self.events[str(event_id)]["role_id"]).delete()
		self.roles["roles_ids"].pop(str(event_id))
		self.delete_invitation_messageid_for_event_member(event_id)
		self.delete_invitation_messageid_for_event_role(event_id)
		self.events.pop(event_id)
		self.write_json(self.events, self.events_file)
		self.write_json(self.roles, self.roles_file)
		self.write_json(self.vars, self.vars_file)

	async def send_invitation_to_member(self, event_id, member) :
		dm_channel = member.dm_channel
		if dm_channel == None :
			dm_channel = await member.create_dm()
		message = await dm_channel.send(member_invitation_msg.format(
			name=self.events[str(event_id)]["name"],
			description=self.events[str(event_id)]["description"],
			date = self.events[str(event_id)]["date"],
			heure = self.events[str(event_id)]["heure"]
		))
		await message.add_reaction(chr(0x2705))
		await message.add_reaction(chr(0x274C))
		self.members[f"{member.name}#{member.discriminator}"]["msgid_to_eventid"][str(message.id)] = str(event_id)
		self.write_json(self.members, self.members_file)
		await self.channels["colocation"].send(f"Invitation à la soirée \"{self.events[str(event_id)]['name']}\" envoyée à {member.name}")

	async def update_invitations_members(self, event_id) :
		nb_invited_members = len(self.events[str(event_id)]["membres présents"])+len(self.events[str(event_id)]["membres en attente"])
		if self.events[str(event_id)]["nb_max_joueurs"] == "infinity" :
			for member in self.events[str(event_id)]["liste d'attente"] :
				Member = self.fetch_member(member)
				await self.send_invitation_to_member(event_id, Member)
				self.events[str(event_id)]["membres en attente"].append(member)
			self.events[str(event_id)]["liste d'attente"] = []
			self.write_json(self.events, self.events_file)
		else :
			for i in range(min([int(self.events[str(event_id)]["nb_max_joueurs"]) - nb_invited_members, len(self.events[str(event_id)]["liste d'attente"])])) :
				Member = self.fetch_member(self.events[str(event_id)]["liste d'attente"][0])
				await self.send_invitation_to_member(event_id, Member)
				self.events[str(event_id)]["membres en attente"].append(self.events[str(event_id)]["liste d'attente"][0])
				self.events[str(event_id)]["liste d'attente"].pop(0)
			self.write_json(self.events, self.events_file)

	async def update_invitations_roles(self, event_id) :
		nb_present_people = len(self.events[str(event_id)]["membres présents"])
		role = self.guild.get_role(self.events[str(event_id)]["role_id"])
		if self.events[str(event_id)]["nb_max_joueurs"] == "infinity" :
			for member in self.events[str(event_id)]["liste d'attente"] :
				Member = self.fetch_member(member)
				self.events[str(event_id)]["membres présents"].append(member)
				await Member.add_roles(role)
				await Member.dm_channel.send(f"Tu as été ajouté aux personnes présentes à la soirée \"{self.events[str(event_id)]['name']}\".")
				await self.channels["colocation"].send(f"{Member.name} as été ajouté aux personnes présentes à la soirée \"{self.events[str(event_id)]['name']}\".")
			self.events[str(event_id)]["liste d'attente"] = []
			self.write_json(self.events, self.events_file)
		else :
			for i in range(min([int(self.events[str(event_id)]["nb_max_joueurs"]) - nb_present_people, len(self.events[str(event_id)]["liste d'attente"])])) :
				Member = self.fetch_member(self.events[str(event_id)]["liste d'attente"][0])
				self.events[str(event_id)]["membres présents"].append(self.events[str(event_id)]["liste d'attente"][0])
				self.events[str(event_id)]["liste d'attente"].pop(0)
				await Member.add_roles(role)
				await Member.dm_channel.send(f"Tu as été ajouté aux personnes présentes à la soirée \"{self.events[str(event_id)]['name']}\".")
				await self.channels["colocation"].send(f"{Member.name} as été ajouté aux personnes présentes à la soirée \"{self.events[str(event_id)]['name']}\".")
			self.write_json(self.events, self.events_file)

	async def remove_guest_from_event_members(self, event_id, member) :
		try :
			self.events[str(event_id)]["membres présents"].remove(f"{member.name}#{member.discriminator}")
			self.write_json(self.events, self.events_file)
			role = await self.get_role(str(event_id))
			await member.remove_roles(role)
			await member.dm_channel.send(f"Tu as été retiré(e) des participants à la soirée \"{self.events[str(event_id)]['name']}\".")
			await self.channels["colocation"].send(f"{member.name} as été retiré(e) des participants à la soirée \"{self.events[str(event_id)]['name']}\".")
			if self.events[str(event_id)]["type_invités"] == "membres" :
				await self.update_invitations_members(event_id)
		except Exception as e :
			raise Exception(str(e))

	async def invite_role_to_event(self, event_id, role) :
		if role.name in role_to_channel :
			message = await self.channels[role.name].send(role_invitation_msg.format(
				role=role.mention,
				name=self.events[str(event_id)]["name"],
				description=self.events[str(event_id)]["description"],
				date=self.events[str(event_id)]["date"],
				heure=self.events[str(event_id)]["heure"]
			))
			await message.add_reaction(chr(0x1F44D))
			self.events[str(event_id)]["rôles invités"].append(role.name)
			self.vars["msgid_to_eventid"][str(message.id)] = str(event_id)
			self.write_json(self.vars, self.vars_file)
			self.write_json(self.events, self.events_file)
		else :
			raise Exception("Invalid role")

	def divide_message(self, message) :
		lines = message.split("\n")
		msg_list = []
		while len(lines) > 0 :
			current_msg = ""
			while len(lines) > 0 and len(current_msg+lines[0]) < 2000 :
				current_msg += f"{lines[0]}\n"
				lines.pop(0)
			msg_list.append(current_msg)
		return msg_list

	async def send_next_question(self, member) :
		if len(self.members[f"{member.name}#{member.discriminator}"]["questions"]) > 0 :
			self.members[f"{member.name}#{member.discriminator}"]["questions"].pop(0)
			if len(self.members[f"{member.name}#{member.discriminator}"]["questions"]) > 0 :
				question = self.members[f"{member.name}#{member.discriminator}"]["questions"][0]
				await member.dm_channel.send(event_creation_questions[question]["text"])
		self.write_json(self.members, self.members_file)

	def answer_is_valid(self, author, answer) :
		question = self.members[f"{author.name}#{author.discriminator}"]["questions"][0]
		valid_anwers = event_creation_questions[question]["valid_answers"]
		if re.match(valid_anwers, answer) :
			return True
		return False

	async def process_msg(self, message) :

		role_colocataire = await self.get_role("colocataire")
		author = self.guild.get_member(message.author.id)

		if author.get_role(role_colocataire.id) != None :

			if self.members[f"{author.name}#{author.discriminator}"]["questionned_event_creation"] :
				if self.answer_is_valid(author, message.content) :
					event_id = self.members[f"{author.name}#{author.discriminator}"]["event_being_created"]
					question = self.members[f"{author.name}#{author.discriminator}"]["questions"][0]
					self.events[str(event_id)][question] = message.content
					self.write_json(self.events, self.events_file)
					await self.send_next_question(author)

					if len(self.members[f"{author.name}#{author.discriminator}"]["questions"]) == 0 :
						event_id = self.members[f"{author.name}#{author.discriminator}"]["event_being_created"]
						channel_tmp = self.guild.get_channel(self.events[str(event_id)]["channel_id"])
						await channel_tmp.edit(name=self.events[str(event_id)]["name"])
						msg = f"Bienvenue dans ce salon temporaire !\n\n"
						msg += f"Ce salon est un salon temporaire associé à une soirée jeux à laquelle tu participes, voici quelques informations sur la soirée :\n"
						msg += f"Nom de la soirée : {self.events[str(event_id)]['name']}\n"
						msg += f"Description : {self.events[str(event_id)]['description']}\n"
						msg += f"Date : {self.events[str(event_id)]['date']}\n"
						await channel_tmp.send(msg)
						self.events[str(event_id)]["creation_finished"] = True
						self.members[f"{author.name}#{author.discriminator}"]["event_being_created"] = 0
						self.members[f"{author.name}#{author.discriminator}"]["questionned_event_creation"] = False
						self.write_json(self.members, self.members_file)
						self.write_json(self.events, self.events_file)
						await author.dm_channel.send("La soirée a bien été créée")


