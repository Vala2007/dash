import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from scipy.stats import chi2_contingency

from data.load_data import load_data


df = load_data()
vars_predictoras = [c for c in df.columns if c != "class"]

COLORES_CLASS = {"nowin": "#F3BF97", "won": "#1CE0D3"}

tonos_pasteles = [
    "#B5EAD7", "#E2BEF1", "#A8D8EA", "#FBC5A2",
    "#C7CEEA", "#FFEAA7", "#FFB6B9"
]

todas_categorias = sorted(set(
    valor for var in vars_predictoras for valor in df[var].unique()
))

colores_personalizados = {
    cat: tonos_pasteles[i % len(tonos_pasteles)]
    for i, cat in enumerate(todas_categorias)
}


def cramers_v(x, y):
    confusion = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion)[0]
    n = confusion.sum().sum()
    r, c = confusion.shape
    return np.sqrt(chi2 / (n * (min(r, c) - 1)))


def figura_dona_target():
    tabla = df["class"].value_counts().reset_index()
    tabla.columns = ["class", "Frecuencia"]
    tabla["Porcentaje"] = round(tabla["Frecuencia"] / tabla["Frecuencia"].sum() * 100, 1)

    fig = px.bar(
        tabla, x="class", y="Frecuencia", color="class",
        color_discrete_map=COLORES_CLASS,
        title="Distribución de la variable target",
        labels={"class": "Clase", "Frecuencia": "Frecuencia"},
        template="plotly_white",
        custom_data=["Porcentaje"],
    )
    fig.update_traces(
        hovertemplate="Frecuencia: %{y}<br>Porcentaje: %{customdata[0]}%<extra></extra>"
    )
    fig.update_layout(
        height=450, width=None, showlegend=False,
        yaxis=dict(range=[0, tabla["Frecuencia"].max() * 1.15]),
    )
    return fig


def figura_donas_variables():
    n_cols = 2
    n_filas = -(-len(vars_predictoras) // n_cols)

    fig = make_subplots(
        rows=n_filas, cols=n_cols,
        specs=[[{"type": "pie"} for _ in range(n_cols)] for _ in range(n_filas)],
        subplot_titles=vars_predictoras,
        vertical_spacing=0.005,
        horizontal_spacing=0.02,
    )

    row = 1
    col = 1

    for var in vars_predictoras:
        tabla = df[var].value_counts().reset_index()
        tabla.columns = ["valor", "n"]
        colores_usar = [colores_personalizados.get(v, "#999999") for v in tabla["valor"]]

        fig.add_trace(
            go.Pie(
                labels=tabla["valor"],
                values=tabla["n"],
                text=tabla["valor"],
                textposition="inside",
                textinfo="text",
                textfont=dict(size=16),
                marker=dict(colors=colores_usar),
                hovertemplate="Frecuencia: %{value}<br>Porcentaje: %{percent}<extra></extra>",
                showlegend=False,
                sort=False,
                direction="clockwise",
                hole=0,
                domain=dict(x=[0, 1], y=[0, 1]),
            ),
            row=row, col=col,
        )

        col += 1
        if col > n_cols:
            col = 1
            row += 1

    fig.update_layout(
        height=350 * n_filas,
        showlegend=False,
        font=dict(size=14),
        margin=dict(l=20, r=20, t=80, b=20),
        hoverlabel=dict(font=dict(size=16)),
    )

    for ann in fig.layout.annotations:
        ann.font.size = 16
        ann.font.color = "black"
        ann.xanchor = "center"

    return fig


def figura_heatmap_class():
    vars_todas = df.columns.tolist()
    n_vars = len(vars_todas)
    mat = np.zeros((n_vars, n_vars))

    for i, v1 in enumerate(vars_todas):
        for j, v2 in enumerate(vars_todas):
            mat[i, j] = cramers_v(df[v1], df[v2])

    fig = go.Figure(data=go.Heatmap(
        z=mat,
        x=vars_todas,
        y=vars_todas,
        colorscale="Blues",
        zmin=0, zmax=1,
        text=np.round(mat, 2),
        texttemplate="%{text:.2f}",
        textfont={"size": 8},
        hoverongaps=False,
        hovertemplate="<b>%{y}</b> ↔ <b>%{x}</b><br>Cramér's V: %{z:.3f}<extra></extra>",
    ))
    fig.update_layout(
        title="Matriz Cramér's V — KRKPA7",
        height=700,
        xaxis=dict(tickangle=90, tickfont=dict(size=8)),
        yaxis=dict(tickfont=dict(size=8)),
        margin=dict(l=50, r=50, t=80, b=120),
    )
    return fig


def figura_top5_class():
    vars_todas = df.columns.tolist()
    asoc = pd.Series({
        v: cramers_v(df[v], df["class"]) for v in vars_todas if v != "class"
    }).sort_values(ascending=False)

    top5 = asoc.head(5).reset_index()
    top5.columns = ["Variable", "cramer"]

    fig = px.bar(
        top5, x="cramer", y="Variable", orientation="h",
        color="cramer",
        color_continuous_scale=[[0.0, "#A8D8EA"], [1.0, "#0D3B66"]],
        text=top5["cramer"].apply(lambda x: f"{x:.3f}"),
        title="Top 5 variables más relacionadas con class",
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=13, color="black"),
        hovertemplate="<b>%{y}</b><br>Cramér's V: %{x:.3f}<extra></extra>",
    )
    fig.update_layout(
        height=400, showlegend=False,
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(range=[0, 0.5], title="Cramér's V", tickformat=".3f",
                   gridcolor="#E5E5E5", zerolinecolor="#E5E5E5"),
        yaxis=dict(title="", autorange="reversed", gridcolor="#E5E5E5"),
        coloraxis_colorbar=dict(title="Cramér's V", tickfont=dict(size=11)),
        margin=dict(l=10, r=40, t=60, b=40),
    )
    return fig


