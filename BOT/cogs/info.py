import discord
from discord import app_commands
import json
import config
import os

@app_commands.command(name="info", description="Información del rol de One Piece")
async def info(interaction: discord.Interaction):
    """Envía los enlaces útiles del rol desde el JSON en un embed"""
    await interaction.response.defer(ephemeral=True)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    ruta_json = os.path.join(base_path, "..", "db", "enlaces.json")

    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        await interaction.followup.send(
            "No se encontró el archivo de enlaces.", ephemeral=True
        )
        return
    except json.JSONDecodeError:
        await interaction.followup.send(
            "El archivo de enlaces está corrupto o mal formateado.", ephemeral=True
        )
        return

    enlaces = data.get("enlaces", [])
    if not enlaces:
        await interaction.followup.send("No hay enlaces disponibles.", ephemeral=True)
        return

    # Construir mensaje simple con estilo
    mensaje = "# Estas son las páginas útiles del rol:\n\n"

    for enlace in enlaces:
        nombre = enlace.get("nombre", "Sin nombre")
        url = enlace.get("url", "#")
        mensaje += f"- **{nombre}:**  [➤  Link Aqui](<{url}>)\n"

    mensaje += "## Si algún enlace no te funciona, avisa a <@481163717862621194> o a <@993505982825119775>."

    await interaction.followup.send(
        content=mensaje,
        ephemeral=True
    )

def setup(tree: app_commands.CommandTree):
    """Registra el comando /info en el árbol del bot"""
    tree.add_command(info, guild=config.GUILD)