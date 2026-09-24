"""
Módulo de utilidades de roles para el rol de One Piece.
Define el orden de roles y función para obtener el rango de un miembro.
"""

# Orden jerárquico de los roles
ORDEN_ROLES = [
    "☀️ Sol",
    "🌙 Luna",
    "👑 Emperador",
    "🐉 Dragón",
    "🐙 Kraken",
    "🏔️ Montaña",
    "🌊 Monstruo Marino",
    "🐗 Bestia",
    "🐯 Tigre",
    "🐾 Perro"
]

def obtener_rango(member):
    """
    Devuelve el rango más alto que tenga el miembro según ORDEN_ROLES.
    Si no tiene ningún rol válido, devuelve "Sin rol".
    """
    roles_en_orden = [r.name for r in member.roles if r.name in ORDEN_ROLES]
    if roles_en_orden:
        return min(roles_en_orden, key=lambda r: ORDEN_ROLES.index(r))
    return "Sin rol"
