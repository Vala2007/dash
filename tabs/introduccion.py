from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd


VARIABLES_DATA = {
    "Variable": [
        "wkblk", "wknwy", "wkna8", "wkona", "wkspr", "wkxbq", "wkxcr", "wkxbp",
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
        "El rey blanco está en el camino de la torre blanca en una situación de doble ataque",
        "El rey blanco obstruye el movimiento de la torre blanca hacia la casilla de coronación (a8)",
        "El rey blanco está en la posición a8",
        "El rey blanco está en la columna a",
        "Puede el rey blanco apoyar a la torre blanca en una horquilla (fork)",
        "El rey blanco es atacado por el peón negro promocionado",
        "Puede el rey blanco atacar la casilla crítica (b7)",
        "El rey blanco captura el peón negro",
        "La torre blanca ataca al peón negro en dirección x<0, y=0",
        "Una o más piezas blancas controlan la casilla de coronación (a8)",
        "El rey negro está en un borde del tablero y no en a8",
        "Están los reyes en oposición normal (separados por una casilla vacía en línea recta)",
        "Distancia del rey blanco al punto de intersección de la torre blanca",
        "Hay un jaque oculto sobre las negras",
        "Algún rey controla el punto de intersección",
        "Pueden las blancas renovar el jaque con ventaja",
        "La casilla de mate es atacada por el peón negro promocionado",
        "La torre blanca tiene acceso seguro a la columna A o a la fila 8",
        "Puede el rey negro ser re-clavado (reskewered) a través de una clavada diferida",
        "Puede la torre blanca sola renovar la amenaza de doble ataque",
        "Puede la torre blanca ser capturada de forma inmediata y segura",
        "La torre blanca amenaza al peón negro (solo en dirección x<0, y=0)",
        "La torre blanca ataca una casilla de mate de forma segura",
        "Se aplica un patrón muy simple (ahogado, clavada diferida o jaque perpetuo)",
        "El rey negro puede ser clavado tras uno o más jaques de la torre blanca",
        "Posibilidad de clavada (skewer)",
        "La torre blanca logra una clavada o el rey blanco ataca el peón negro",
        "Hay un patrón de oposición especial presente",
        "El rey blanco está en ahogado, o el avance del peón negro fuerza el ahogado",
        "Hay una amenaza de clavada (skewer) acechando",
        "El rey negro puede controlar el punto de intersección",
        "El rey negro está en a8",
        "El rey negro está en jaque",
        "El rey negro está sobrecargado y no puede cubrir los puntos de intersección de la torre blanca",
        "El rey negro está en posición de posible clavada (skewer)",
        "El rey negro está a una casilla del borde relevante",
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
        html.Div([
            html.H2("Contexto"),
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
        ], className="krk-section"),

                # ---------- Datos clave ----------
        html.Div([
            dbc.Row([
                dbc.Col(html.Div([
                    html.H4("3.196"),
                    html.P("posiciones legales del final"),
                ], className="krk-stat accent"), md=3),
                dbc.Col(html.Div([
                    html.H4("36"),
                    html.P("variables categóricas por posición"),
                ], className="krk-stat"), md=3),
                dbc.Col(html.Div([
                    html.H4("2"),
                    html.P("clases: won / nowin"),
                ], className="krk-stat warm"), md=3),
                dbc.Col(html.Div([
                    html.H4("1983"),
                    html.P("Shapiro, University of Edinburgh"),
                ], className="krk-stat"), md=3),
            ], className="g-3"),
        ], className="krk-section krk-section-alt"),

        # ---------- Objetivos ----------
        html.Div([
            html.H2("Objetivos"),
            html.H3("Objetivo general"),
            html.P(
                "Analizar el comportamiento del final de ajedrez Rey + Torre vs "
                "Rey + Peón a partir del dataset KRKPA7, mediante técnicas de análisis "
                "exploratorio de datos, visualización interactiva y modelado predictivo, "
                "para identificar los patrones que determinan si las blancas ganan o no "
                "la partida."
            ),
            html.H3("Objetivos específicos"),
            dbc.Row([
                dbc.Col(html.Div([
                    html.H4("1. Caracterizar"),
                    html.P(
                        "Realizar un análisis univariado y bivariado de las 36 "
                        "variables categóricas, identificando su distribución, "
                        "asociación con la variable objetivo y relaciones entre "
                        "predictoras mediante V de Cramér."
                    ),
                ], className="krk-stat"), md=6),
                dbc.Col(html.Div([
                    html.H4("2. Predecir"),
                    html.P(
                        "Construir un modelo predictivo que clasifique si una "
                        "posición termina en victoria de las blancas (won) o no "
                        "(nowin), evaluado con exactitud, F1, AUC-ROC y validación "
                        "cruzada."
                    ),
                ], className="krk-stat accent"), md=6),
            ], className="g-3"),
        ], className="krk-section"),

        # ---------- Marco teórico ----------
        html.Div([
            html.H2("Marco teórico"),

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
                "alguna celda queda por debajo de ese umbral, se recomienda usar el "
                "chi-cuadrado con simulación de Monte Carlo para evitar distorsiones "
                "en el cálculo (Agresti, 2002)."
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
        ], className="krk-section krk-section-alt"),

        # ---------- Metodología ----------
        html.Div([
            html.H2("Metodología"),
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
                        "Clasificación binaria won/nowin. Métricas: exactitud, "
                        "precisión, recall, F1, AUC-ROC y validación cruzada."
                    ),
                ], className="krk-stat warm"), md=4),
            ], className="g-3"),
        ], className="krk-section"),

        # ---------- Dataset ----------
        html.Div([
            html.H2("El dataset"),
            html.P(
                "KRKPA7 contiene 3.196 posiciones del final Rey + Torre (blancas) vs "
                "Rey + Peón (negras) en a7, con el peón negro a punto de coronar y el "
                "tablero visto desde la perspectiva del negro (Shapiro, 1983). Fue "
                "generado por Alen D. Shapiro en su tesis doctoral de 1983, Structured "
                "Induction in Expert Systems. Cada posición se describe con 36 "
                "variables categóricas; la variable objetivo class indica si las "
                "blancas ganan (won) o no (nowin)."
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
        ], className="krk-section krk-section-alt"),

        # ---------- Observación sobre los niveles ----------
        html.Div([
            html.H2("Observación sobre los niveles"),
            html.P(
                "g y w representan el mismo concepto general (acción o característica "
                "de las blancas), pero su uso depende de la variable específica:"
            ),
            dbc.Row([
                dbc.Col(html.Div([
                    html.H4("w — White"),
                    html.P(
                        "Se usa cuando la variable indica directamente una acción o "
                        "posición de las blancas."
                    ),
                ], className="krk-stat"), md=6),
                dbc.Col(html.Div([
                    html.H4("g — Good"),
                    html.P(
                        "Se usa en dwipd para indicar una posición favorable (menor "
                        "o igual a dos casillas) para las blancas."
                    ),
                ], className="krk-stat accent"), md=6),
            ], className="g-3"),
        ], className="krk-section"),

    ], fluid=True)