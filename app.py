import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, clientside_callback

from components import navbar, footer, page_header
from tabs import bienvenida, introduccion, eda, modelo, referencias

FUENTES = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,800&display=swap"

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, FUENTES],
    suppress_callback_exceptions=True,
    title="KRKPA7 Dashboard",
)
server = app.server

# ----- Páginas: ruta -> (icono, título, subtítulo, función layout) -----
PAGES = {
    "/intro":  ("♞", "Introducción", "Contexto, objetivos, marco teórico y dataset", introduccion.layout),
    "/eda":    ("♝", "EDA", "Qué dicen las 36 variables sobre el resultado", eda.layout),
    "/modelo": ("♛", "Modelado predictivo", "CatBoost y un predictor de posiciones", modelo.layout),
    "/refs":   ("♜", "Referencias", "Bibliografía del proyecto", referencias.layout),
}
NAV_LABELS = {"/intro": "Introducción", "/eda": "EDA", "/modelo": "Modelado predictivo", "/refs": "Referencias"}
NAV_LINKS = [(NAV_LABELS[ruta], ruta) for ruta in PAGES]

# Se construyen una sola vez para que cambiar de pestaña sea instantáneo
_cache = {}


def get_page(ruta):
    if ruta not in _cache:
        if ruta in PAGES:
            icono, titulo, sub, fn = PAGES[ruta]
            _cache[ruta] = html.Div([page_header(icono, titulo, sub), fn()], className="krk-page")
        else:
            _cache[ruta] = html.Div(bienvenida.layout(), className="krk-page")
    return _cache[ruta]


for _ruta in [*PAGES, "/"]:
    get_page(_ruta)

# ----- Layout -----
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="theme-store", data="dark", storage_type="local"),
    navbar(NAV_LINKS),
    html.Main(id="page-content", className="krk-shell"),
    footer(),
])


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    ruta = (pathname or "/").rstrip("/") or "/"
    return get_page(ruta)


# ----- Tema claro/oscuro -----
clientside_callback(
    """
    function(n, current) {
        if (!n) { return window.dash_clientside.no_update; }
        return current === "dark" ? "light" : "dark";
    }
    """,
    Output("theme-store", "data"),
    Input("theme-toggle", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)

clientside_callback(
    """
    function(theme) {
        document.body.classList.toggle("dark-mode", theme === "dark");
        return theme === "dark" ? "☀️" : "🌙";
    }
    """,
    Output("theme-toggle", "children"),
    Input("theme-store", "data"),
)

if __name__ == "__main__":
    app.run(debug=True)