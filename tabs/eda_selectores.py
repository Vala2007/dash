import math

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc, callback, Input, Output, ctx
import dash_bootstrap_components as dbc

from data.load_data import load_data

df = load_data()
VARS = [c for c in df.columns if c != "class"]

# Mismos colores que ya usaba eda.py
COLORES_CLASS = {"nowin": "#40B5A0", "won": "#008080"}
COLORES_BINARIAS = ["#00CED1", "#8BFFFF"]
COLORES_TERNARIAS = ["#20B2AA", "#00CED1", "#8BFFFF"]


def _vacia():
    fig = go.Figure()
    fig.add_annotation(text="Selecciona al menos una variable", showarrow=False,
                       font=dict(size=16))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(height=180)
    return fig


# ---------------------------------------------------------------- tortas
def figura_tortas(sel):
    if not sel:
        return _vacia()

    n_cols = min(3, len(sel))
    n_filas = math.ceil(len(sel) / n_cols)
    fig = make_subplots(
        rows=n_filas, cols=n_cols,
        specs=[[{"type": "pie"}] * n_cols for _ in range(n_filas)],
        subplot_titles=sel,
        vertical_spacing=min(0.08, 0.9 / max(n_filas - 1, 1)),
    )

    for i, var in enumerate(sel):
        t = df[var].value_counts()
        paleta = COLORES_TERNARIAS if len(t) == 3 else COLORES_BINARIAS
        fig.add_trace(
            go.Pie(
                labels=list(t.index), values=list(t.values), text=list(t.index),
                textinfo="text", textposition="inside", textfont=dict(size=16),
                marker=dict(colors=[paleta[k % len(paleta)] for k in range(len(t))]),
                hovertemplate="Frecuencia: %{value}<br>Porcentaje: %{percent}<extra></extra>",
                showlegend=False, sort=False, direction="clockwise",
            ),
            row=i // n_cols + 1, col=i % n_cols + 1,
        )

    fig.update_layout(
        height=300 * n_filas + 40, showlegend=False, font=dict(size=14),
        margin=dict(l=20, r=20, t=40, b=20), hoverlabel=dict(font=dict(size=16)),
    )
    for ann in fig.layout.annotations:
        ann.font.size = 16
    return fig


# ---------------------------------------------------------------- barras
def figura_barras(sel):
    if not sel:
        return _vacia()

    n_cols = 2 if len(sel) > 1 else 1
    n_filas = math.ceil(len(sel) / n_cols)
    fig = make_subplots(
        rows=n_filas, cols=n_cols, subplot_titles=sel,
        vertical_spacing=min(0.05, 0.9 / max(n_filas - 1, 1)),
        horizontal_spacing=0.08,
    )

    for i, var in enumerate(sel):
        ct = pd.crosstab(df[var], df["class"])
        pct = ct.div(ct.sum(axis=0), axis=1) * 100
        cats = [str(c) for c in ct.index]

        for clase in ["won", "nowin"]:
            fig.add_trace(
                go.Bar(
                    x=cats, y=ct[clase].tolist(), name=clase,
                    marker_color=COLORES_CLASS[clase], legendgroup=clase,
                    showlegend=(i == 0),
                    customdata=[round(v, 1) for v in pct[clase]],
                    hovertemplate="Frecuencia: %{y}<br>Porcentaje: %{customdata}%<extra></extra>",
                ),
                row=i // n_cols + 1, col=i % n_cols + 1,
            )

    fig.update_xaxes(tickfont=dict(size=11))
    fig.update_yaxes(tickfont=dict(size=10))
    fig.update_layout(
        barmode="group", bargap=0.25,
        height=max(360, 330 * n_filas),
        legend=dict(orientation="h", xref="container", yref="container",
                    x=0.5, xanchor="center", y=0.99, yanchor="top",
                    font=dict(size=15)),
        margin=dict(l=40, r=40, t=70, b=30), hoverlabel=dict(font=dict(size=14)),
    )
    for ann in fig.layout.annotations:
        ann.font.size = 13
    return fig


# ---------------------------------------------------------------- UI
def _selector(prefix, titulo, defaults):
    return dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    html.P("Marca las variables que quieres ver; el gráfico se actualiza al instante.",
                           className="text-muted mb-2"),
                    html.Div([
                        dbc.Button("Todas", id=f"{prefix}-all", size="sm", color="primary",
                                   outline=True, className="me-2"),
                        dbc.Button("Ninguna", id=f"{prefix}-none", size="sm", color="primary",
                                   outline=True),
                    ], className="mb-2"),
                    html.Div(
                        dbc.Checklist(
                            id=f"{prefix}-vars",
                            options=[{"label": v, "value": v} for v in VARS],
                            value=defaults, inline=True, className="krk-checks",
                        ),
                        className="krk-checks-box",
                    ),
                    dcc.Graph(id=f"{prefix}-graph", config={"displayModeBar": False}),
                ],
                title=titulo,
            )
        ],
        start_collapsed=True,
        className="krk-accordion",
    )


def _registrar(prefix, fig_fn):
    @callback(
        Output(f"{prefix}-vars", "value"),
        Input(f"{prefix}-all", "n_clicks"),
        Input(f"{prefix}-none", "n_clicks"),
        prevent_initial_call=True,
    )
    def _marcar(_a, _b):
        return VARS if ctx.triggered_id == f"{prefix}-all" else []

    @callback(Output(f"{prefix}-graph", "figure"), Input(f"{prefix}-vars", "value"))
    def _dibujar(sel):
        return fig_fn(sel or [])


_registrar("tortas", figura_tortas)
_registrar("barras", figura_barras)


def selector_tortas():
    return _selector("tortas", "Elegir variables y ver las tortas", VARS[:4])


def selector_barras():
    return _selector("barras", "Elegir variables y ver las barras por clase", VARS[:4])