def figura_barras_por_clase():
    n_cols = 2
    n_filas = -(-len(vars_predictoras) // n_cols)

    fig = make_subplots(
        rows=n_filas, cols=n_cols,
        subplot_titles=vars_predictoras,
        vertical_spacing=0.03,
        horizontal_spacing=0.08,
    )

    row = 1
    col = 1

    for var in vars_predictoras:
        df_plot = df.groupby(["class", var]).size().reset_index(name="n")
        df_plot["porcentaje"] = df_plot.groupby("class")["n"].transform(
            lambda x: round(x / x.sum() * 100, 1)
        )

        categorias = sorted(df[var].unique())
        n_cats = len(categorias)
        posiciones = list(range(n_cats))
        ancho_total = 0.7
        ancho_barra = ancho_total / 2

        for i_clase, clase in enumerate(["won", "nowin"]):
            sub = df_plot[df_plot["class"] == clase].set_index(var)
            y_vals = [sub["n"].get(cat, 0) for cat in categorias]
            pct_vals = [sub["porcentaje"].get(cat, 0) for cat in categorias]

            x_vals = [
                p - ancho_total / 2 + ancho_barra / 2 + i_clase * ancho_barra
                for p in posiciones
            ]

            customdata = list(zip([clase] * n_cats, categorias, y_vals, pct_vals))

            fig.add_trace(
                go.Bar(
                    x=x_vals, y=y_vals, name=clase,
                    marker_color=COLORES_CLASS[clase],
                    legendgroup=clase,
                    showlegend=(row == 1 and col == 1),
                    customdata=customdata,
                    width=ancho_barra * 0.95,
                    hovertemplate="Frecuencia: %{customdata[2]}<br>Porcentaje: %{customdata[3]}%<extra></extra>",
                ),
                row=row, col=col,
            )

        fig.update_xaxes(
            title_text="", tickmode="array",
            tickvals=posiciones, ticktext=categorias,
            range=[-0.5, n_cats - 0.5],
            row=row, col=col, tickfont=dict(size=10),
        )
        fig.update_yaxes(title_text="", row=row, col=col, tickfont=dict(size=9))

        col += 1
        if col > n_cols:
            col = 1
            row += 1

    fig.update_layout(
        title=dict(
            text="Distribución de variables por clase",
            x=0.5, xanchor="center", y=0.995, yanchor="top",
            font=dict(size=22),
        ),
        barmode="overlay",
        height=400 * n_filas,
        legend=dict(
            orientation="h", yanchor="top", y=0.989,
            xanchor="center", x=0.5,
            xref="container", yref="container",
            title=None, font=dict(size=16),
        ),
        margin=dict(l=40, r=40, t=150, b=40),
        hoverlabel=dict(font=dict(size=14)),
    )

    for ann in fig.layout.annotations:
        ann.font.size = 12
        ann.font.color = "black"
        ann.xanchor = "center"

    return fig


def figura_heatmap_predictoras():
    n_pred = len(vars_predictoras)
    mat = np.zeros((n_pred, n_pred))

    for i, v1 in enumerate(vars_predictoras):
        for j, v2 in enumerate(vars_predictoras):
            mat[i, j] = cramers_v(df[v1], df[v2])

    fig = go.Figure(data=go.Heatmap(
        z=mat,
        x=vars_predictoras,
        y=vars_predictoras,
        colorscale="Blues",
        zmin=0, zmax=1,
        text=np.round(mat, 2),
        texttemplate="%{text:.2f}",
        textfont={"size": 7},
        hoverongaps=False,
        hovertemplate="<b>%{y}</b> ↔ <b>%{x}</b><br>Cramér's V: %{z:.3f}<extra></extra>",
    ))
    fig.update_layout(
        title="Relación entre variables predictoras (Cramér's V)",
        height=600,
        xaxis=dict(tickangle=90, tickfont=dict(size=7)),
        yaxis=dict(tickfont=dict(size=7)),
        margin=dict(l=50, r=50, t=80, b=120),
    )
    return fig


def figura_top5_pares():
    n_pred = len(vars_predictoras)
    pares = []
    for i in range(n_pred):
        for j in range(i + 1, n_pred):
            pares.append({
                "var1": vars_predictoras[i],
                "var2": vars_predictoras[j],
                "cramer": cramers_v(df[vars_predictoras[i]], df[vars_predictoras[j]]),
            })
    pares = pd.DataFrame(pares).sort_values("cramer", ascending=False).head(5)
    pares["par"] = pares["var1"] + " ↔ " + pares["var2"]

    fig = px.bar(
        pares, x="cramer", y="par", orientation="h",
        color="cramer",
        color_continuous_scale=[[0.0, "#D1F2FD"], [1.0, "#0D3B66"]],
        text=pares["cramer"].apply(lambda x: f"{x:.3f}"),
        title="Top 5 pares de variables predictoras con mayor relación",
        labels={"cramer": "Cramér's V", "par": ""},
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=12, color="black"),
        hovertemplate="%{y}<br>Cramér's V: %{x:.3f}<extra></extra>",
    )
    fig.update_layout(
        height=400, showlegend=False,
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(range=[0, 0.75], title="Cramér's V",
                   gridcolor="#E5E5E5", zerolinecolor="#E5E5E5"),
        yaxis=dict(title="", autorange="reversed", gridcolor="#E5E5E5"),
        coloraxis_colorbar=dict(title="Cramér's V", tickfont=dict(size=11)),
        margin=dict(l=10, r=40, t=60, b=40),
    )
    return fig


