from dash import html, dcc
import dash_bootstrap_components as dbc

from components import stat_card, feature_card

# (símbolo, color, columna, fila, retraso de animación)
# Fila 0 = rank 8, columna 0 = columna a  ->  el peón negro está en a7 (col 0, fila 1)
# Convención UCI: peón y rey negros; rey y torre blancos.
PIEZAS = [
    ("♚", "blanca", 2, 3, "0s"),
    ("♜", "blanca", 4, 6, ".7s"),
    ("♚", "negra", 5, 1, "1.4s"),
    ("♟", "negra", 0, 1, "2.1s"),
]


def tablero_decorativo():
    """Tablero CSS con el final KRKPA7.

    >>> Para poner tu propia imagen o animación, reemplaza el contenido de
    >>> `html.Div(id="hero-visual")` en layout() por, por ejemplo:
    >>>     html.Img(src="/assets/hero.png", className="krk-hero-img")
    """
    casillas = [
        html.Div(
            className="krk-sq "
            + ("l" if (r + c) % 2 == 0 else "d")
            + (" target" if (r, c) == (0, 0) else "")  # a8: casilla de coronación
        )
        for r in range(8)
        for c in range(8)
    ]
    piezas = [
        html.Span(
            simbolo,
            className=f"krk-piece {color}",
            style={"left": f"{c * 12.5}%", "top": f"{r * 12.5}%", "animationDelay": delay},
        )
        for simbolo, color, c, r, delay in PIEZAS
    ]
    return html.Div(
        [html.Div(casillas, className="krk-board-grid"), *piezas],
        className="krk-board",
    )


def layout():
    return html.Div(
        [
            # ---------- Hero ----------
            html.Section(
                [
                    html.Div(
                        [
                            html.P("Final de ajedrez · Shapiro, 1983", className="krk-kicker"),
                            html.H1(
                                "El peón está en A7 y la torre decide la partida",
                                className="krk-welcome-title",
                            ),
                            html.P(
                                "Exploramos 3.196 posiciones de Rey + Torre (blancas) contra "
                                "Rey + Peón (negras) para entender qué patrones hacen que el "
                                "peón logre coronar o que la torre lo detenga.",
                                className="krk-welcome-lead",
                            ),
                            html.P(
                                [
                                    html.B("won"),
                                    ": gana el bando del peón (negras). ",
                                    html.B("nowin"),
                                    ": las blancas detienen al peón.",
                                ],
                                className="krk-welcome-lead",
                                style={"fontSize": "0.95rem", "opacity": 0.85},
                            ),
                        ],
                        className="krk-welcome-text",
                    ),
                    html.Div(tablero_decorativo(), id="hero-visual", className="krk-welcome-visual"),
                ],
                className="krk-welcome",
            ),

            # ---------- Datos clave ----------
            dbc.Row(
                [
                    dbc.Col(stat_card("3.196", "posiciones del final"), xs=6, md=3),
                    dbc.Col(stat_card("36", "variables categóricas"), xs=6, md=3),
                    dbc.Col(stat_card("2", "clases: won / nowin"), xs=6, md=3),
                    dbc.Col(stat_card("1983", "tesis de Shapiro, Edimburgo"), xs=6, md=3),
                ],
                className="g-3 mb-4",
            ),

            # ---------- Accesos ----------
            html.Div(
                [
                    feature_card("", "Introducción",
                                 "Contexto, objetivos, marco teórico y descripción del dataset.", "/intro"),
                    feature_card("", "EDA",
                                 "Distribuciones, V de Cramér y relación de cada variable con la clase.", "/eda"),
                    feature_card("", "Modelado predictivo",
                                 "Selección del modelo (CatBoost) y un predictor de posiciones.", "/modelo"),
                    feature_card("", "Referencias",
                                 "Bibliografía usada en el proyecto.", "/refs"),
                ],
                className="krk-feature-grid",
            ),
        ]
    )