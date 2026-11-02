from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from components import stat_card, seccion

VARIABLES_DATA = {
    "Variable": [
        "wkblk", "wknwy", "wkna8", "wkon8", "wkspr", "wkxbq", "wkxcr", "wkxbp",
        "whxbp", "wxqsq", "cntxt", "dsopp", "dwipd", "hdchk", "katri", "mulch",
        "qxmsq", "r2ar8", "reskd", "reskr", "rimmx", "rkxwp", "rxmsq", "simpl",
        "skach", "skewr", "skrxp", "spcop", "stlmt", "thrsk", "bkcti", "bkna8",
        "bknck", "bkovl", "bkpos", "btoeg",
    ],
    "Nombre real": [
        "White King in the way", "White King No Way", "White King on a8",
        "White King on a", "White King Support Rook",
        "Black King attacked by promoted Pawn",
        "White King attack Critical square", "White King captures Black Pawn",
        "White attack Black Pawn", "White control Queen Square",
        "Context (edge)", "Diagonal Opposite", "Distance to intersect point",
        "Hidden Check", "King Attack Three", "Multiple Checks", "Queen Square",
        "Rook to A or Rank 8", "Reskewer Delayed", "Reskewer", "Rook in Middle",
        "Rook captures Pawn", "Rook attacks mating square", "Simple pattern",
        "Skewer after Checks", "Skewer", "Skewer or attack Pawn",
        "Special Opposition", "Stalemate", "Threat Skewer",
        "Black King Control The Intersect", "Black King on a8",
        "Black King Check", "Black King Overloaded",
        "Black King Position (potential skewer)", "Black to Egress",
    ],
    "Significado": [
        "El rey blanco obstruye el camino de la torre blanca (bloquea su movimiento).",
        "El rey blanco está en la columna 'a' o en el borde, limitando el movimiento de la torre.",
        "El rey blanco está en la casilla a8.",
        "El rey blanco está en la columna 'a'.",
        "El rey blanco puede apoyar a la torre blanca en una horquilla (fork).",
        "El rey blanco está siendo atacado por el peón promocionado.",
        "El rey blanco ataca la casilla crítica (normalmente b7).",
        "El rey blanco captura el peón negro.",
        "La torre blanca ataca al peón negro.",
        "Las blancas controlan la casilla de la dama (a8, casilla de coronación).",
        "El rey negro está en un borde del tablero.",
        "Los reyes están en oposición diagonal.",
        "La distancia del rey negro al punto de intersección es mayor que dos (g=cerca, l=lejos).",
        "Hay un jaque oculto (descubierto) contra el rey negro.",
        "Algún rey controla el punto de intersección (n=ninguno, b=negro, w=blanco).",
        "Hay múltiples jaques disponibles.",
        "La casilla de la dama (a8) está siendo atacada.",
        "La torre blanca tiene acceso a la columna 'a' o a la fila 8.",
        "Re-clavada diferida.",
        "La torre blanca puede renovar la clavada (skewer).",
        "Se puede capturar la torre blanca de forma segura.", 
        "La torre blanca captura el peón negro.",
        "La torre blanca ataca la casilla de mate.",
        "Se aplica un patrón simple (ahogado, etc).",
        "Clavada (skewer) tras jaques.",
        "Posibilidad de clavada (skewer) por parte de la torre.",
        "La torre blanca hace una clavada o ataca el peón.",
        "Oposición especial.",
        "El rey blanco está ahogado o en riesgo de estarlo.",
        "Amenaza de clavada (skewer).",
        "El rey negro controla el punto de intersección.",
        "El rey negro está en a8.",
        "El rey negro está en jaque.",
        "El rey negro está sobrecargado.",
        "El rey negro está en posición vulnerable a una clavada.",
        "El rey negro tiene vía de escape (egress).",
    ],
    "Niveles": [
        "t, f", "t, f", "t, f", "t, f", "t, f",
        "t, f", "t, f", "t, f", "t, f", "t, f",
        "t, f", "t, f", "g, l", "t, f",
        "n, b, w", "t, f", "t, f", "t, f",
        "t, f", "t, f", "t, f", "t, f",
        "t, f", "t, f", "t, f", "t, f",
        "t, f", "t, f", "t, f", "t, f",
        "t, f", "t, f", "t, f", "t, f",
        "t, f", "t, n",
    ],
    "Significado niveles": [
        "t=sí, f=no", "t=sí, f=no", "t=sí, f=no", "t=sí, f=no", "t=sí, f=no",
        "t=sí, f=no", "t=sí, f=no", "t=sí, f=no", "t=sí, f=no", "t=sí, f=no",
        "t=está en un borde (no a8), f=no está en un borde (o está en a8)",
        "t=sí, f=no",
        "g=distancia ≤ 2 (bueno para blancas), l=distancia > 2 (malo para blancas)",
        "t=sí, f=no",
        "n=ninguno, b=negro, w=blanco",
        "t=sí, f=no", "t=sí, f=no", "t=sí, f=no",
        "t=sí, f=no", "t=sí, f=no", "t=sí, f=no", "t=sí, f=no",
        "t=sí, f=no",
        "t=se aplica, f=no se aplica",
        "t=puede ser clavado tras jaques, f=no puede",
        "t=clavada, f=no",
        "t=sí, f=no",
        "t=hay, f=no hay",
        "t=hay riesgo de ahogado, f=no hay riesgo de ahogado",
        "t=hay amenaza de clavada, f=no hay",
        "t=sí, f=no",
        "t=en a8, f=no",
        "t=jaque, f=no",
        "t=sobrecargado, f=no sobrecargado",
        "t=posición de skewer, f=no",
        "t=sí, n=no",
    ],
}

