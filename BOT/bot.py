import discord
from discord import app_commands
import config
import sys
import os

# Agregar la carpeta raíz a sys.path para que imports funcionen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar setups de los cogs
from cogs.info import setup as info_setup
from cogs.rol import setup as rol_setup
from cogs.mision import setup as mision_setup
from cogs.nuevoeliminar import setup as nuevoeliminar_setup


def setup_ping(tree: app_commands.CommandTree):
    """Comando /ping para verificar la latencia del bot"""
    @tree.command(
        name="ping",
        description="Muestra la latencia del bot",
        guild=config.GUILD
    )
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Pong! {round(interaction.client.latency * 1000)} ms"
        )


def setup_actividad(tree: app_commands.CommandTree):
    """Comando /actividad para cambiar la actividad del bot con tipo"""
    @tree.command(
        name="actividad",
        description="Cambia la actividad del bot",
        guild=config.GUILD
    )
    @app_commands.describe(
        tipo="Tipo de actividad",
        texto="Texto de la actividad"
    )
    @app_commands.choices(tipo=[
        app_commands.Choice(name="Jugando", value="playing"),
        app_commands.Choice(name="Streaming", value="streaming"),
        app_commands.Choice(name="Escuchando", value="listening"),
        app_commands.Choice(name="Viendo", value="watching")
    ])
    async def actividad(interaction: discord.Interaction, tipo: app_commands.Choice[str], texto: str):
        if tipo.value == "playing":
            actividad_obj = discord.Game(name=texto)
        elif tipo.value == "streaming":
            actividad_obj = discord.Streaming(name=texto, url="https://twitch.tv/tu_canal")
        elif tipo.value == "listening":
            actividad_obj = discord.Activity(type=discord.ActivityType.listening, name=texto)
        elif tipo.value == "watching":
            actividad_obj = discord.Activity(type=discord.ActivityType.watching, name=texto)
        else:
            await interaction.response.send_message("Tipo de actividad inválido.", ephemeral=True)
            return

        await interaction.client.change_presence(activity=actividad_obj)
        await interaction.response.send_message(f"Actividad cambiada a: {tipo.name} {texto}", ephemeral=True)


class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=config.INTENTS)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Borrar comandos antiguos del servidor para pruebas
        self.tree.clear_commands(guild=config.GUILD)

        # Registrar comandos antes de sincronizar
        setup_ping(self.tree)
        setup_actividad(self.tree)
        info_setup(self.tree)
        rol_setup(self.tree)
        mision_setup(self.tree)
        nuevoeliminar_setup(self.tree)

        # Sincronizar solo en el servidor
        await self.tree.sync(guild=config.GUILD)

        # Mostrar comandos registrados
        cmds = self.tree.get_commands(guild=config.GUILD)
        print(
            f"Comandos registrados ({len(cmds)}): "
            + ", ".join(cmd.name for cmd in cmds)
        )


# Crear instancia del bot
bot = Bot()


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

    # Actividad inicial
    await bot.change_presence(
        activity=discord.Game(name="⌛Esperando nueva partida⏳")
    )


# Ejecutar el bot
bot.run(config.TOKEN)