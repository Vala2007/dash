import json
from functools import lru_cache
from pathlib import Path
 
import pandas as pd
import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, ctx, html, no_update
 
from components import stat_card
 
# Significado de cada variable (convención UCI, opción B), para la ayuda bajo cada selector
DEFINICIONES = {
    'wkblk': '¿El rey blanco estorba el camino de su propia torre? (contexto de doble ataque)',
    'wknwy': '¿El rey blanco está en el camino de la torre blanca cuando esta intenta atacar la casilla de coronación?',
    'wkna8': '¿El rey blanco está en la fila 8 en posición de ayudar a la torre blanca?',
    'wkona': '¿El rey blanco está en la columna a en posición de ayudar a la torre blanca?',
    'wkspr': '¿El rey blanco puede apoyar a la torre blanca? (importa en dobles ataques tipo horquilla, con la torre entre el rey negro y el peón)',
    'wkxbq': '¿El rey blanco es atacado de algún modo por el peón negro ya promovido (la nueva dama)?',
    'wkxcr': '¿El rey blanco puede atacar la casilla crítica (b7)?',
    'wkxbp': '¿El rey blanco puede atacar al peón negro?',
    'whxbp': '¿Las blancas atacan al peón negro con la torre? (solo en dirección x<0, y=0)',
    'wxqsq': '¿Alguna pieza blanca controla la casilla de coronación (a8)?',
    'cntxt': '¿El rey negro está en un borde del tablero y no en a8?',
    'dsopp': '¿Los reyes están en oposición normal? (separados por una casilla vacía, en línea perpendicular al borde relevante y con el rey blanco más cerca del centro)',
    'dwipd': '¿La distancia del rey negro al punto de intersección es mayor que dos? Si no, el rey negro puede evitar la clavada acercándose.',
    'katri': '¿Algún rey controla el punto de intersección (la casilla de borde que usaría la torre para clavar)? ¿Cuál?',
    'mulch': '¿Pueden las blancas renovar el jaque con ventaja?',
    'qxmsq': '¿La casilla de mate está atacada por el peón negro promovido?',
    'r2ar8': '¿La torre blanca tiene acceso seguro a la columna a o a la fila 8?',
    'reskr': '¿Puede la torre blanca, sola, renovar la amenaza de doble ataque?',
    'rimmx': '¿Se puede capturar la torre blanca de forma segura (con el peón o el rey negros)?',
    'rkxwp': '¿La torre blanca incide sobre el peón negro? (solo en dirección x<0, y=0)',
    'rxmsq': '¿La torre blanca ataca de forma segura la casilla de mate?',
    'simpl': '¿Se aplica un patrón muy simple? (ahogado, clavada retardada o jaque perpetuo en posiciones concretas)',
    'skewr': '¿Hay una posible clavada (y no una horquilla)? Es decir, ¿el punto de intersección queda fuera del segmento entre el peón promovido y el rey negro?',
    'skrxp': '¿Puede la torre blanca lograr una clavada, o el rey blanco atacar al peón negro?',
    'stlmt': '¿El rey negro está en ahogado (stalemate)?',
    'thrsk': '¿Hay una amenaza de clavada al acecho?',
    'bkcti': '¿Puede el rey negro controlar el punto de intersección?',
    'bkna8': '¿El rey negro está en la casilla a8 (la de coronación)?',
    'bknck': '¿El rey negro está en jaque?',
    'bkovl': '¿El rey negro está sobrecargado, sin poder cubrir todos los puntos de intersección de la torre blanca?',
    'bkpos': '¿El rey negro está en una posible posición de horquilla (y no de clavada)? Es decir, ¿el punto de intersección queda entre las piezas negras?',
    'btoeg': '¿El rey negro está a una jugada del borde relevante (fila 8 o columna a)?',
}
 
CARPETA = Path(__file__).resolve().parent.parent / "models"
RUTA_MODELO = CARPETA / "modelo_ajedrez.pkl"
RUTA_META = CARPETA / "modelo_meta.json"
 
