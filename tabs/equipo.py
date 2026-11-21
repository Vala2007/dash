"""Pestaña Equipo: foto, nombre y LinkedIn de cada integrante.

Fotos: guárdalas en  assets/equipo/  (jpg, jpeg, png o webp) con el nombre que pongas en
la columna "foto" de MIEMBROS, sin la extensión. Si no encuentra la foto, muestra las iniciales.
"""
from pathlib import Path

from dash import html

CARPETA_FOTOS = Path(__file__).resolve().parent.parent / "assets" / "equipo"

# >>> EDITA AQUÍ: nombre, rol, nombre de la foto (sin extensión) y link de LinkedIn
MIEMBROS = [
    {
        "nombre": "Valamy Donado",
        "rol": "Integrante del proyecto",
        "foto": "valamy",
        "linkedin": "https://www.linkedin.com/in/valamy-donado-gorut-3a9521338/",
    },
    {
        "nombre": "Abraham Navarro",
        "rol": "Integrante del proyecto",
        "foto": "abraham",
        "linkedin": "https://www.linkedin.com/in/TU_PERFIL_ABRAHAM/",
    },
]


def _ruta_foto(base):
    if not base:
        return None
    for ext in ("jpg", "jpeg", "png", "webp"):
        if (CARPETA_FOTOS / f"{base}.{ext}").exists():
            return f"/assets/equipo/{base}.{ext}"
    return None


def _iniciales(nombre):
    return "".join(p[0] for p in nombre.split()[:2]).upper()


def _tarjeta(m):
    nombre = m.get("nombre", "")
    rol = m.get("rol")
    linkedin = m.get("linkedin")
    src = _ruta_foto(m.get("foto"))
    foto = (html.Img(src=src, alt=f"Foto de {nombre}", className="krk-member-photo")
            if src else html.Div(_iniciales(nombre) or "?", className="krk-member-photo krk-member-initials"))
    hijos = [foto, html.H3(nombre, className="krk-member-name")]
    if rol:                                   # el rol es opcional
        hijos.append(html.P(rol, className="krk-member-role"))
    if linkedin:                              # el LinkedIn también
        hijos.append(html.A([html.Span("in", className="krk-linkedin-badge"), "LinkedIn"],
                            href=linkedin, target="_blank", rel="noopener noreferrer",
                            className="krk-linkedin"))
    return html.Div(hijos, className="krk-member")


def layout():
    return html.Div(
        html.Div([_tarjeta(m) for m in MIEMBROS], className="krk-team-grid"),
    )