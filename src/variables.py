import re, sys

vars_json = "json/vars.json"
members_json = "json/members.json"
roles_json = "json/roles.json"
events_json = "json/events.json"
games_json = "json/games.json"
rankings_json = "json/rankings.json"

bot_guild_id = 1099428860514271282

roles_channel_id = 1179099714025689128
bienvenue_channel_id = 1179099642634444921
colocation_channel_id = 1179775060064600164
general_annonces_channel_id = 1179810037116444802

soirees_jeux_cat_id = 1179145721572765706

role_to_channel = {
	"ésisarien(ne)": 1179805849531719775,
	"soirées jeux": 1179805962987647037,
	"novice": 1179807649815068762
}

# /!\ Si CRLF en début ou fin de message, le bot ne les enverra pas dans le message
#     et renverra donc le message à chaque redémarrage (donc ne pas faire !)
roles_msg = """Salut jeune joueur,
Ici, tu peux décider d'avoir ou non certains rôles du serveur. Réagis à ce message avec l'émoji correspondant au rôle que tu souhaites avoir :
- si tu souhaites avoir le rôle {soirées_jeux} pour être informé(e) des soirées jeux organisées à Grenoble, réagis avec :game_die:
- si tu es un joueur peu expérimenté et que tu souhaites découvrir les jeux de société lors de soirées d'initiation ou simplement que tu aimes les jeux d'ambiance, tu peux réagir avec :baby: pour obtenir le rôle {novice}
- si tu habites à Grenoble ou dans les alentours, tu peux avoir le rôle {grenoble} en réagissant avec :mountain_snow:"""

welcome_msg = "7tadelliens, 7tadelliennes,\n\
{username} vient de nous rejoindre, faites lui un accueil des plus chaleureux !\n\
Bienvenue parmi nous, {username} !"

dm_welcome_msg = "Salut !\n\
\n\
Moi c'est **GameBot**,\n\
Je suis le bot s'occupant du serveur 7tadelles (un des meilleurs serveurs discord du monde à mon humble avis).\n\
\n\
Laisse-moi te présenter rapidement ce serveur :\n\
7tadelles est un serveur discord conçu par le merveilleux M1k3y (je suis très objectif hein). Il a pour but \
de réunir des personnes ayant un goût plus ou moins prononcé pour les jeux de société afin qu'elles puissent \
jouer ensemble aussi fréquement qu'elles le souhaitent. Tous les types et niveaux de joueurs sont les \
bienvenus dans ce serveur et y trouveront (j'espère) ce qu'ils cherchent. Que tu sois novice ou \
expérimenté, joueur occasionnel ou régulier, tu es aussi le bienvenu dans ce serveur.\n\
\n\
Juste avant de terminer, voici les règles à respecter au sein du serveur.\
En cliquand sur \"OK\", tu t'engages à les respecter.\n\
\n\
Règles :\n\
- être gentil\n\
- ne pas être méchant\n\
\n\
Je te souhaite la bienvevue à 7tadelles et espère que tu y fera de belles rencontres.\n\u200B"

member_invitation_msg = "Salut !\n\
\n\
Tu as été invité(e) à une soirée jeux à Grenoble !\n\
Voici quelques informations sur la soirée :\n\
Nom de la soirée : {name}\n\
Description : {description}\n\
Date : {date}\n\
Heure : {heure}\n\
Membres présents : {présents}\n\
Membres invités : {invités}\n\
\n\
Tu peux accepter ou refuser cette invitation en réagissant avec l'émoji approprié \
(attention, une fois ta réponse envoyée, tu devras contacter un @colocataire si tu \
veux la modifier, donc réfléchis bien avant de répondre, tu as tout ton temps)."

member_invitation_msg_start = "Salut !\n\
\n\
Tu as été invité(e) à une soirée jeux à Grenoble !\n\
Voici quelques informations sur la soirée :\n"

role_invitation_msg = "Salut {role} !\n\
\n\
Une nouvelle soirée jeux arrive et tu y as été invité !\n\
\n\
Voici quelques informations sur la soirée :\n\
Nom : {name}\n\
Description : {description}\n\
Date : {date}\n\
Heure : {heure}\n\
\n\
Réagis avec :+1: si tu souhaites participer !\n\
\n\
NB: retirer cette réaction te désinscrira de la soirée donc fais attention à ne pas retirer ta réaction par inadvertance car s'il y a des personnes dans la liste d'attente, la place que tu libères leur sera donnée"