CLASE_POSITIVA = "won"
 
# Cómo se agrupan las variables en el formulario (las que no estén en la meta se ignoran)
GRUPOS = [
    ("Rey blanco (wk…)", ["wkblk", "wknwy", "wkna8", "wkona", "wkspr", "wkxbq", "wkxcr", "wkxbp"]),
    ("Torre y control blanco",
     ["whxbp", "wxqsq", "r2ar8", "reskr", "rimmx", "rkxwp", "rxmsq", "skewr", "skrxp", "thrsk", "qxmsq"]),
    ("Rey negro y peón (bk…)", ["bkcti", "bkna8", "bknck", "bkovl", "bkpos", "btoeg", "cntxt"]),
    ("Reyes y patrones generales", ["dsopp", "dwipd", "katri", "mulch", "simpl", "stlmt"]),
]
 
# Texto de cada nivel (lo que no esté aquí se muestra tal cual)
ETIQUETAS_NIVEL = {
    "katri": {"n": "n — ninguno", "b": "b — rey blanco", "w": "w — rey negro"},
    "btoeg": {"t": "t — sí", "n": "n — no"},
}
 
 
# ---------------------------------------------------------------- carga
@lru_cache(maxsize=1)
def cargar_meta():
    """Lee modelo_meta.json. Devuelve None si no existe."""
    try:
        return json.loads(RUTA_META.read_text(encoding="utf-8"))
    except Exception:
        return None
 
 
@lru_cache(maxsize=1)
def cargar_modelo():
    """Carga el pipeline. Devuelve (modelo, mensaje_de_error)."""
    try:
        import joblib
        return joblib.load(RUTA_MODELO), None
    except Exception as e:  # falta el archivo, falta catboost, versión distinta de sklearn…
        return None, f"{type(e).__name__}: {e}"
 
 
@lru_cache(maxsize=1)
def cargar_ejemplos():
    """Posiciones reales del dataset (para el botón de ejemplo aleatorio)."""
    try:
        from data.load_data import load_data
        meta = cargar_meta()
        df = load_data()
        columnas = meta["variables"] + ["class"]
        return df[columnas].astype(str).reset_index(drop=True)
    except Exception as e:
        print(f"[modelo] No se pudo cargar el dataset para ejemplos: {type(e).__name__}: {e}")
        return None
 
 
def etiqueta_nivel(var, nivel):
    if var in ETIQUETAS_NIVEL and nivel in ETIQUETAS_NIVEL[var]:
        return ETIQUETAS_NIVEL[var][nivel]
    if nivel == "t":
        return "t — sí"
    if nivel == "f":
        return "f — no"
    return nivel
 
 
# ------------------------------------------------------------ componentes
def _campo(var, niveles):
    opciones = [{"label": "— elegir —", "value": ""}] + [
        {"label": etiqueta_nivel(var, n), "value": n} for n in niveles
    ]
    return dbc.Col(
        [
            dbc.Label(html.Span(var, className="krk-var"), className="mb-0 d-block"),
            dbc.Select(
                id={"type": "var", "name": var},
                options=opciones, value="", size="sm",
            ),
            html.Small(DEFINICIONES.get(var, ""), className="text-muted d-block mt-1"),
        ],
        xs=12, md=6, lg=4, className="mb-3",
    )
 
 
def _formulario(meta):
    en_meta = set(meta["variables"])
    usadas, items = set(), []
    for titulo, variables in GRUPOS:
        vs = [v for v in variables if v in en_meta]
        usadas.update(vs)
        if vs:
            items.append((titulo, vs))
    resto = [v for v in meta["variables"] if v not in usadas]
    if resto:
        items.append(("Otras variables", resto))
 
    return dbc.Accordion(
        [
            dbc.AccordionItem(
                dbc.Row([_campo(v, meta["niveles"][v]) for v in vs]),
                title=f"{titulo} · {len(vs)}",
            )
            for titulo, vs in items
        ],
        start_collapsed=False, always_open=True, className="krk-accordion",
    )
 
 
