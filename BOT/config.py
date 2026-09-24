import discord

TOKEN = 'MTQ1MzQwNjQ4NTkxMTQ0MTUwNA.GdS-mw.AnstaA0Dmeg3PYtQzfXydwh0dgIDW6QpeLjuOY'

GUILD_ID = 1105177286375899207
GUILD = discord.Object(id=GUILD_ID)

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True
