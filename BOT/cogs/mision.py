import discord
from discord import app_commands
import config
import json
from discord.ui import View, Button
import os  # si aún no lo tienes importado

# Ruta absoluta a la base de datos
base_path = os.path.dirname(os.path.abspath(__file__))
RUTA_MISIONES = os.path.join(base_path, "..", "db", "misiones.json")

# --- Grupo principal /mision ---
mision = app_commands.Group(name="mision", description="Gestiona misiones")

# --- Funciones para leer y guardar misiones ---
def leer_misiones():
    try:
        with open(RUTA_MISIONES, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Asegurar que cada misión tenga lista de jugadores
            for m in data.get("misiones", []):
                m.setdefault("jugadores", [])
            return data.get("misiones", [])
    except FileNotFoundError:
        return []

def guardar_misiones(misiones):
    with open(RUTA_MISIONES, "w", encoding="utf-8") as f:
        json.dump({"misiones": misiones}, f, indent=4, ensure_ascii=False)

# --- Subcomando /mision info ---
@mision.command(name="info", description="Muestra información de tus misiones activas")
@app_commands.describe(nombre="Selecciona una misión (opcional)")
async def mision_info(interaction: discord.Interaction, nombre: str = None):
    misiones_lista = leer_misiones()
    user_id = str(interaction.user.id)
    user_misiones = [m["nombre"] for m in misiones_lista if user_id in m.get("jugadores", [])]

    if not user_misiones:
        await interaction.response.send_message("No tienes misiones activas.", ephemeral=True)
        return

    if nombre:
        if nombre not in user_misiones:
            await interaction.response.send_message(f"No tienes la misión '{nombre}' activa.", ephemeral=True)
            return
        descripcion = f"Misión seleccionada: {nombre}"
    else:
        descripcion = "\n".join(user_misiones)

    embed = discord.Embed(
        title="Tus misiones activas",
        description=descripcion,
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@mision_info.autocomplete("nombre")
async def mision_info_autocomplete(interaction: discord.Interaction, current: str):
    misiones_lista = leer_misiones()
    user_id = str(interaction.user.id)
    opciones = [m["nombre"] for m in misiones_lista if user_id in m.get("jugadores", [])]
    return [
        app_commands.Choice(name=m, value=m)
        for m in opciones if current.lower() in m.lower()
    ][:25]


# --- Subcomando /mision aceptar ---
@mision.command(name="aceptar", description="Acepta una misión")
@app_commands.describe(nombre="Nombre de la misión a aceptar")
async def mision_aceptar(interaction: discord.Interaction, nombre: str):
    misiones_lista = leer_misiones()
    mision_obj = next((m for m in misiones_lista if m["nombre"].lower() == nombre.lower()), None)
    if not mision_obj:
        await interaction.response.send_message(f"❌ No existe la misión '{nombre}'", ephemeral=True)
        return

    user_id = str(interaction.user.id)
    if user_id in mision_obj["jugadores"]:
        await interaction.response.send_message(f"❌ Ya tienes la misión '{nombre}' activa", ephemeral=True)
        return

    # Añadir usuario a la misión
    mision_obj["jugadores"].append(user_id)
    guardar_misiones(misiones_lista)

    await interaction.response.send_message(f"✅ Has aceptado la misión '{nombre}'", ephemeral=True)

@mision_aceptar.autocomplete("nombre")
async def mision_aceptar_autocomplete(interaction: discord.Interaction, current: str):
    misiones_lista = leer_misiones()
    return [
        app_commands.Choice(name=m["nombre"], value=m["nombre"])
        for m in misiones_lista if current.lower() in m["nombre"].lower()
    ][:25]


# --- Subcomando /mision abandonar ---
@mision.command(name="abandonar", description="Abandona una misión activa")
@app_commands.describe(nombre="Nombre de la misión a abandonar")
async def mision_abandonar(interaction: discord.Interaction, nombre: str):
    misiones_lista = leer_misiones()
    mision_obj = next((m for m in misiones_lista if m["nombre"].lower() == nombre.lower()), None)
    if not mision_obj:
        await interaction.response.send_message(f"❌ No existe la misión '{nombre}'", ephemeral=True)
        return

    user_id = str(interaction.user.id)
    if user_id not in mision_obj["jugadores"]:
        await interaction.response.send_message(f"❌ No tienes la misión '{nombre}' activa", ephemeral=True)
        return

    # Quitar usuario de la misión
    mision_obj["jugadores"].remove(user_id)
    guardar_misiones(misiones_lista)

    await interaction.response.send_message(f"✅ Has abandonado la misión '{nombre}'", ephemeral=True)

@mision_abandonar.autocomplete("nombre")
async def mision_abandonar_autocomplete(interaction: discord.Interaction, current: str):
    misiones_lista = leer_misiones()
    user_id = str(interaction.user.id)
    opciones = [m["nombre"] for m in misiones_lista if user_id in m.get("jugadores", [])]
    return [
        app_commands.Choice(name=m, value=m)
        for m in opciones if current.lower() in m.lower()
    ][:25]


# --- Subcomando /mision finalizar (solo staff) ---
@mision.command(name="finalizar", description="Marca una misión como finalizada para todos los jugadores (solo staff)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(nombre="Nombre de la misión a finalizar")
async def mision_finalizar(interaction: discord.Interaction, nombre: str):
    misiones_lista = leer_misiones()
    mision_obj = next((m for m in misiones_lista if m["nombre"].lower() == nombre.lower()), None)
    if not mision_obj:
        await interaction.response.send_message(f"❌ No existe la misión '{nombre}'", ephemeral=True)
        return

    usuarios_afectados = mision_obj.get("jugadores", []).copy()
    if not usuarios_afectados:
        await interaction.response.send_message(f"❌ Ningún jugador tiene activa la misión '{nombre}'", ephemeral=True)
        return

    # Limpiar lista de jugadores
    mision_obj["jugadores"] = []
    guardar_misiones(misiones_lista)

    embed = discord.Embed(
        title=f"✅ Misión '{nombre}' finalizada",
        description=f"Jugadores afectados: {len(usuarios_afectados)}",
        color=discord.Color.green()
    )

    dificultad = mision_obj["dificultad"]
    bloques = ""
    for i in range(1, 11):
        if i <= dificultad:
            if i <= 3:
                bloques += "🟩"
            elif i <= 6:
                bloques += "🟨"
            else:
                bloques += "🟥"
        else:
            bloques += "⬜"

    embed.add_field(
        name=f"{mision_obj['nombre']}",
        value=f"🌴 Isla: {mision_obj['isla']}\n"
              f"📝 {mision_obj['descripcion']}\n"
              f"🎯 Dificultad: {bloques} ({dificultad}/10)\n"
              f"👥 Jugadores afectados: {', '.join(f'<@{uid}>' for uid in usuarios_afectados)}",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

@mision_finalizar.autocomplete("nombre")
async def mision_finalizar_autocomplete(interaction: discord.Interaction, current: str):
    misiones_lista = leer_misiones()
    opciones = [m["nombre"] for m in misiones_lista if m.get("jugadores")]
    return [
        app_commands.Choice(name=m, value=m)
        for m in opciones if current.lower() in m.lower()
    ][:25]


# --- Comando independiente /misiones con botones ---
@app_commands.command(name="misiones", description="Muestra todas las misiones disponibles")
async def misiones(interaction: discord.Interaction):
    misiones_lista = leer_misiones()
    if not misiones_lista:
        await interaction.response.send_message("No hay misiones disponibles.", ephemeral=True)
        return

    user_id = str(interaction.user.id)
    embed = discord.Embed(
        title="Misiones disponibles",
        description="Lista de misiones que puedes aceptar",
        color=discord.Color.green()
    )

    view = View()
    for index, m in enumerate(misiones_lista, start=1):
        estado = "✅ Aceptada" if user_id in m.get("jugadores", []) else "❌ No aceptada"

        dificultad = m["dificultad"]
        bloques = ""
        for i in range(1, 11):
            if i <= dificultad:
                if i <= 3:
                    bloques += "🟩"
                elif i <= 6:
                    bloques += "🟨"
                else:
                    bloques += "🟥"
            else:
                bloques += "⬜"

        embed.add_field(
            name=f"{index}. {m['nombre']} ({estado})",
            value=f"🌴 Isla: {m['isla']}\n"
                  f"📝 {m['descripcion']}\n"
                  f"🎯 Dificultad: {bloques} ({dificultad}/10)\n"
                  f"👥 Jugadores: {', '.join(f'<@{uid}>' for uid in m.get('jugadores', [])) or 'Ninguno'}",
            inline=False
        )

        button = Button(label=str(index), style=discord.ButtonStyle.primary)

        async def button_callback(interaction_btn, m=m):
            uid = str(interaction_btn.user.id)
            jugadores = m.setdefault("jugadores", [])
            if uid not in jugadores:
                jugadores.append(uid)
                guardar_misiones(misiones_lista)
                await interaction_btn.response.send_message(
                    f"✅ Has aceptado la misión '{m['nombre']}'\n"
                    f"👥 Jugadores actuales: {', '.join(f'<@{j}>' for j in jugadores)}",
                    ephemeral=True
                )
            else:
                jugadores.remove(uid)
                guardar_misiones(misiones_lista)
                await interaction_btn.response.send_message(
                    f"❌ Has abandonado la misión '{m['nombre']}'\n"
                    f"👥 Jugadores actuales: {', '.join(f'<@{j}>' for j in jugadores) or 'Ninguno'}",
                    ephemeral=True
                )

        button.callback = button_callback
        view.add_item(button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

# ---------- SETUP ----------
def setup(tree: app_commands.CommandTree):
    tree.add_command(mision, guild=config.GUILD)
    tree.add_command(misiones, guild=config.GUILD)