def tabla_contingencia_completa():
    filas = []
    for var in vars_predictoras:
        for class_val in df["class"].unique():
            for cat in df[var].unique():
                n = ((df["class"] == class_val) & (df[var] == cat)).sum()
                if n > 0:
                    total_class = (df["class"] == class_val).sum()
                    pct = round((n / total_class) * 100, 1)
                    filas.append({
                        "Class": class_val,
                        "Variable": var,
                        "Categoria": cat,
                        "Frecuencia": n,
                        "Porcentaje": pct,
                    })
    tabla = pd.DataFrame(filas).sort_values(["Variable", "Class"]).reset_index(drop=True)
    tabla.index = tabla.index + 1
    return tabla


def layout():
    
    fig_target = figura_dona_target()
    fig_donas = figura_donas_variables()
    fig_heat_class = figura_heatmap_class()
    fig_top5_class = figura_top5_class()
    fig_barras = figura_barras_por_clase()
    fig_heat_pred = figura_heatmap_predictoras()
    fig_top5_pares = figura_top5_pares()
    tabla_cont = tabla_contingencia_completa()

    return dbc.Container([

        html.H2("EDA — KRKPA7"),
        html.H3("Análisis de la variable target class"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig_target))), md=6),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.P(
                    "En 1669 partidas, el 52.2%, resultó won, es decir que las "
                    "blancas ganaron, y en 1527 partidas, el 47.8%, resultó nowin. "
                    "La diferencia entre ambas clases es de solo 4.4 puntos "
                    "porcentuales, lo que indica que el dataset no tiene un sesgo "
                    "significativo hacia ninguna clase."
                ),
            ])), md=6),
        ], className="g-3 mb-4"),

        html.H3("Análisis de las variables independientes"),

        dbc.Card(dbc.CardBody([
            html.H5("Distribución de cada variable predictora", className="card-title"),
            dcc.Graph(figure=fig_donas, config={"displayModeBar": False}),
            html.P(
                "whxbp: la torre blanca ataca al peón negro en el 38% de las "
                "posiciones. wxqsq: las blancas controlan la casilla de coronación "
                "(a8) en el 30.4% de las posiciones. cntxt: el rey negro está en el "
                "borde del tablero en el 43.1% de las posiciones, lo que lo hace más "
                "vulnerable a clavadas."
            ),
            html.P(
                "Tácticas avanzadas como el jaque oculto (hdchk, 0.5%), la "
                "re-clavada diferida (reskd, 0.8%), la oposición especial (spcop, 0%) "
                "y la clavada tras jaques (skach, 0.3%) son muy raras. Sin embargo, "
                "la posibilidad de una clavada (skewer) está presente en el 30.7% de "
                "las posiciones (skewr), lo que la convierte en una amenaza real."
            ),
            html.P(
                "Variables del rey blanco (wk...): el rey blanco rara vez bloquea a "
                "su propia torre (wkblk: 88.8% falso) o se encuentra en a8 "
                "(wkna8: 96.2% falso). En un 36.6% de posiciones el rey blanco puede "
                "atacar la casilla crítica b7 (wkxcr)."
            ),
            html.P(
                "Variables del rey negro (bk...): está bajo presión en un porcentaje "
                "significativo de posiciones, en el 37.9% está en jaque (bknck), en "
                "el 37.2% está sobrecargado (bkovl) y en el 26.6% está en posición "
                "de posible clavada (bkpos)."
            ),
        ]), className="mb-4"),

        html.H3("Análisis bivariado class vs independientes"),

        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Matriz de asociación con class", className="card-title"),
            dcc.Graph(figure=fig_heat_class, config={"displayModeBar": False}),
            html.P(
                "El heatmap muestra la fuerza de la relación entre las variables "
                "predictoras y la variable objetivo class. Los valores más altos "
                "(azul oscuro) indican una relación más fuerte con el resultado del "
                "final de ajedrez. Los valores más bajos (blanco) sugieren que la "
                "variable es prácticamente independiente de si la posición es "
                "ganable o no."
            ),
        ]))), className="mb-4"),

        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Top 5 variables más relacionadas con class", className="card-title"),
            dcc.Graph(figure=fig_top5_class, config={"displayModeBar": False}),
            html.Ul([
                html.Li("rimmx (0.45): captura segura de la torre blanca. Si la torre blanca puede ser capturada de forma segura por las negras, las blancas pierden su principal ventaja."),
                html.Li("wxqsq (0.38): control blanco de la casilla de coronación (a8)."),
                html.Li("bknck (0.365): rey negro en jaque."),
                html.Li("wkxbp (0.233): rey blanco captura el peón negro."),
                html.Li("katri (0.22): control del punto de intersección."),
            ]),
        ]))), className="mb-4"),

        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Tabla de contingencia: class vs variables predictoras", className="card-title"),
            dash_table.DataTable(
                data=tabla_cont.to_dict("records"),
                columns=[{"name": c, "id": c} for c in tabla_cont.columns],
                style_table={"overflowX": "auto", "maxHeight": "500px", "overflowY": "auto"},
                style_cell={"textAlign": "left", "padding": "6px", "fontSize": "12px"},
                style_header={"fontWeight": "bold", "backgroundColor": "#F2E9E4"},
                page_size=20,
                sort_action="native",
                filter_action="native",
            ),
        ]))), className="mb-4"),

        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Distribución de variables por clase", className="card-title"),
            dcc.Graph(figure=fig_barras, config={"displayModeBar": False}),
            html.H6("Factores relacionados con la victoria (won)", className="mt-3"),
            html.Ul([
                html.Li("katri = w: la proporción de won (20.9%) es más del triple que en nowin (6.4%)."),
                html.Li("rkxwp = t: 23.9% won vs 15.8% nowin."),
                html.Li("bkpos = t: ligeramente más común en won (79.6%) que en nowin (66.6%)."),
            ]),
            html.H6("Factores relacionados con la no victoria (nowin)"),
            html.Ul([
                html.Li("rimmx = f: se da el 100% de los casos de nowin."),
                html.Li("bkna8 = t: 5 veces más frecuente en nowin (10.2%) que en won (1.2%)."),
                html.Li("bknck = t: 2.7 veces más frecuente en nowin (56.5%) que en won (21.0%)."),
                html.Li("wkxbp = t: 2.5 veces más frecuente en nowin (31.8%) que en won (12.6%)."),
                html.Li("wxqsq = t: 3.5 veces más frecuente en nowin (48.7%) que en won (13.7%)."),
            ]),
            html.H6("Variables con poca diferencia"),
            html.P(
                "wkblk, wknwy, dsopp, qxmsq, reskd, reskr y btoeg presentan "
                "distribuciones muy similares entre won y nowin, lo que indica que "
                "podrían no ser útiles para predecir el resultado."
            ),
        ]))), className="mb-4"),

        html.H3("Relaciones entre variables predictoras"),

        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Matriz de asociación entre predictoras", className="card-title"),
            dcc.Graph(figure=fig_heat_pred, config={"displayModeBar": False}),
        ]))), className="mb-4"),

        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Top 5 pares de predictoras con mayor relación", className="card-title"),
            dcc.Graph(figure=fig_top5_pares, config={"displayModeBar": False}),
            html.Ul([
                html.Li("whxbp ↔ wkxbp (0.67): captura del peón negro por la torre blanca vs por el rey blanco."),
                html.Li("rkxwp ↔ whxbp (0.639): amenaza de la torre blanca sobre el peón vs ataque de la torre."),
                html.Li("bkovl ↔ r2ar8 (0.591): rey negro sobrecargado vs acceso de la torre a columna A o fila 8."),
                html.Li("cntxt ↔ skewr (0.579): rey negro en el borde vs posibilidad de clavada."),
                html.Li("wkxbp ↔ wkxcr (0.564): captura del peón vs ataque a b7 por parte del rey blanco."),
            ]),
            html.P(
                "Ninguno de estos valores supera 0.7, lo que indica que no hay "
                "variables altamente redundantes. Sin embargo, las relaciones "
                "moderadas (0.5 – 0.67) sugieren que algunos pares de variables "
                "miden conceptos relacionados desde diferentes perspectivas."
            ),
        ]))), className="mb-4"),

        html.H3("Conclusiones"),
        dbc.Card(dbc.CardBody([
            html.Ol([
                html.Li("La variable objetivo class presenta una distribución prácticamente balanceada (52.2% won, 47.8% nowin)."),
                html.Li("La mayoría de las variables predictoras son binarias (t/f), con excepción de dwipd (g/l), btoeg (n, t) y katri (única ternaria: n/b/w)."),
                html.Li("Tácticas avanzadas como hdchk (0.5%), reskd (0.8%), skach (0.3%) y spcop (0%) son muy raras."),
                html.Li("La variable más determinante es rimmx (V = 0.45): cuando la torre blanca no puede ser capturada de forma segura (rimmx = f), se da el 100% de los casos de nowin."),
                html.Li("Otras variables con alta relación: wxqsq (0.38) y bknck (0.365)."),
                html.Li("No hay variables altamente redundantes (ninguna supera 0.7 de Cramér's V)."),
                html.Li("El resultado del final depende de la combinación de múltiples factores: seguridad de la torre (rimmx), control del punto de intersección (katri) y posición del rey negro (bkna8, bknck)."),
            ]),
        ])),

    ], fluid=True)