role_invitation_msg_end = "Réagis avec :+1: si tu souhaites participer !\n\
\n\
NB: retirer cette réaction te désinscrira de la soirée donc fais attention à ne pas retirer ta réaction par inadvertance car s'il y a des personnes dans la liste d'attente, la place que tu libères leur sera donnée"

event_creation_questions = {
	"name": {
		"text": "Quel nom veux-tu donner à cette soirée ?",
		"valid_answers": r".*"
	},
	"date": {
		"text": "Quelle est la date de la soirée ? (format: jj-mm-aaaa)",
		"valid_answers": r"^((0[1-9]|[1-2][0-9]|3[0-1])-(0[1-9]|1[0-2])-20(2[4-9]|[3-9][0-9]))$"
	},
	"heure": {
		"text": "À quelle heure débutera cette soirée ? (format : XXhXX)",
		"valid_answers": r"^(([0-1][0-9]|2[0-3])h([0-5][0-9]))$"
	},
	"description": {
		"text": "Donne-moi une courte description pour cette soirée",
		"valid_answers": r".*"
	},
	"nb_max_joueurs": {
		"text": "Combien de joueurs seront présents au maximum ? (donne moi un nonmbre ou \"infinity\" si tu ne veux pas mettre de nombre maximum de joueur)",
		"valid_answers": r"^([1-9][0-9]*|infinity)$"
	},
	"type_invités": {
		"text": "Veux-tu inviter des rôles du serveur ou inviter des membres un par un ? Dis-moi \"roles\" ou \"membres\" (on ne peut pas faire un mix des deux malheureusement)",
		"valid_answers": r"^(roles|membres)$"
	}
}

alphabet = "0123456789AaàâBbCcçDdEeéèêëFfGgHhIiîïJjKkLlMmNnOoôPpQqRrSsTtUuùûüVvWwXxYyZz ?,.;/:§!%$£*&~\"#'}{)(][-|`_\\@=°+"
alphabet_list = [c for c in alphabet]
print(alphabet_list)
print("|".join(alphabet_list))
print(re.compile(r"^(" + '|'.join(alphabet_list) + ")*$"))
sys.exit()
games_categories = ["ambiance", "amateur", "initié", "expert"]
keywords = [
	"deck building",
	"worker placement",
	"draft",
	"cartes",
	"dés",
	"plis",
	"asymétrie",
	"rôles cachés"
]
game_creation_questions = {
	"name": {
		"text": "Quel est le nom du jeu à ajouter ?",
		"valid_answers": re.compile(r"^("+"|".join(alphabet_list)+")*$")
	},
	"description": {
		"text": "Donne moi une courte description du jeu",
		"valid_answers": r".*"
	},
	"players_min": {
		"text": "À partir de combien de joueurs peut-on jouer à ce jeu ?",
		"valid_answers": r"[1-9][0-9]*"
	},
	"players_max": {
		"text": "Jusqu'à combien de joueurs peut-on jouer à ce jeu ?",
		"valid_answers": r"[1-9][0-9]*"
	},
	"category": {
		"text": "Quelle est la catégorie du jeu ? {" + "|".join(games_categories) + "}",
		"valid_answers": re.compile(r"^(" + "|".join(games_categories) + ")$")
	},
	"duration": {
		"text": "Combien de temps dure une partie ? (format : \"Xmin - Xmin\" ou \"XhXX - XhXX\")",
		"valid_answers": r"^((([1-9][0-9]*min) - ([1-9][0-9]*min))|((([1-9][0-9]*)h([0-5][0-9])) - (([1-9][0-9]*)h([0-5][0-9]))))$"
	},
	"keywords": {
		"text": "Tu peux me donner des mots-clé correspondant à ce jeu. Envois-moi \"None\" si tu ne veux pas en renseigner ou une liste de mots-clé séparés par des points virgules. Liste de mots-clé disponibles : \n[ "+' , '.join(keywords)+" ]",
		"valid_answers": re.compile(r"^(None|((" + "|".join(keywords) + ")(;(" + "|".join(keywords) + "))*))$")
	}
}
