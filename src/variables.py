import re

vars_json = "json/vars.json"
members_json = "json/members.json"
roles_json = "json/roles.json"
events_json = "json/events.json"
games_json = "json/games.json"
rankings_json = "json/rankings.json"
polls_json = "json/polls.json"
news_json = "json/news.json"

bot_guild_id = 1099428860514271282

roles_channel_id = 1179099714025689128
bienvenue_channel_id = 1179099642634444921
colocation_channel_id = 1179775060064600164
general_annonces_channel_id = 1179810037116444802

soirees_jeux_cat_id = 1179145721572765706
colocation_cat_id = 1179145861926748221

bot_owner_id = 394185214479302656

role_to_channel = {
	"ésisarien(ne)": 1179805849531719775,
	"soirées jeux": 1179805962987647037,
	"testeur": 1218976328447955004
}

# /!\ Si CRLF en début ou fin de message, le bot ne les enverra pas dans le message
#     et renverra donc le message à chaque redémarrage (donc ne pas faire !)
roles_msg = """Salut {tadelles},
Ici, tu peux décider d'avoir ou non certains rôles du serveur. Réagis à ce message avec l'émoji correspondant au rôle que tu souhaites avoir :
- si tu souhaites avoir le rôle {soirées_jeux} pour être informé(e) des soirées jeux organisées à Grenoble, réagis avec :game_die:
- si tu habites à Grenoble ou dans les alentours, tu peux avoir le rôle {grenoble} en réagissant avec :mountain_snow:"""

welcome_msg = "7tadelliens, 7tadelliennes,\n\
Un nouveau membre vient d'arriver, faites lui un accueil digne de ce nom !\n\
Bienvenue parmi nous, {username} !"

dm_welcome_msg = "Salut !\n\
\n\
Moi c'est **GameBot**,\n\
Je suis le bot s'occupant du serveur 7tadelles (un des meilleurs serveurs discord du monde à mon humble avis).\n\
\n\
Laisse-moi te présenter rapidement ce serveur :\n\
7tadelles est un serveur discord conçu par le talentueux M1k3y (je suis très objectif hein). Il a pour but \
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
souhaites la modifier, donc réfléchis bien avant de répondre, tu as tout ton temps)."

member_invitation_msg_start = "Salut !\n\
\n\
Tu as été invité(e) à une soirée jeux à Grenoble !\n\
Voici quelques informations sur la soirée :\n"

role_invitation_msg = "Salut {role},\n\
\n\
Une nouvelle soirée jeux arrive ! Si tu souhaites y participer, réagis avec :+1:\n\
{nb_max_joueurs}\n\
Voici quelques informations sur la soirée :\n\
Nom : {name}\n\
Description : {description}\n\
Date : {date}\n\
Heure : {heure}\n\
\n\
J'espère vous y voir nombreux :slight_smile:"

role_invitation_msg_end = "J'espère vous y voir nombreux :slight_smile:"

vip_msg = "Tu as été inscrit(e) à la soirée {soiree} par un colocataire. \
Tu n'as rien besoin de faire pour t'inscrire à cette soirée, une place toute chaude a été réservée spécialement pour toi. \
Si tu souhaites te désinscrire de cette soirée, préviens un des colocataires."

event_creation_questions = {
	"name": {
		"text": "Quel nom veux-tu donner à cette soirée ?",
		"valid_answers": r".*"
	},
	"datetime": {
		"text": "Quelles sont la date et l'heure de la soirée ? (format: jj/mm/aaaa hh:mm)",
		"valid_answers": r"^((0[1-9]|[1-2][0-9]|3[0-1])/(0[1-9]|1[0-2])/20(2[4-9]|[3-9][0-9]) ([0-1][0-9]|2[0-3]):([0-5][0-9]))$"
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

alphabet = "0123456789AaàâBbCcçDdEeéèêëFfGgHhIiîïJjKkLlMmNnOoôPpQqRrSsTtUuùûüVvWwXxYyZz ?,.;/:§!%$£*&~\"#'}{()][-|`_\\@=°+"
alphabet_list = [re.escape(c) for c in alphabet]
games_categories = ["ambiance", "amateur", "initié", "expert"]
keywords = [
	"asymétrie",
	"bluff",
	"cartes",
	"coop",
	"deck building",
	"dés",
	"draft",
	"placement d'ouvriers",
	"plis",
	"prise de risque",
	"rôles cachés",
	"roll and write",
	"semi-coop",
	"stop ou encore",
	"tuiles",
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
		"text": "Combien de temps dure une partie ? (format : \"< X\" ou \"X - X\" avec X au format \"Xmin\" ou \"Xh[XX]\")",
		"valid_answers": r"^((< (([1-9][0-9]*min)|(([1-9][0-9]*)h(([0-5][0-9]){0,1}))))|((([1-9][0-9]*min)|(([1-9][0-9]*)h(([0-5][0-9]){0,1}))) - (([1-9][0-9]*min)|(([1-9][0-9]*)h(([0-5][0-9]){0,1})))))$"
	},
	"keywords": {
		"text": "Tu peux me donner des mots-clé correspondant à ce jeu. Envois-moi \"None\" si tu ne veux pas en renseigner ou une liste de mots-clé séparés par des points virgules. Liste de mots-clé disponibles : \n[ "+' , '.join(keywords)+" ]",
		"valid_answers": re.compile(r"^(None|((" + "|".join(keywords) + ")(;(" + "|".join(keywords) + "))*))$")
	},
	"rules": {
		"text": "Donne-moi un lien vers les règles du jeu.",
		"valid_answers": r".*"
	}
}

poll_creation_questions = {
	"text_poll": {
		"text": "Envoie-moi le texte du sondage que tu veux créer, puis réagis à ton message avec les réactions à utiliser pour le sondage",
		"valid_answers": r".*"
	},
	"soirée?": {
		"text": "Ce sondage est-il lié à une soirée ? (si c'est le cas, j'enverrai le sondage dans le channel de cette soirée, sinon, je l'enverrai dans annonces-bot). Envoie-moi \"oui:<id_soirée>\" ou \"non\"",
		"valid_answers": r"^(non|oui:[1-9][0-9]*)$"
	},
	"end_date": {
		"text": "Donne moi la date de fin du sondage (je pourrai annoncer les résultats à cette date). Ajoute \"N\" à la fin du message pour que je n'annonce pas les résultats. Format: jj/mm/aa hh:mm [N]",
		"valid_answers": r"^((0[1-9]|[1-2][0-9]|3[0-1])/(0[1-9]|1[0-2])/(2[3-9]|[3-9][0-9]) ([0-1][0-9]|2[0-3]):([0-5][0-9])( N){0,1})$"
	},
	"confirmation": {
		"text": "__**Après avoir ajouté les réactions à ton message**__, confirme-moi que tu veux vraiment envoyer ce sondage et que tu n'as pas fait d'erreur (oui/non)",
		"valid_answers": r"^(oui|non)$"
	}
	
}

news_creation_questions = {
	"news": {
		"text": "Écris l'annonce que tu souhaites que je fasse",
		"valid_answers": r".*"
	},
	"confirmation": {
		"text": "Confirme-moi que tu veux vraiment faire cette annonce et que tu n'as pas fait d'erreur (oui/non)",
		"valid_answers": r"^(oui|non)$"
	}
}