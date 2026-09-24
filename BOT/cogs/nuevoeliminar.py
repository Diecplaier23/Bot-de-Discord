import discord
from discord import app_commands
from discord.ui import View, Button
import config
from data.tripulacion import tripulacion, guardar_tripulacion
from utils.roles import obtener_rango, ORDEN_ROLES
import json
from pathlib import Path
import os

# =========================
# RUTAS DB
# =========================

# Carpeta donde está este archivo
base_path = Path(__file__).resolve().parent

# Subir una carpeta (..), entrar en db
DB_DIR = base_path.parent / "db"
DB_DIR.mkdir(exist_ok=True)

# Rutas a los JSON
ENLACES_PATH = DB_DIR / "enlaces.json"
MISIONES_PATH = DB_DIR / "misiones.json"

# =========================
# Funciones de guardado
# =========================

def guardar_enlaces(enlace_nuevo):
    """Guarda un nuevo enlace en enlaces.json"""
    try:
        with open(ENLACES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"enlaces": []}

    data["enlaces"].append(enlace_nuevo)

    with open(ENLACES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def guardar_mision(mision_nueva):
    """Guarda una nueva misión en misiones.json"""
    try:
        with open(MISIONES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"misiones": []}

    data["misiones"].append(mision_nueva)

    with open(MISIONES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# =========================
# Grupo principal /nuevo
# =========================

nuevo = app_commands.Group(
    name="nuevo",
    description="Agrega un miembro, enlace o misión"
)

# =========================
# Subcomando /nuevo miembro
# =========================

@nuevo.command(
    name="miembro",
    description="Agrega un miembro"
)
@app_commands.default_permissions(administrator=True)
@app_commands.describe(usuario="Usuario", personaje="Personaje")
async def nuevo_miembro(interaction: discord.Interaction, usuario: discord.Member, personaje: str):
    if usuario.id in tripulacion:
        await interaction.response.send_message("❌ Ya existe", ephemeral=True)
        return

    tripulacion[usuario.id] = personaje
    guardar_tripulacion()
    await interaction.response.send_message(
        f"✅ {usuario.mention} añadido como {personaje}", ephemeral=True
    )

# =========================
# Subcomando /nuevo enlace
# =========================

@nuevo.command(
    name="enlace",
    description="Agrega un enlace"
)
@app_commands.default_permissions(administrator=True)
@app_commands.describe(nombre="Nombre del enlace", url="URL del enlace")
async def nuevo_enlace(interaction: discord.Interaction, nombre: str, url: str):
    enlace_nuevo = {"nombre": nombre, "url": url}
    guardar_enlaces(enlace_nuevo)
    await interaction.response.send_message(
        f"✅ Enlace '{nombre}' añadido correctamente", ephemeral=True
    )

# =========================
# Subcomando /nuevo misión
# =========================

@nuevo.command(
    name="mision",
    description="Agrega una misión"
)
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    nombre="Nombre de la misión",
    isla="Isla donde ocurre la misión",
    descripcion="Descripción de la misión",
    dificultad="Dificultad de 0 a 10",
    recompensa="Recompensa en dinero"
)
async def nuevo_mision(
    interaction: discord.Interaction,
    nombre: str,
    isla: str,
    descripcion: str,
    dificultad: int,
    recompensa: int
):
    if dificultad < 0 or dificultad > 10:
        await interaction.response.send_message(
            "❌ La dificultad debe estar entre 0 y 10.", ephemeral=True
        )
        return

    mision_nueva = {
        "nombre": nombre,
        "isla": isla,
        "descripcion": descripcion,
        "dificultad": dificultad,
        "recompensa": recompensa,
        "jugadores": []
    }

    guardar_mision(mision_nueva)
    await interaction.response.send_message(
        f"✅ Misión '{nombre}' añadida correctamente", ephemeral=True
    )

# =========================
# Funciones lógicas de eliminación
# =========================

def eliminar_enlace_logica(nombre):
    try:
        with open(ENLACES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return False

    original_len = len(data["enlaces"])
    data["enlaces"] = [
        e for e in data["enlaces"]
        if e["nombre"].lower() != nombre.lower()
    ]

    with open(ENLACES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return len(data["enlaces"]) < original_len


def eliminar_mision_logica(nombre):
    try:
        with open(MISIONES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return None

    mision_eliminada = None
    nuevas_misiones = []

    for m in data["misiones"]:
        if m["nombre"].lower() == nombre.lower():
            mision_eliminada = m
        else:
            nuevas_misiones.append(m)

    if mision_eliminada is None:
        return None

    data["misiones"] = nuevas_misiones
    with open(MISIONES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return mision_eliminada


def eliminar_miembro_logica(usuario_id):
    if usuario_id in tripulacion:
        del tripulacion[usuario_id]
        guardar_tripulacion()
        return True
    return False

# =========================
# Grupo principal /eliminar
# =========================

eliminar = app_commands.Group(
    name="eliminar",
    description="Elimina un miembro, enlace o misión"
)

# =========================
# Subcomando /eliminar miembro
# =========================

@eliminar.command(
    name="miembro",
    description="Elimina un miembro de la tripulación"
)
@app_commands.default_permissions(administrator=True)
@app_commands.describe(usuario="Usuario a eliminar")
async def eliminar_miembro_cmd(interaction: discord.Interaction, usuario: discord.Member):
    if eliminar_miembro_logica(usuario.id):
        await interaction.response.send_message(
            f"✅ {usuario.mention} eliminado de la tripulación", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ No existe en la tripulación", ephemeral=True
        )

# =========================
# Subcomando /eliminar enlace
# =========================

@eliminar.command(
    name="enlace",
    description="Elimina un enlace"
)
@app_commands.default_permissions(administrator=True)
@app_commands.describe(nombre="Nombre del enlace a eliminar")
async def eliminar_enlace_cmd(interaction: discord.Interaction, nombre: str):
    if eliminar_enlace_logica(nombre):
        await interaction.response.send_message(
            f"✅ Enlace '{nombre}' eliminado correctamente", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ Enlace no encontrado", ephemeral=True
        )

# =========================
# Subcomando /eliminar misión
# =========================

@eliminar.command(
    name="mision",
    description="Elimina una misión (ver jugadores antes de eliminar)"
)
@app_commands.default_permissions(administrator=True)
async def eliminar_mision_cmd(interaction: discord.Interaction):
    try:
        with open(MISIONES_PATH, "r", encoding="utf-8") as f:
            misiones = json.load(f)["misiones"]
    except FileNotFoundError:
        await interaction.response.send_message(
            "❌ No hay misiones registradas.", ephemeral=True
        )
        return

    if not misiones:
        await interaction.response.send_message(
            "❌ No hay misiones registradas.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Misiones disponibles para eliminar",
        description="Selecciona la misión que deseas eliminar",
        color=discord.Color.red()
    )

    view = View()

    for index, m in enumerate(misiones, start=1):
        jugadores = ", ".join(f"<@{uid}>" for uid in m.get("jugadores", [])) or "Ninguno"

        embed.add_field(
            name=f"{index}. {m['nombre']}",
            value=(
                f"🌴 Isla: {m['isla']}\n"
                f"📝 {m['descripcion']}\n"
                f"👥 Jugadores: {jugadores}\n"
                f"💰 Recompensa: ${m['recompensa']}"
            ),
            inline=False
        )

        button = Button(label=str(index), style=discord.ButtonStyle.danger)

        async def callback(interaction_btn, nombre_mision=m["nombre"]):
            eliminar_mision_logica(nombre_mision)
            await interaction_btn.response.send_message(
                f"✅ Misión '{nombre_mision}' eliminada", ephemeral=True
            )

        button.callback = callback
        view.add_item(button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# =========================
# SETUP
# =========================

def setup(tree: app_commands.CommandTree):
    tree.add_command(eliminar, guild=config.GUILD)
    tree.add_command(nuevo, guild=config.GUILD)