tabla_variables = pd.DataFrame(VARIABLES_DATA)


def layout():
    return dbc.Container([
 
        # ---------- Contexto ----------
        seccion("Contexto", [
            html.P(
                "El ajedrez, además de ser un deporte, constituye un dominio clásico "
                "para el estudio de la toma de decisiones y el razonamiento automático "
                "(Russell y Norvig, 2020). Desde los años cincuenta, se han utilizado "
                "los finales de ajedrez como pruebas para algoritmos de aprendizaje "
                "automático, ya que poseen un número reducido de piezas, reglas "
                "perfectamente definidas y resultados verificables objetivamente: "
                "victoria, derrota o tablas (Shapiro, 1983)."
            ),
            html.P(
                "Tradicionalmente se reconocen tres fases en una partida de ajedrez: "
                "la apertura, donde predomina el desarrollo de las piezas y el control "
                "del centro; el medio juego, donde se producen maniobras de ataque y "
                "defensa contra el rey rival o sus debilidades estructurales; y el "
                "final, donde tras varios intercambios la promoción de peones se "
                "convierte en el tema dominante (Dvoretsky, 2003). Uno de los aspectos "
                "más fascinantes del ajedrez es el estudio de los finales, donde el "
                "número de piezas se reduce y el juego se vuelve más teórico y preciso "
                "(Nunn, 2010)."
            ),
        ]),
 
        # ---------- Datos clave ----------
        html.Div([
            dbc.Row([
                dbc.Col(stat_card("3.196", "posiciones del final"), xs=6, md=3),
                dbc.Col(stat_card("36", "variables categóricas por posición"), xs=6, md=3),
                dbc.Col(stat_card("2", "clases: won / nowin"), xs=6, md=3),
                dbc.Col(stat_card("1983", "Shapiro, University of Edinburgh"), xs=6, md=3),
            ], className="g-3"),
        ], className="krk-section krk-section-alt"),
 
        # ---------- Objetivos ----------
        seccion("Objetivos", [
            html.H3("Objetivo general"),
            html.P(
                "Analizar el comportamiento del final de ajedrez Rey + Torre vs "
                "Rey + Peón a partir del dataset KRKPA7, mediante técnicas de análisis "
                "exploratorio de datos, visualización interactiva y modelado predictivo, "
                "para identificar los patrones que determinan si el peón logra ganar o si "
                "las blancas lo detienen."
            ),
            html.H3("Objetivos específicos"),
            dbc.Row([
                dbc.Col(html.Div([
                    html.H4("1. Caracterizar", style={"color": "#008080"}),
                    html.P(
                        "Realizar un análisis univariado y bivariado de las 36 "
                        "variables categóricas, identificando su distribución, "
                        "asociación con la variable objetivo y relaciones entre "
                        "predictoras mediante V de Cramér."
                    ),
                ], className="krk-stat"), md=6),
                dbc.Col(html.Div([
                    html.H4("2. Predecir", style={"color": "#40B5A0"}),
                    html.P(
                        "Construir un modelo predictivo que clasifique si una "
                        "posición termina en victoria del bando del peón (won) o no "
                        "(nowin), evaluado con exactitud, F1, AUC-ROC y validación "
                        "cruzada."
                    ),
                ], className="krk-stat"), md=6),
            ], className="g-3"), # <-- Aquí faltaba cerrar el Row
        ]),
 
        # ---------- Marco teórico ----------
        seccion("Marco teórico", [
 
            html.H3("Finales de ajedrez"),
            html.P(
                "Los finales han sido estudiados desde dos perspectivas complementarias: "
                "la teoría ajedrecística, que establece reglas prácticas sobre cómo "
                "ganar o entablar, y la teoría de la computación, que los utiliza como "
                "problemas de búsqueda y clasificación (Russell y Norvig, 2020). La "
                "teoría clásica (Dvoretsky, 2003) establece que las blancas ganan si "
                "logran detener al peón con la torre y acercar su rey para dar mate. "
                "Las negras, en cambio, obtienen tablas o ganan si coronan el peón, "
                "ahogan al rey blanco o capturan la torre."
            ),
 
            html.H3("V de Cramér"),
            html.P(
                "Dado que todas las variables del dataset son categóricas, no es "
                "posible usar correlaciones de Pearson o Spearman. En su lugar se "
                "emplea la V de Cramér (Cramér, 1946), que cuantifica la fuerza de "
                "asociación entre dos variables categóricas con valores entre 0 "
                "(independencia) y 1 (asociación perfecta)."
            ),
 
            html.Div(
                dcc.Markdown(
                    r"""
                    $$
                    V = \sqrt{\frac{\chi^2}{n \cdot \min(r-1, c-1)}}
                    $$
                    """,
                    mathjax=True,
                ),
                className="krk-formula",
            ),
 
            html.P(
                "Para que la V de Cramér sea válida se requiere que ambas variables "
                "sean categóricas, que las observaciones sean independientes y que "
                "las frecuencias esperadas de la tabla de contingencia sean adecuadas "
                "(al menos el 80 % de las celdas con frecuencia esperada ≥ 5). Cuando "
                "alguna celda queda por debajo de ese umbral, el p-valor del chi-cuadrado "
                "clásico pierde validez. En esos casos, si se requiere un contraste de "
                "hipótesis, se recomienda usar chi-cuadrado con simulación de Monte Carlo "
                "o la prueba exacta de Fisher para tablas 2×2 (Agresti, 2002). Sin embargo, "
                "la V de Cramér como medida descriptiva se calcula directamente a partir "
                "del estadístico chi-cuadrado observado, sin requerir corrección."
            ),
 
            html.P(
                "Su principal ventaja es que permite comparar asociaciones en tablas "
                "de contingencia de dimensiones distintas, algo que el coeficiente "
                "phi no permite (Agresti, 2002). Se usa con dos propósitos: medir la "
                "relación de cada predictora con class, y construir la matriz de "
                "asociación entre predictoras para detectar redundancia."
            ),
 
            html.H3("Residuos estandarizados"),
            html.P(
                "Una vez detectada una asociación significativa con la V de Cramér, "
                "es útil identificar qué celdas específicas contribuyen a esa "
                "asociación. Para esto se emplean los residuos estandarizados de "
                "Pearson, que comparan la frecuencia observada con la esperada bajo "
                "independencia:"
            ),
 
            html.Div(
                dcc.Markdown(
                    r"""
                    $$
                    r_{ij} = \frac{O_{ij} - E_{ij}}{\sqrt{E_{ij}}}
                    $$
                    """,
                    mathjax=True,
                ),
                className="krk-formula",
            ),
 
            html.P(
                "Un residuo mayor a 2 en valor absoluto indica que esa celda aporta "
                "significativamente a la asociación, y un residuo mayor a 3 señala "
                "una desviación fuerte. Los residuos positivos indican que la "
                "combinación observada ocurre más de lo esperado, y los negativos "
                "que ocurre menos (Agresti, 2002). Existe también la versión "
                "ajustada de Haberman, que corrige por el tamaño de la tabla y es "
                "preferible cuando hay más de 2 filas o columnas."
            ),
        ], alt=True),
 
        # ---------- Metodología ----------
        seccion("Metodología", [
            dbc.Row([
                dbc.Col(html.Div([
                    html.H4("Análisis exploratorio"),
                    html.P(
                        "Univariado (frecuencias y distribuciones), bivariado "
                        "(tablas de contingencia y V de Cramér) y multivariado "
                        "(matriz de asociación entre predictoras)."
                    ),
                ], className="krk-stat"), md=4),
                dbc.Col(html.Div([
                    html.H4("Visualización interactiva"),
                    html.P(
                        "Dashboard con filtros por clase (won / nowin), exploración "
                        "individual y agrupada de variables, y matrices con tooltip."
                    ),
                ], className="krk-stat accent"), md=4),
                dbc.Col(html.Div([
                    html.H4("Modelado predictivo"),
                    html.P(
                        "Se procederá a construir un modelo de predicción que, a "
                        "partir de las variables del tablero, clasifique "
                        "correctamente si una posición termina en victoria del bando "
                        "del peón (won) o no (nowin), evaluando su desempeño mediante "
                        "métricas como exactitud, matriz de confusión, F1-score, "
                        "AUC-ROC y validación cruzada."
                    ),
                ], className="krk-stat warm"), md=4),
            ], className="g-3"),
        ]),
 
        # ---------- Modelado Predictivo ----------
        seccion("Modelado predictivo", [
            html.P(
                "Para identificar el modelo que mejor clasifica las posiciones del final de "
                "ajedrez, se evaluaron cuatro algoritmos candidatos: Regresión logística, "
                "Árbol de Decisión, Random Forest y CatBoost. Dado que todas las variables "
                "son categóricas, se codificaron con One-Hot antes de entrenar cada modelo."
            ),
            html.P(
                "Tras evaluar los cuatro modelos con validación cruzada y las métricas de "
                "desempeño (Accuracy y F1-Score), el mejor modelo fue CatBoost, "
                "que fue el seleccionado y guardado para producción."
            ),
        ], alt=True),
 
        # ---------- Dataset ----------
        seccion("El dataset", [
            html.P(
                "KRKPA7 contiene 3.196 posiciones del final Rey + Torre (blancas) vs "
                "Rey + Peón (negras) en a7, con el peón negro a punto de coronar y el "
                "tablero visto desde la perspectiva del negro (Shapiro, 1983). Fue "
                "generado por Alen D. Shapiro en su tesis doctoral de 1983, Structured "
                "Induction in Expert Systems. Cada posición se describe con 36 "
                "variables categóricas; la variable objetivo class indica si gana el "
                "bando del peón (won) o no (nowin)."
            ),
            html.H3("Tabla de variables"),
            dash_table.DataTable(
                data=tabla_variables.to_dict("records"),
                columns=[{"name": c, "id": c} for c in tabla_variables.columns],
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left",
                    "padding": "10px 12px",
                    "fontSize": "12.5px",
                    "whiteSpace": "normal",
                    "height": "auto",
                    "fontFamily": "Inter, Segoe UI, sans-serif",
                    "backgroundColor": "transparent",
                    "color": "inherit",
                    "border": "1px solid rgba(0, 0, 0, 0.06)",
                },
                page_size=15,
                sort_action="native",
                filter_action="native",
            ),
        ], alt=True),
 
    ], fluid=True)