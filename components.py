"""Componentes reutilizables del dashboard KRKPA7."""
from dash import html, dcc
import dash_bootstrap_components as dbc


def section(*children, alt=False, className=""):
    """Bloque de contenido con fondo propio."""
    clases = "krk-section" + (" krk-section-alt" if alt else "")
    return html.Div(list(children), className=f"{clases} {className}".strip())


def seccion(titulo, children, alt=False, abierta=False):
    """Sección con fondo propio que se puede desplegar y retraer."""
    clases = "krk-section" + (" krk-section-alt" if alt else "")
    return html.Div(
        dbc.Accordion(
            [dbc.AccordionItem(children, title=titulo, item_id="s")],
            start_collapsed=not abierta,
            className="krk-acc",
        ),
        className=clases,
    )


def colapsable(titulo, children, abierta=False):
    """Bloque sencillo (sin fondo) que se puede desplegar y retraer."""
    return html.Div(
        dbc.Accordion(
            [dbc.AccordionItem(children, title=titulo, item_id="s")],
            start_collapsed=not abierta,
            className="krk-acc krk-acc-sm",
        ),
        className="krk-collapse-plain",
    )


def stat_card(value, label, className=""):
    """Número grande + descripción."""
    return html.Div(
        [html.H4(value), html.P(label)],
        className=f"krk-kpi{className}".strip(),
    )


def feature_card(icon, title, text, href=None):
    """Tarjeta clicable que lleva a otra sección."""
    return dcc.Link(
        [
            html.Span(icon, className="krk-feature-icon"),
            html.H4(title),
            html.P(text),
        ],
        href=href,
        className="krk-feature",
    )


def page_header(icon, title, subtitle):
    """Encabezado compacto de cada sección (sin icono)."""
    return html.Div(
        html.Div([html.H1(title), html.P(subtitle)]),
        className="krk-page-header",
    )


def navbar(links):
    """Barra superior fija. `links` = lista de (etiqueta, href)."""
    return html.Header(
        [
            dcc.Link(
                [
                    html.Img(src="/assets/logo.jpeg", alt="Logo KRKPA7"),
                    html.Span("KRKPA7"),
                ],
                href="/",
                className="krk-brand",
            ),
            dbc.Nav(
                [dbc.NavLink(label, href=href, active="exact") for label, href in links],
                className="krk-nav-links",
            ),
            html.Button("☀️", id="theme-toggle", className="krk-theme-toggle",
                        n_clicks=0, title="Cambiar tema"),
        ],
        className="krk-nav",
    )


def footer():
    return html.Footer(
        [
            html.P("Valamy Donado · Abraham Navarro", className="mb-1"),
            html.P("Proyecto KRKPA7 · 2026", className="mb-0"),
        ],
        className="krk-footer",
    )