def _tarjetas_metricas(meta):
    m = meta.get("metricas_test", {})
    ic = meta.get("ic95_accuracy")
    acc = m.get("Accuracy")
    tarjetas = [stat_card("CatBoost", "modelo seleccionado")]
    if acc is not None:
        tarjetas.append(stat_card(f"{acc * 100:.1f} %", "exactitud en el conjunto de prueba"))
    if ic:
        tarjetas.append(stat_card(f"{ic[0] * 100:.1f}–{ic[1] * 100:.1f} %", "IC 95 % de la exactitud"))
    if "AUC-ROC" in m:
        tarjetas.append(stat_card(f"{m['AUC-ROC']:.3f}", "AUC-ROC en prueba"))
    tarjetas = tarjetas[:4]
    ancho = 12 // max(len(tarjetas), 1)
    return dbc.Row(
        [dbc.Col(t, xs=6, md=ancho) for t in tarjetas],
        className="g-3",
    )
 
 
def _aviso_sin_modelo(detalle):
    return html.Div(
        [
            html.H2("Modelado predictivo"),
            dbc.Alert(
                [
                    html.B("No se pudo cargar el modelo. "),
                    "Copia ",
                    html.Code("modelo_ajedrez.pkl"),
                    " y ",
                    html.Code("modelo_meta.json"),
                    " (los genera el notebook de modelado) a la carpeta ",
                    html.Code("models/"),
                    " del dashboard e instala catboost en este entorno.",
                    html.Br(),
                    html.Small(detalle or "", className="text-muted"),
                ],
                color="warning",
            ),
        ],
        className="krk-section",
    )
 
 
# ------------------------------------------------------------------ layout
def layout():
    meta = cargar_meta()
    modelo, error = cargar_modelo() if meta else (None, "No existe models/modelo_meta.json")
    if meta is None or modelo is None:
        return html.Div(_aviso_sin_modelo(error))
 
    hay_ejemplos = cargar_ejemplos() is not None
 
    return html.Div([
        html.Div([
            html.H2("Modelo final"),
            html.P(
                "El modelo final es un CatBoost entrenado con 32 variables categóricas "
                "(se eliminaron spcop, skach, hdchk y reskd por tener un nivel con menos "
                "del 1 % de las posiciones). Dada una posición, estima si gana el bando "
                "del peón (won) o si las blancas lo detienen (nowin)."
            ),
            _tarjetas_metricas(meta),
        ], className="krk-section krk-section-alt"),
 
        html.Div([
            html.H2("Predecir una posición"),
            html.P(
                "Elige el valor de cada variable (el significado está debajo de cada "
                "selector) o carga una posición real del dataset para ver si el modelo acierta."
            ),
            _formulario(meta),
            html.Div(
                [
                    dbc.Button("Predecir", id="btn-predecir", color="primary", className="me-2"),
                    dbc.Button("Posición aleatoria del dataset", id="btn-aleatoria",
                               color="light", className="me-2 krk-btn-grey",
                               disabled=not hay_ejemplos),
                    dbc.Button("Limpiar", id="btn-limpiar", color="light", className="krk-btn-grey"),
                ],
                className="mb-3",
            ),
            html.Div(id="resultado-modelo"),
        ], className="krk-section"),
 
        html.Div([
            html.H3("Cómo leer el resultado", className="mt-0"),
            html.Ul([
                html.Li("La probabilidad es la que estima el modelo, no una garantía: con exactitud cercana al 99 % puede equivocarse en casos raros."),
                html.Li("El modelo aprendió de las 3.196 posiciones del dataset. No es un motor de ajedrez: una combinación de valores que no corresponde a una posición real puede dar una respuesta sin sentido."),
                html.Li("Variables más influyentes (importancia por permutación): bknck, rimmx y wxqsq."),
            ]),
        ], className="krk-section krk-section-alt"),
    ])
 
 
