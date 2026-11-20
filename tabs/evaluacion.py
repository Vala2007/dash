"""Evaluación del modelo: las tablas y gráficas del Jupyter Book dentro del Dash.

Los números salen de models/resultados_modelado.json (lo genera la última celda del
notebook de modelado: notebook/celda_exportar_resultados.py).
"""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc

from components import colapsable

RUTA = Path(__file__).resolve().parent.parent / "models" / "resultados_modelado.json"
COLOR_WON, COLOR_NOWIN = "#008080", "#40B5A0"


@lru_cache(maxsize=1)
def cargar_resultados():
    try:
        return json.loads(RUTA.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[evaluacion] No se pudo leer {RUTA}: {type(e).__name__}: {e}")
        return None


# ------------------------------------------------------------------ utilidades
def _tabla(filas, columnas):
    """filas: lista de dicts ya formateados; columnas: lista de nombres (en orden)."""
    return dash_table.DataTable(
        data=filas,
        columns=[{"name": c, "id": c} for c in columnas],
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left", "padding": "10px 12px", "fontSize": "13px",
            "whiteSpace": "normal", "height": "auto",
            "fontFamily": "Inter, Segoe UI, sans-serif",
            "backgroundColor": "transparent", "color": "inherit",
            "border": "1px solid rgba(0, 0, 0, 0.06)",
        },
        page_size=20,
    )


def _tarjeta(*hijos):
    return dbc.Card(dbc.CardBody(list(hijos)), className="mb-3")


def _p(texto):
    return html.P(texto)


# ---------------------------------------------------------------------- gráficas
def fig_cv_f1(cv):
    orden = [m["Modelo"] for m in cv][::-1]          # el mejor queda arriba
    por_nombre = {m["Modelo"]: m for m in cv}
    rng = np.random.default_rng(42)
    fig = go.Figure()
    for i, nombre in enumerate(orden):
        v = np.array(por_nombre[nombre]["f1_folds"], dtype=float)
        fig.add_trace(go.Scatter(
            x=v, y=i + rng.uniform(-.15, .15, len(v)), mode="markers", showlegend=False,
            marker=dict(color=COLOR_NOWIN, size=8, opacity=.6),
            hovertemplate="F1: %{x:.4f}<extra>" + nombre + "</extra>",
        ))
        fig.add_trace(go.Scatter(
            x=[float(v.mean())], y=[i], mode="markers", showlegend=False,
            marker=dict(symbol="diamond", size=13, color=COLOR_WON, line=dict(color="white", width=1)),
            hovertemplate="Media: %{x:.4f}<extra>" + nombre + "</extra>",
        ))
    fig.update_yaxes(tickmode="array", tickvals=list(range(len(orden))), ticktext=orden)
    fig.update_xaxes(title="F1 de la clase won (validación cruzada)")
    fig.update_layout(title="Desempeño por modelo (◆ = media; cada punto = una partición)")
    return fig


def fig_confusion(conf):
    z = conf["matriz"]
    etiquetas = conf["labels"]
    fig = go.Figure(go.Heatmap(
        z=z, x=etiquetas, y=etiquetas, text=z, texttemplate="%{text}", textfont=dict(size=22),
        colorscale=[[0, "#F0FFFF"], [1, COLOR_WON]], showscale=False,
        hovertemplate="Real: %{y}<br>Predicho: %{x}<br>Posiciones: %{z}<extra></extra>",
    ))
    fig.update_xaxes(title="Clase predicha")
    fig.update_yaxes(title="Clase real", autorange="reversed")
    fig.update_layout(title="Matriz de confusión (prueba)")
    return fig


def fig_roc(roc):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=roc["fpr"], y=roc["tpr"], mode="lines", line=dict(color=COLOR_WON, width=3),
        name=f"AUC = {roc['auc']:.3f}",
        hovertemplate="FPR: %{x:.3f}<br>TPR: %{y:.3f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines", line=dict(color="grey", dash="dash"),
        name="Azar", hoverinfo="skip",
    ))
    fig.update_xaxes(title="Tasa de falsos positivos", range=[-0.02, 1.02])
    fig.update_yaxes(title="Tasa de verdaderos positivos", range=[-0.02, 1.05])
    fig.update_layout(title="Curva ROC (prueba)", legend=dict(x=0.98, y=0.05, xanchor="right"))
    return fig


