import discord
from discord import app_commands
import config
from utils.roles import obtener_rango, ORDEN_ROLES
import json
from pathlib import Path
import os

# ---------- RUTAS ----------
# Carpeta donde está este archivo (cogs)
base_path = Path(__file__).resolve().parent

# Subir una carpeta (..), entrar en db
DB_DIR = base_path.parent / "db"
DB_DIR.mkdir(exist_ok=True)

# Ruta al JSON
TRIPULACION_PATH = DB_DIR / "tripulacion.json"

# ---------- FUNCIONES ----------
def cargar_tripulacion():
    """Carga la base de datos de la tripulación desde el JSON"""
    if not TRIPULACION_PATH.exists():
        return {}
    with open(TRIPULACION_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_tripulacion(tripulacion):
    """Guarda el diccionario de tripulación en un JSON"""
    with open(TRIPULACION_PATH, "w", encoding="utf-8") as f:
        json.dump(tripulacion, f, indent=4, ensure_ascii=False)

tripulacion = cargar_tripulacion()

# ---------- COMANDOS ----------
@app_commands.command(
    name="miembros",
    description="Muestra la tripulación"
)
async def miembros(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message(
            "No se pudo obtener el servidor.", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    if not tripulacion:
        await interaction.followup.send(
            "No se encontró la base de datos de la tripulación.", ephemeral=True
        )
        return

    lista = []
    for uid, personaje in tripulacion.items():
        try:
            member = guild.get_member(int(uid)) or await guild.fetch_member(int(uid))
            rango = obtener_rango(member)
            pos = ORDEN_ROLES.index(rango) if rango in ORDEN_ROLES else len(ORDEN_ROLES)
            lista.append((pos, member.mention, personaje, rango))
        except Exception:
            lista.append((len(ORDEN_ROLES), f"<@{uid}>", personaje, "No encontrado"))

    lista.sort(key=lambda x: x[0])
    mensaje = "**Tripulación:**\n\n" + "\n".join(
        f"{m} - {p} - {r}" for _, m, p, r in lista
    )

    await interaction.followup.send(mensaje, ephemeral=True)


@app_commands.command(
    name="rangos",
    description="Lista de rangos"
)
async def rangos(interaction: discord.Interaction):
    mensaje = "**Rangos:**\n\n" + "\n".join(ORDEN_ROLES)
    await interaction.response.send_message(mensaje, ephemeral=True)


# ---------- SETUP ----------
def setup(tree: app_commands.CommandTree):
    """Registra los comandos en el árbol del bot"""
    tree.add_command(miembros, guild=config.GUILD)
    tree.add_command(rangos, guild=config.GUILD)