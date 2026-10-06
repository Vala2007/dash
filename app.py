import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, clientside_callback, ClientsideFunction

from tabs import introduccion, eda, referencias

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="KRKPA7 Dashboard",
)

# ----- Botón de modo oscuro -----
theme_toggle = html.Button(
    "🌙",
    id="theme-toggle",
    className="krk-theme-toggle",
    n_clicks=0,
)

# ----- Hero header -----
hero = html.Div([
    html.Div([
        html.Img(
            src="/assets/logo.jpeg",
            className="krk-hero-logo",
            alt="Logo KRKPA7",
        ),
        html.Div([
            html.H1("King + Rook vs King + Pawn on A7", className="mb-1"),
            html.P(
                "Análisis del final KRKPA7"
            ),
        ], className="krk-hero-text"),
    ], className="krk-hero-inner"),
], className="krk-hero")

# ----- Tabs -----
tabs = dbc.Tabs(
    [
        dbc.Tab(label="Introducción", tab_id="intro", children=introduccion.layout()),
        dbc.Tab(label="EDA",          tab_id="eda",   children=eda.layout()),
        dbc.Tab(label="Referencias",  tab_id="refs",  children=referencias.layout()),
    ],
    active_tab="intro",
)

# ----- Footer -----
footer = html.Div([
    html.P("Valamy Donado · Abraham Navarro", className="mb-1"),
    html.P("Proyecto KRKPA7 · 2026", className="mb-0"),
], className="krk-footer")

app.layout = dbc.Container([
    dcc.Store(id="theme-store", data="light"),
    theme_toggle,
    hero,
    tabs,
    footer,
], fluid=True, style={"maxWidth": "1300px", "paddingTop": "32px", "paddingBottom": "30px"})


# ----- Callback del toggle -----
clientside_callback(
    """
    function(n_clicks, current) {
        if (n_clicks === 0) { return window.dash_clientside.no_update; }
        const next = current === "light" ? "dark" : "light";
        if (next === "dark") {
            document.body.classList.add("dark-mode");
        } else {
            document.body.classList.remove("dark-mode");
        }
        return next;
    }
    """,
    Output("theme-store", "data"),
    Input("theme-toggle", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)

# Cambia el ícono según el modo
clientside_callback(
    """
    function(theme) {
        return theme === "dark" ? "☀️" : "🌙";
    }
    """,
    Output("theme-toggle", "children"),
    Input("theme-store", "data"),
)

server = app.server  

if __name__ == "__main__":
    app.run(debug=True)