def fig_permutacion(perm):
    variables = [p["variable"] for p in perm]
    fig = go.Figure(go.Bar(
        x=[p["media"] for p in perm], y=variables, orientation="h", marker_color=COLOR_WON,
        error_x=dict(type="data", array=[p["sd"] for p in perm], color="grey", thickness=1.5),
        hovertemplate="<b>%{y}</b><br>Caída del F1: %{x:.3f}<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(title="Caída del F1 al permutar la variable")
    fig.update_layout(title="Importancia por permutación (top 10)")
    return fig


def fig_estabilidad(est):
    acc = est["accuracy"]
    fig = go.Figure(go.Histogram(x=acc, nbinsx=8, marker=dict(color=COLOR_NOWIN, line=dict(color="white", width=1)),
                                 hovertemplate="Accuracy: %{x}<br>Particiones: %{y}<extra></extra>"))
    fig.add_vline(x=float(np.mean(acc)), line_color=COLOR_WON, line_width=3)
    fig.update_xaxes(title="Accuracy de prueba")
    fig.update_yaxes(title="Particiones")
    fig.update_layout(title="Variación de la exactitud con 10 particiones (línea = media)")
    return fig


# ------------------------------------------------------------------- bloques
def _bloque_comparacion(r):
    filas = [{"Modelo": m["Modelo"], "Accuracy": f"{m['Accuracy']:.4f}", "F1-Score": f"{m['F1']:.4f}"}
             for m in r["comparacion_prueba"]]
    return colapsable("1. Comparación preliminar de los cuatro modelos", [
        _tarjeta(
            _p("Los cuatro candidatos se entrenan con el 80 % de las posiciones (One-Hot dentro del Pipeline, "
               "hiperparámetros por defecto) y se evalúan en el 20 % de prueba (640 posiciones)."),
            _tabla(filas, ["Modelo", "Accuracy", "F1-Score"]),
            _p("CatBoost obtiene el mejor resultado (Accuracy = 0.9953, F1 = 0.9955), seguido del Árbol de Decisión, "
               "Random Forest y la Regresión Logística. La diferencia entre CatBoost y el árbol equivale a una sola "
               "posición de las 640, por lo que no es concluyente; la brecha con la regresión logística "
               "(≈ 3.4 puntos de exactitud) sí es amplia."),
        ),
    ])


def _bloque_cv(r):
    cv = r["cv"]
    filas = [{
        "Modelo": m["Modelo"],
        "Accuracy": f"{m['acc'][0]:.4f} ± {m['acc'][1]:.4f}",
        "F1 (won)": f"{m['f1'][0]:.4f} ± {m['f1'][1]:.4f}",
        "AUC-ROC": f"{m['auc'][0]:.4f} ± {m['auc'][1]:.4f}",
        "Brecha train − val (acc)": f"{m['brecha']:.4f}",
    } for m in cv]
    return colapsable("2. Validación cruzada (15 evaluaciones por modelo)", [
        _tarjeta(
            _p("Para que la elección no dependa de una sola partición, cada modelo se evalúa 15 veces "
               "(validación cruzada estratificada de 5 particiones × 3 repeticiones) usando solo el 80 % de "
               "entrenamiento. Se añade una línea base que siempre predice la clase mayoritaria."),
            _tabla(filas, ["Modelo", "Accuracy", "F1 (won)", "AUC-ROC", "Brecha train − val (acc)"]),
        ),
        _tarjeta(
            dcc.Graph(figure=_figura_lista(fig_cv_f1(cv), 380), config={"displayModeBar": False}),
            _p("CatBoost vuelve a obtener el mayor F1 medio (0.9916 ± 0.0030) y el AUC-ROC más alto y estable "
               "(0.9995). La línea base queda en una exactitud de 0.522 y un AUC de 0.5, de modo que los cuatro "
               "modelos capturan señal real. Las brechas entre entrenamiento y validación son pequeñas "
               "(entre 0.004 y 0.011): no hay sobreajuste preocupante. Los tres modelos basados en árboles se "
               "solapan casi por completo y la regresión logística queda claramente por debajo."),
        ),
    ])


def _bloque_wilcoxon(r):
    filas = [{
        "Modelo": w["Modelo"],
        "Dif. media de F1 (CatBoost − modelo)": f"{w['dif']:.4f}",
        "% de particiones donde CatBoost gana o empata": f"{w['gana']:.1f}",
        "p (Wilcoxon)": f"{w['p']:.4f}",
    } for w in r["wilcoxon"]]
    return colapsable("3. ¿Las diferencias entre modelos son reales o ruido?", [
        _tarjeta(
            _p("Como todos los modelos se evalúan sobre las mismas 15 particiones, se compara el F1 de CatBoost "
               "con el de cada otro modelo partición por partición (prueba de rangos con signo de Wilcoxon)."),
            _tabla(filas, ["Modelo", "Dif. media de F1 (CatBoost − modelo)",
                           "% de particiones donde CatBoost gana o empata", "p (Wilcoxon)"]),
            _p("CatBoost supera de forma significativa a la Regresión Logística (p = 0.0001) y, con un margen "
               "mínimo, a Random Forest (p = 0.048). No se distingue del Árbol de Decisión (p = 0.85). Como las "
               "particiones comparten datos, los p-valores son algo optimistas y la ventaja sobre Random Forest "
               "debe tomarse como marginal. Lo importante: la regresión logística, que suma efectos "
               "independientes, queda ≈ 3 puntos de F1 por debajo; los modelos de árboles pueden representar "
               "combinaciones de condiciones tácticas. Se selecciona CatBoost por el F1 medio más alto, la menor "
               "variabilidad y el mejor AUC (útil porque el dashboard muestra probabilidades)."),
        ),
    ])


def _bloque_test(r):
    m = r["metricas_test"]
    filas = [{
        "Modelo": "CatBoost (prueba)", "Accuracy": f"{m['Accuracy']:.4f}", "Precisión": f"{m['Precisión']:.4f}",
        "Recall": f"{m['Recall']:.4f}", "F1": f"{m['F1']:.4f}", "AUC-ROC": f"{m['AUC-ROC']:.4f}",
    }]
    return colapsable("4. Modelo final en el conjunto de prueba", [
        _tarjeta(
            _tabla(filas, ["Modelo", "Accuracy", "Precisión", "Recall", "F1", "AUC-ROC"]),
        ),
        dbc.Row([
            dbc.Col(_tarjeta(dcc.Graph(figure=_figura_lista(fig_confusion(r["confusion"]), 400),
                                       config={"displayModeBar": False})), md=6),
            dbc.Col(_tarjeta(dcc.Graph(figure=_figura_lista(fig_roc(r["roc"]), 400),
                                       config={"displayModeBar": False})), md=6),
        ]),
        _tarjeta(
            _p("En las 640 posiciones de prueba el modelo acierta 637 y falla 3 (exactitud = 0.9953): un falso "
               "won (una posición nowin que predice como victoria del peón) y dos falsos nowin. La precisión de "
               "won es 0.9970, el recall 0.9940 y el AUC-ROC es prácticamente 1. Con un conjunto de prueba tan "
               "pequeño, una posición de diferencia mueve la exactitud 0.0016; por eso conviene leerlo junto con "
               "el intervalo de confianza del 95 % de la sección «Modelo final»."),
        ),
    ])


def _bloque_permutacion(r):
    t5 = r["top5"]
    filas = [{"#": str(i + 1), "Top 5 V de Cramér (EDA)": a, "Top 5 permutación (modelo)": b}
             for i, (a, b) in enumerate(zip(t5["cramer"], t5["permutacion"]))]
    return colapsable("5. Interpretabilidad: ¿qué variables usa el modelo?", [
        _tarjeta(
            _p("La importancia por permutación mide cuánto cae el F1 en la prueba al barajar al azar los valores de "
               "una variable: si el modelo depende de ella, el desempeño empeora."),
            dcc.Graph(figure=_figura_lista(fig_permutacion(r["permutacion"]), 420),
                      config={"displayModeBar": False}),
            _p("Tres variables concentran casi toda la importancia: bknck (≈ 0.195), rimmx (≈ 0.185) y "
               "wxqsq (≈ 0.168). Les siguen, muy por debajo, bkpos, katri y wkxbq (≈ 0.02–0.04)."),
        ),
        _tarjeta(
            html.H5("¿Coincide con lo que mostró el EDA?", className="card-title"),
            _tabla(filas, ["#", "Top 5 V de Cramér (EDA)", "Top 5 permutación (modelo)"]),
            _p("Cuatro de las cinco variables principales (rimmx, wxqsq, bknck y katri) coinciden con las de mayor "
               "V de Cramér del EDA. La diferencia es que el modelo usa bkpos en lugar de wkxbp: wkxbp comparte "
               "información con whxbp y wkxcr (V de 0.67 y 0.56), así que el modelo puede apoyarse en cualquiera "
               "de ellas. La permutación mide cuánto depende el modelo de una variable, no en qué dirección empuja; "
               "esa lectura sigue siendo la del EDA (rimmx = t solo aparece en posiciones won)."),
        ),
    ])


def _bloque_estabilidad(r):
    e = r["estabilidad"]
    def resumen(v):
        v = np.array(v, dtype=float)
        return v.mean(), v.std(ddof=1), v.min(), v.max()
    a, f = resumen(e["accuracy"]), resumen(e["f1"])
    filas = [{"": nombre, "accuracy": f"{a[i]:.4f}", "f1": f"{f[i]:.4f}"}
             for i, nombre in enumerate(["mean", "std", "min", "max"])]
    return colapsable("6. Estabilidad ante distintas particiones", [
        _tarjeta(
            _p("La exactitud de prueba depende de qué 20 % de las posiciones cayó en la prueba. Para ver cuánto "
               "varía, se repite la partición con 10 semillas distintas, reentrenando el pipeline cada vez."),
            dcc.Graph(figure=_figura_lista(fig_estabilidad(e), 330), config={"displayModeBar": False}),
            _tabla(filas, ["", "accuracy", "f1"]),
            _p(f"Con 10 particiones distintas la exactitud media fue {a[0]:.4f} (desviación {a[1]:.4f}), con valores "
               f"entre {a[2]:.4f} y {a[3]:.4f}. Coincide con la validación cruzada (≈ 0.991) y muestra que el "
               "0.9953 de la partición original está en el extremo alto del rango: el desempeño esperado del "
               "modelo es de ≈ 99.1 %."),
        ),
    ])


def _bloque_conclusiones():
    return colapsable("7. Conclusiones y limitaciones", [
        _tarjeta(
            html.Ul([
                html.Li("CatBoost obtuvo el F1 medio más alto en validación cruzada (0.9916 ± 0.0030) y el mejor "
                        "AUC-ROC (0.9995). Supera de forma significativa a la regresión logística y, "
                        "marginalmente, a Random Forest; no se distingue del Árbol de Decisión."),
                html.Li("En prueba: Accuracy = 0.9953, F1 = 0.9955 y AUC-ROC ≈ 1, con 3 errores en 640 posiciones."),
                html.Li("Con 10 particiones distintas la exactitud media es 0.9914: el desempeño esperado es ≈ 99.1 %."),
                html.Li("Las variables que más pesan son bknck, rimmx y wxqsq, coherentes con el EDA."),
            ]),
            html.H5("Limitaciones", className="mt-3"),
            html.Ul([
                html.Li("Las diferencias entre CatBoost y los otros modelos de árboles son pequeñas y no se "
                        "ajustaron hiperparámetros."),
                html.Li("Las variables fueron diseñadas por Shapiro como predicados de conocimiento experto sobre el "
                        "final; no son mediciones libres de partidas reales. Esto explica la alta separabilidad de "
                        "las clases: el resultado describe qué tan bien se aprende esa codificación experta y no "
                        "debe extrapolarse a partidas reales."),
                html.Li("Se usan los colores de UCI (peón negro, torre blanca) y se lee won como «gana el bando del "
                        "peón», porque es lo que indican los datos (todas las posiciones nowin tienen rimmx = f). "
                        "Esto afecta la interpretación de las variables, no el desempeño del modelo."),
            ]),
        ),
    ])


def _figura_lista(fig, alto):
    """Aplica el estilo común (fondo transparente, márgenes, altura) a una figura."""
    fig.update_layout(
        height=alto, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=20, t=50, b=40), font=dict(family="Inter, sans-serif"),
    )
    return fig


# ------------------------------------------------------------------- sección
def seccion_evaluacion():
    r = cargar_resultados()
    if r is None:
        return html.Div([
            html.H2("Evaluación del modelo"),
            dbc.Alert([
                html.B("Falta el archivo de resultados. "),
                "Ejecuta la última celda del notebook (", html.Code("celda_exportar_resultados.py"),
                ") y copia ", html.Code("resultados_modelado.json"), " a la carpeta ", html.Code("models/"), ".",
            ], color="warning"),
        ], className="krk-section")

    return html.Div([
        html.H2("Evaluación del modelo"),
        html.P(
            "Cómo se eligió CatBoost: se separa un 20 % de las posiciones como prueba (estratificado, "
            "random_state = 42); la codificación One-Hot va dentro del Pipeline para que la prueba no influya en "
            "el entrenamiento; los cuatro candidatos se comparan en la prueba y la decisión se confirma con "
            "validación cruzada repetida, una línea base y pruebas de Wilcoxon. Cada bloque se despliega con un clic."
        ),
        _bloque_comparacion(r),
        _bloque_cv(r),
        _bloque_wilcoxon(r),
        _bloque_test(r),
        _bloque_permutacion(r),
        _bloque_estabilidad(r),
        _bloque_conclusiones(),
    ], className="krk-section")