# ---------------------------------------------------------------- callbacks
@callback(
    Output({"type": "var", "name": ALL}, "value"),
    Output("resultado-modelo", "children", allow_duplicate=True),
    Input("btn-aleatoria", "n_clicks"),
    Input("btn-limpiar", "n_clicks"),
    State({"type": "var", "name": ALL}, "id"),
    prevent_initial_call=True,
)
def cargar_o_limpiar(n_aleatoria, n_limpiar, ids):
    nombres = [i["name"] for i in ids]
    if ctx.triggered_id == "btn-aleatoria":
        ej = cargar_ejemplos()
        if ej is None:
            return [no_update] * len(nombres), no_update
        fila = ej.sample(1).iloc[0]
        return [fila[n] for n in nombres], ""
    return [""] * len(nombres), ""
 
 
def predecir_posicion(valores: dict):
    """valores = {variable: nivel}. Devuelve (clase, {clase: prob})."""
    modelo, _ = cargar_modelo()
    meta = cargar_meta()
    fila = pd.DataFrame([{v: str(valores[v]) for v in meta["variables"]}])
    clases = list(modelo.classes_)
    probs = modelo.predict_proba(fila)[0]
    dist = {str(c): float(p) for c, p in zip(clases, probs)}
    return max(dist, key=dist.get), dist
 
 
def tarjeta_resultado(clase, dist, real=None):
    gana_peon = clase == CLASE_POSITIVA
    p = dist[clase]
    texto = ("Gana el bando del peón (negras)" if gana_peon
             else "Las blancas detienen al peón (no hay victoria del peón)")
    hijos = [
        html.H3(f"Predicción: {clase}", className="mt-0"),
        html.P(texto, className="mb-2"),
        html.Small(f"Probabilidad estimada: {p * 100:.1f} %", className="text-muted"),
        dbc.Progress(
            [
                dbc.Progress(value=dist.get("won", 0) * 100, color="primary", bar=True,
                             label=f"won {dist.get('won', 0) * 100:.0f} %"),
                dbc.Progress(value=dist.get("nowin", 0) * 100, color="info", bar=True,
                             label=f"nowin {dist.get('nowin', 0) * 100:.0f} %"),
            ],
            className="my-2", style={"height": "26px"},
        ),
    ]
    if real is not None:
        acierto = real == clase
        hijos.append(
            dbc.Alert(
                f"Clase real en el dataset: {real}. "
                + ("El modelo acertó." if acierto else "El modelo se equivocó en esta posición."),
                color="success" if acierto else "danger", className="mb-0 mt-2",
            )
        )
    return dbc.Card(dbc.CardBody(hijos))
 
 
@callback(
    Output("resultado-modelo", "children"),
    Input("btn-predecir", "n_clicks"),
    State({"type": "var", "name": ALL}, "value"),
    State({"type": "var", "name": ALL}, "id"),
    prevent_initial_call=True,
)
def al_predecir(n, valores, ids):
    nombres = [i["name"] for i in ids]
    elegidos = dict(zip(nombres, valores))
    faltan = [v for v, x in elegidos.items() if not x]
    if faltan:
        return dbc.Alert(
            f"Faltan {len(faltan)} variable(s) por elegir: " + ", ".join(faltan[:8])
            + ("…" if len(faltan) > 8 else ""),
            color="warning",
        )
    try:
        clase, dist = predecir_posicion(elegidos)
    except Exception as e:
        return dbc.Alert(f"No se pudo predecir ({type(e).__name__}: {e})", color="danger")
 
    # Si la combinación coincide con una posición real, se muestra su clase verdadera
    real = None
    ej = cargar_ejemplos()
    if ej is not None:
        mask = pd.Series(True, index=ej.index)
        for v, x in elegidos.items():
            mask &= ej[v] == str(x)
        if mask.any():
            real = ej.loc[mask, "class"].iloc[0]
    return tarjeta_resultado(clase, dist, real)