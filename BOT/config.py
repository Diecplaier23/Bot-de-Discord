import discord

TOKEN = ''

GUILD_ID = 1105177286375899207
GUILD = discord.Object(id=GUILD_ID)

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True
