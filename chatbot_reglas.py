"""Cerebro del asistente por reglas (sin IA externa, sin API key, sin costo).

- Normaliza la pregunta (minúsculas, sin tildes) y tolera errores de ortografía.
- Cada tema tiene palabras clave, una respuesta, a veces una ampliación ("explícame más")
  y preguntas relacionadas que el chat muestra como botones.
- Para variables concretas (rimmx, wkna8...) arma la respuesta con su definición.
No depende de Dash, así que se puede probar solo.
"""
import difflib
import re
import unicodedata

SALUDO = (
    "Hola, soy el asistente del proyecto KRKPA7. Puedo explicarte el dataset, las variables, "
    "el EDA, cómo se eligió y evaluó el modelo, y cómo usar el predictor. ¿Qué quieres saber?"
)

# Preguntas que se muestran al abrir el chat (deben ser el "q" de algún tema)
SUG_INICIAL = ["clases", "modelo", "top_vars"]

V_CLASS = {"rimmx": 0.45, "wxqsq": 0.38, "bknck": 0.365, "wkxbp": 0.233, "katri": 0.22}
DATOS_VAR = {
    "rimmx": "Es la variable más relacionada con la clase (V = 0,45): con rimmx = f se da el 100 % de los casos nowin. También es de las 3 que más usa el modelo.",
    "wxqsq": "V = 0,38 con la clase. wxqsq = t es 3,5 veces más frecuente en nowin (48,7 %) que en won (13,7 %). También es de las 3 que más usa el modelo.",
    "bknck": "V = 0,365 con la clase. bknck = t aparece en el 56,5 % de los nowin frente al 21,0 % de los won. Es la variable que más usa el modelo.",
    "wkxbp": "V = 0,233 con la clase. wkxbp = t: 31,8 % en nowin frente a 12,6 % en won.",
    "katri": "V = 0,22 con la clase. katri = w es más frecuente en won (20,9 %) que en nowin (6,4 %). Es la única variable ternaria (n/b/w).",
    "bkna8": "bkna8 = t es 5 veces más frecuente en nowin (10,2 %) que en won (1,2 %).",
    "rkxwp": "rkxwp = t: 23,9 % en won frente a 15,8 % en nowin.",
    "bkpos": "bkpos = t es algo más común en won (79,6 %) que en nowin (66,6 %); en total, 73,4 % de las posiciones. Es la cuarta variable que más usa el modelo.",
    "whxbp": "La torre blanca ataca al peón en el 38 % de las posiciones.",
    "cntxt": "El rey negro está en el borde (y no en a8) en el 43,1 % de las posiciones.",
    "wkna8": "wkna8 = f en el 96,2 % de las posiciones: casi nunca se da.",
    "wkblk": "wkblk = f en el 88,8 % de las posiciones: el rey blanco rara vez bloquea a su torre.",
    "wkxcr": "wkxcr = t en el 36,6 % de las posiciones.",
    "bkovl": "bkovl = t en el 37,2 % de las posiciones.",
    "skewr": "Hay posibilidad de clavada en el 30,7 % de las posiciones.",
}
ELIMINADAS = {
    "spcop": "oposición especial (0,03 % de las posiciones)",
    "skach": "clavada tras jaques (0,34 %)",
    "hdchk": "jaque oculto (0,47 %)",
    "reskd": "re-clavada diferida (0,81 %)",
}
GRUPOS = {
    "rey blanco": ("Rey blanco (prefijo wk)", ["wkblk", "wknwy", "wkna8", "wkona", "wkspr", "wkxbq", "wkxcr", "wkxbp"]),
    "rey negro": ("Rey negro y peón (prefijo bk)", ["bkcti", "bkna8", "bknck", "bkovl", "bkpos", "btoeg", "cntxt"]),
    "torre": ("Torre y control blanco", ["whxbp", "wxqsq", "r2ar8", "reskr", "rimmx", "rkxwp", "rxmsq", "skewr", "skrxp", "thrsk", "qxmsq"]),
}


def normalizar(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _temas(meta):
    """Lista de temas. Cada uno: id, q (pregunta canónica), claves, resp, mas, sug."""
    m = (meta or {}).get("metricas_test", {})
    ic = (meta or {}).get("ic95_accuracy")
    if m:
        t_modelo = (f"En la prueba logró una exactitud de {m.get('Accuracy', 0) * 100:.1f} %, F1 de {m.get('F1', 0):.3f} "
                    f"y AUC-ROC de {m.get('AUC-ROC', m.get('AUC_ROC', 0)):.3f}.")
        if ic:
            t_modelo += f" El IC 95 % de la exactitud es {ic[0] * 100:.1f}–{ic[1] * 100:.1f} %."
        t_modelo = " " + t_modelo.replace(".", ",") if False else " " + re.sub(r"(\d)\.(\d)", r"\1,\2", t_modelo)
    else:
        t_modelo = ""

    return [
        dict(id="saludo", q=None, claves=["hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "hey", "saludos"],
             resp="¡Hola! ¿Qué quieres saber del proyecto: dataset, variables, EDA, modelo o predictor?",
             sug=["clases", "modelo", "importancia"]),
        dict(id="gracias", q=None, claves=["gracias", "muchas gracias", "genial", "perfecto", "chao", "adios", "hasta luego", "excelente"],
             resp="¡Con gusto! Si tienes otra duda del proyecto, aquí estoy.", sug=["modelo", "importancia"]),

        # ---------------------------------------------------------- dataset / EDA
        dict(id="clases", q="¿Qué significan won y nowin?",
             claves=["won", "nowin", "no win", "clase", "class", "variable objetivo", "target", "significan"],
             resp="**won**: gana el bando del peón (negras). **nowin**: las blancas (bando de la torre) detienen al peón, "
                  "o no hay victoria del peón (incluye tablas). La variable objetivo es *class*.",
             sug=["balance", "convencion", "dataset"]),
        dict(id="dataset", q="¿Qué es el dataset KRKPA7?",
             claves=["krkpa7", "dataset", "base de datos", "datos", "shapiro", "cuantas posiciones", "cuantas filas", "de donde", "origen"],
             resp="**KRKPA7** tiene 3.196 posiciones del final Rey + Torre (blancas) contra Rey + Peón (negras) en a7, con el peón "
                  "a punto de coronar. Lo generó Alen D. Shapiro en su tesis de 1983 (*Structured Induction in Expert Systems*, "
                  "Universidad de Edimburgo). Cada posición tiene 36 variables categóricas y la clase won/nowin.",
             sug=["variables", "clases", "ajedrez"]),
        dict(id="variables", q="¿Cuántas variables hay y de qué tipo?",
             claves=["cuantas variables", "numero de variables", "tipos de variables", "binarias", "categoricas", "predictoras", "36 variables"],
             resp="Hay **36 variables categóricas**; casi todas son binarias (t/f). Excepciones: *dwipd* (g/l), *btoeg* (n/t) y "
                  "*katri* (n/b/w). Para el modelo se usan 32, porque se eliminaron 4 con algún nivel de menos del 1 %.",
             mas="Las variables son predicados de conocimiento experto que Shapiro diseñó sobre el final: no son mediciones libres de "
                 "partidas reales. Escribe el nombre de una (por ejemplo *rimmx*) y te explico qué mide.",
             sug=["eliminadas", "top_vars", "limitaciones"]),
        dict(id="eliminadas", q="¿Por qué se eliminaron variables?",
             claves=["eliminaron", "eliminadas", "eliminar", "quitaron", "descartaron", "menos del 1", "1 por ciento", "raras", "spcop", "skach", "hdchk", "reskd"],
             resp="Se eliminaron 4 variables porque algún nivel tenía menos del 1 % de las posiciones: **spcop** (0,03 %), "
                  "**skach** (0,34 %), **hdchk** (0,47 %) y **reskd** (0,81 %). Casi no varían y, al cruzarlas entre sí, invalidan el "
                  "chi-cuadrado. Quedaron 32 para el modelo.",
             sug=["supuestos", "variables", "cramer"]),
        dict(id="supuestos", q="¿Qué supuestos tiene la V de Cramér?",
             claves=["que supuestos", "supuestos", "supuesto", "frecuencias esperadas", "chi cuadrado", "celdas", "verificacion", "630 pares"],
             resp="La V de Cramér parte del chi-cuadrado, que pide al menos el 80 % de las celdas con frecuencia esperada ≥ 5 y ninguna "
                  "por debajo de 1. Frente a *class*, 35 de 36 variables lo cumplen (falla solo spcop). Entre predictoras, de 630 pares, "
                  "508 cumplen y 122 no; los que fallan involucran variables con niveles minoritarios.",
             sug=["eliminadas", "cramer", "redundancia"]),
        dict(id="balance", q="¿Está balanceada la clase?",
             claves=["esta balanceada", "distribucion de la clase", "balance", "balanceada", "cuantos won", "cuantos nowin", "proporcion", "porcentaje de won", "desbalance"],
             resp="La clase está casi balanceada: **1669 won (52,2 %)** y **1527 nowin (47,8 %)**, solo 4,4 puntos de diferencia. "
                  "Por eso un modelo que siempre dijera la clase mayoritaria acertaría ≈ 52 %.",
             sug=["clases", "validacion", "modelo"]),
        dict(id="top_vars", q="¿Qué variable influye más en el resultado?",
             claves=["mas influye", "mas importante", "mas relacionada", "mas relacionadas", "mejor variable", "variable clave", "top 5",
                     "influye", "determinante", "relacion con la clase", "que variables pesan"],
             resp="Según el EDA (V de Cramér con la clase): **rimmx (0,45)**, **wxqsq (0,38)**, **bknck (0,365)**, "
                  "**wkxbp (0,233)** y **katri (0,22)**. La clave es rimmx: con rimmx = f se da el 100 % de los casos nowin.",
             sug=["permutacion", "cramer", "residuos"]),
        dict(id="cramer", q="¿Qué es la V de Cramér?",
             claves=["v de cramer", "cramer", "asociacion", "asociacion entre variables"],
             resp="La **V de Cramér** mide la fuerza de asociación entre dos variables categóricas, de 0 (independientes) a 1 "
                  "(asociación perfecta). Se calcula a partir del chi-cuadrado y sirve para comparar tablas de distinto tamaño. "
                  "Aquí se usa entre cada predictora y la clase, y entre predictoras.",
             mas="Ejemplo: rimmx tiene V = 0,45 con la clase, la más alta; una V de 0,2 ya es una asociación moderada. No dice en qué "
                 "dirección va la relación: para eso están los residuos estandarizados.",
             sug=["supuestos", "residuos", "top_vars"]),
        dict(id="residuos", q="¿Qué son los residuos estandarizados?",
             claves=["residuo", "residuos", "estandarizados", "pearson"],
             resp="Los **residuos estandarizados** comparan lo observado con lo esperado bajo independencia. Un valor mayor a 2 en "
                  "valor absoluto indica que esa celda aporta a la asociación; mayor a 3, una desviación fuerte.",
             mas="Ejemplo: en rimmx, el residuo de t × won es +15,98: cuando la torre puede ser capturada de forma segura, el peón gana "
                 "mucho más de lo esperado. Positivo = ocurre más de lo esperado; negativo = menos.",
             sug=["cramer", "top_vars"]),
        dict(id="redundancia", q="¿Hay variables redundantes?",
             claves=["hay variables redundantes", "redundan", "entre predictoras", "pares", "correlacion entre", "multicolinealidad", "colinealidad", "vif", "inflacion de la varianza"],
             resp="Los pares más asociados son **whxbp–wkxbp (0,67)**, **rkxwp–whxbp (0,639)**, **bkovl–r2ar8 (0,591)**, "
                  "**cntxt–skewr (0,579)** y **wkxbp–wkxcr (0,564)**. Ninguno supera 0,7: no hay redundancia fuerte. Como todas las "
                  "variables son categóricas, no se usó el VIF, sino la V de Cramér entre predictoras.",
             sug=["cramer", "eda"]),
        dict(id="eda", q="¿Qué conclusiones dejó el EDA?",
             claves=["eda", "analisis exploratorio", "conclusiones", "hallazgos", "resultados del analisis"],
             resp="Conclusiones del EDA: la clase está balanceada (52,2 % won); casi todas las variables son binarias; las tácticas "
                  "avanzadas son rarísimas; la más determinante es **rimmx** (V = 0,45); y no hay redundancia fuerte entre "
                  "predictoras (ninguna pasa de 0,7).",
             sug=["top_vars", "eliminadas", "modelo"]),

        # ---------------------------------------------------------------- modelo
        dict(id="modelo", q="¿Qué modelo se eligió y qué tan bueno es?",
             claves=["mejor modelo", "que modelo", "cual modelo", "modelo elegido", "modelo se eligio", "catboost", "que tan bueno",
                     "exactitud", "accuracy", "metricas", "desempeno", "rendimiento", "resultados del modelo"],
             resp="El mejor modelo fue **CatBoost**." + t_modelo + " Se compararon también Regresión logística, Árbol de decisión y "
                  "Random Forest, con validación cruzada y una línea base.",
             mas="El modelo es un Pipeline: codificación One-Hot + CatBoost con hiperparámetros por defecto (no se ajustaron). Se entrenó "
                 "con el 80 % de las posiciones y se evaluó en el 20 % restante (640 posiciones).",
             sug=["validacion", "confusion", "estabilidad"]),
        dict(id="comparacion", q="¿Qué modelos se compararon?",
             claves=["que modelos", "compararon", "comparaste", "comparacion de modelos", "otros modelos", "random forest", "regresion logistica", "arbol de decision", "algoritmos", "candidatos"],
             resp="Se evaluaron cuatro algoritmos: **Regresión logística, Árbol de decisión, Random Forest y CatBoost**, más una línea base "
                  "que siempre predice la clase mayoritaria. En la prueba, F1: CatBoost 0,9955; árbol 0,9940; Random Forest 0,9910; "
                  "regresión logística 0,9624.",
             sug=["cv", "wilcoxon", "modelo"]),
        dict(id="validacion", q="¿Cómo se validó el modelo?",
             claves=["dividieron los datos", "como se dividieron", "dividieron", "validacion", "como se valido", "como se evaluo", "particion", "entrenamiento y prueba", "train test", "80 20", "estratificada", "metodologia del modelo"],
             resp="Primero se separa un 20 % como prueba (estratificado, random_state = 42). El One-Hot va dentro del Pipeline, así la prueba "
                  "no influye en el entrenamiento. Los modelos se comparan en la prueba y la decisión se confirma con **validación cruzada "
                  "repetida** (5 particiones × 3 repeticiones = 15 evaluaciones por modelo) usando solo el 80 % de entrenamiento.",
             sug=["cv", "wilcoxon", "sobreajuste"]),
        dict(id="cv", q="¿Qué resultados dio la validación cruzada?",
             claves=["validacion cruzada", "cross validation", "15 evaluaciones", "resultados de la validacion", "linea base", "baseline"],
             resp="En validación cruzada, CatBoost tuvo F1 = **0,9916 ± 0,0030** y AUC-ROC = 0,9995; árbol 0,9911; Random Forest 0,9888; "
                  "regresión logística 0,9631. La línea base (clase mayoritaria) queda en exactitud 0,522 y AUC 0,5, así que los cuatro modelos "
                  "capturan señal real.",
             mas="El gráfico de puntos del Dash muestra el F1 de cada una de las 15 particiones por modelo (el rombo es la media): los tres "
                 "modelos de árboles se solapan casi por completo y la regresión logística queda claramente por debajo.",
             sug=["wilcoxon", "sobreajuste", "modelo"]),
        dict(id="wilcoxon", q="¿Qué es la prueba de Wilcoxon?",
             claves=["wilcoxon", "diferencias reales", "significativa", "significativo", "p valor", "valor p", "estadisticamente", "ruido"],
             resp="Compara el F1 de CatBoost con el de otro modelo partición por partición (prueba de rangos con signo). Resultado: supera "
                  "de forma significativa a la regresión logística (p = 0,0001), apenas a Random Forest (p = 0,048) y **no se distingue del "
                  "árbol de decisión** (p = 0,85).",
             mas="Los p-valores son algo optimistas porque las particiones comparten datos, así que la ventaja sobre Random Forest es marginal. "
                 "CatBoost se eligió por F1 medio más alto, menor variabilidad y mejor AUC (útil porque el predictor muestra probabilidades).",
             sug=["cv", "modelo", "limitaciones"]),
        dict(id="confusion", q="¿Cómo se lee la matriz de confusión?",
             claves=["cuantos errores", "comete", "matriz de confusion", "matriz", "confusion", "falsos positivos", "falsos negativos", "aciertos", "errores del modelo", "falso won", "falso nowin"],
             resp="En las 640 posiciones de prueba hay **305 nowin bien clasificados, 332 won bien clasificados, 1 falso won y 2 falsos "
                  "nowin**: 637 aciertos y 3 errores (exactitud 0,9953). Las filas son la clase real y las columnas la predicha.",
             mas="Un *falso won* es una posición nowin que el modelo predice como victoria del peón; un *falso nowin* es lo contrario. "
                 "Con un conjunto de prueba tan pequeño, una posición de diferencia mueve la exactitud 0,0016.",
             sug=["roc", "metricas", "estabilidad"]),
        dict(id="metricas", q="¿Qué son precisión, recall y F1?",
             claves=["precision", "recall", "f1", "f1 score", "sensibilidad", "exhaustividad", "que es f1"],
             resp="Con *won* como clase positiva: **precisión** = de lo que el modelo llama won, cuánto lo es de verdad (0,997); **recall** = de "
                  "los won reales, cuántos detecta (0,994); **F1** = media armónica de ambas (0,9955).",
             sug=["confusion", "roc"]),
        dict(id="roc", q="¿Qué es el AUC-ROC?",
             claves=["auc", "roc", "curva roc", "area bajo la curva"],
             resp="El **AUC-ROC** es la probabilidad de que el modelo asigne mayor probabilidad de won a una posición won que a una nowin "
                  "tomadas al azar. Aquí es ≈ 1 (0,9996): separa casi perfectamente las clases. La curva pegada a la esquina superior "
                  "izquierda lo muestra; la diagonal punteada sería adivinar al azar (AUC = 0,5).",
             sug=["confusion", "metricas", "cv"]),
        dict(id="sobreajuste", q="¿Hay sobreajuste?",
             claves=["sobreajuste", "overfitting", "sobreentrenamiento", "memoriza", "generaliza", "brecha"],
             resp="No hay sobreajuste preocupante: la brecha entre exactitud de entrenamiento y de validación es de solo 0,004 a 0,011 en todos "
                  "los modelos, y con 10 particiones distintas la exactitud se mantiene entre 0,986 y 0,995.",
             sug=["estabilidad", "cv", "limitaciones"]),
        dict(id="estabilidad", q="¿Qué tan estable es el desempeño?",
             claves=["tan estable", "estabilidad", "estable", "variacion", "10 particiones", "semillas", "desempeno esperado"],
             resp="Con 10 particiones distintas la exactitud media fue **0,9914** (desviación 0,0033), entre 0,9859 y 0,9953. El 0,9953 de la "
                  "partición original está en el extremo alto: el desempeño esperado es de ≈ 99,1 %.",
             sug=["sobreajuste", "modelo", "limitaciones"]),
        dict(id="permutacion", q="¿Qué variables usa más el modelo?",
             claves=["variables usa", "usa mas el modelo", "permutacion", "importancia por permutacion", "usa el modelo", "que usa el modelo", "importancia del modelo", "interpretabilidad", "interpretar el modelo"],
             resp="Por importancia de permutación (cuánto cae el F1 al barajar una variable), el modelo depende sobre todo de **bknck (≈ 0,195), "
                  "rimmx (≈ 0,185) y wxqsq (≈ 0,168)**; muy por debajo, bkpos, katri y wkxbq. Cuatro de sus cinco principales coinciden con "
                  "las del EDA.",
             sug=["top_vars", "modelo"]),
        dict(id="onehot", q="¿Qué es la codificación One-Hot?",
             claves=["one hot", "onehot", "codificacion", "codificaron", "dummy", "dummies"],
             resp="Como todas las variables son categóricas, se codificaron con **One-Hot**: una columna 0/1 por cada nivel (por ejemplo, "
                  "rimmx=t y rimmx=f). Se aprende solo con el entrenamiento y se aplica luego a la prueba.",
             sug=["validacion", "modelo"]),
        dict(id="predictor", q="¿Cómo uso el predictor?",
             claves=["predictor", "como uso", "como se usa", "como predigo", "predecir", "prediccion", "posicion aleatoria", "probabilidad", "formulario"],
             resp="En **Modelado predictivo**, elige el valor de cada variable (debajo de cada selector está su significado) o pulsa "
                  "*Posición aleatoria del dataset* y luego **Predecir**. Verás la probabilidad de won y nowin; con posiciones "
                  "reales del dataset también se indica si el modelo acertó.",
             sug=["limitaciones", "modelo", "clases"]),
        dict(id="limitaciones", q="¿Qué limitaciones tiene el modelo?",
             claves=["limitaciones", "limitacion", "se equivoca", "confiable", "puedo confiar", "es un motor", "motor de ajedrez", "100 por ciento", "por que da casi 100", "casi perfecto"],
             resp="Las variables son predicados de **conocimiento experto** diseñados por Shapiro, no mediciones de partidas reales. Por eso la "
                  "exactitud es tan alta: el resultado describe qué tan bien se aprende esa codificación, no el ajedrez real. Además, las "
                  "diferencias entre CatBoost y los otros modelos de árboles son pequeñas y no se ajustaron hiperparámetros.",
             sug=["usos", "importancia", "estabilidad"]),

        # ------------------------------------------------------------- contexto
        dict(id="importancia", q="¿Cuál es la importancia del proyecto?",
             claves=["importancia del proyecto", "para que sirve el proyecto", "por que es importante", "relevancia", "aporte", "aporta", "valor del proyecto", "justificacion"],
             resp="Es un caso de estudio de un flujo **completo y riguroso** de análisis con variables categóricas: verificar supuestos, "
                  "explorar, comparar modelos con evidencia estadística, interpretarlos y publicarlos en un dashboard. Parte de un dataset "
                  "clásico del aprendizaje automático (Shapiro, 1983).",
             sug=["usos", "limitaciones", "dataset"]),
        dict(id="usos", q="¿Para qué se puede usar?",
             claves=["para que se puede usar", "para que sirve", "utilidad", "aplicaciones", "usos", "se puede usar", "aplicar"],
             resp="El modelo en sí sirve para enseñanza y como benchmark académico, no para analizar partidas reales. Lo transferible es la "
                  "**metodología**: V de Cramér y verificación de supuestos con datos categóricos, selección de modelos con validación "
                  "cruzada y pruebas estadísticas, y comunicar resultados con un dashboard (útil en datos clínicos, fraude, encuestas, etc.).",
             sug=["limitaciones", "importancia"]),
        dict(id="convencion", q="¿Qué significan blancas y negras en el proyecto?",
             claves=["blancas", "negras", "convencion", "quien gana", "bando", "prefijo", "uci"],
             resp="Convención del proyecto: el prefijo **w** corresponde al bando de la torre (blancas) y **b** al bando del peón "
                  "(negras). *won* = gana el peón (negras); *nowin* = las blancas lo detienen. La tesis original de Shapiro usa los colores "
                  "contrarios; esto afecta la interpretación de las variables, no el desempeño.",
             sug=["clases", "ajedrez"]),
        dict(id="ajedrez", q="¿Cómo es el final de ajedrez del dataset?",
             claves=["ajedrez", "final de ajedrez", "rey torre", "peon", "a7", "a8", "coronar", "coronacion"],
             resp="El final es **Rey + Torre (blancas) contra Rey + Peón (negras)**, con el peón negro en a7 a punto de coronar en "
                  "a8. Las blancas intentan detenerlo; las negras ganan si logran coronar o capturan la torre.",
             sug=["convencion", "clases", "dataset"]),
        dict(id="referencias", q="¿Cuáles son las referencias?",
             claves=["referencias", "bibliografia", "fuentes", "citas", "autores citados"],
             resp="Las referencias están en la pestaña **Referencias**: Shapiro (1983), Agresti (2002), Cohen (1988), Cramér (1946), "
                  "Dvoretsky (2003), Nunn (2010) y Russell y Norvig (2020).", sug=["dataset"]),
        dict(id="objetivo", q="¿Cuáles son los objetivos del proyecto?",
             claves=["objetivo", "objetivos", "de que trata", "proyecto", "para que se hizo"],
             resp="Analizar el final Rey + Torre vs Rey + Peón con EDA, visualización interactiva y modelado predictivo, para identificar qué "
                  "patrones determinan si el peón gana (won) o las blancas lo detienen (nowin).",
             sug=["importancia", "eda", "modelo"]),
        dict(id="autores", q=None, claves=["quienes son los autores", "autores", "quien lo hizo", "quien hizo", "quienes hicieron", "hicieron", "integrantes", "creadores", "equipo", "autores del proyecto"],
             resp="El proyecto lo hicieron **Valamy Donado** y **Abraham Navarro** (2026).", sug=["importancia"]),
        dict(id="navegacion", q="¿Cómo me muevo por el dashboard?",
             claves=["me muevo", "mover", "dashboard", "donde", "pestana", "pagina", "menu", "navegar", "secciones", "como uso el dashboard"],
             resp="El dashboard tiene cuatro secciones: **Introducción**, **EDA**, **Modelado predictivo** (con la evaluación y el predictor) y "
                  "**Referencias**. Las secciones se despliegan con un clic. Usa el menú de arriba para moverte.",
             sug=["predictor", "eda"]),
    ]


_MAS = ["mas detalle", "explicame mas", "explica mas", "no entendi", "ampliar", "profundiza", "mas informacion", "mas info",
        "ejemplo", "explicalo mejor", "explica mejor", "dame mas"]


def _coincide(k, w):
    """¿La palabra del usuario w equivale a la palabra clave k? (exacta, plural/conjugación o error de ortografía)"""
    if k == w:
        return True
    if len(k) < 5 or len(w) < 5:
        return False
    return (w.startswith(k[:-1]) or k.startswith(w[:-1]) or
            difflib.SequenceMatcher(None, w, k).ratio() >= 0.84)


def _puntaje(norm, palabras, claves):
    p = 0
    for k in claves:
        kn = normalizar(k)
        partes = kn.split()
        if (" " + kn + " ") in (" " + norm + " "):
            p += 2 + len(partes)                            # frase o palabra exacta
        elif all(any(_coincide(kw, w) for w in palabras) for kw in partes):
            p += 1 + len(partes) if len(partes) > 1 else 2  # con errores de ortografía o variantes
    return p


def _buscar_variable(norm, definiciones):
    for v in list(definiciones) + list(ELIMINADAS):
        if re.search(rf"\b{v}\b", norm):
            return v
    return None


def responder(texto, definiciones, meta=None, tema_previo=None):
    """Devuelve {'texto', 'tema', 'sug'}; 'sug' es una lista de preguntas relacionadas."""
    temas = _temas(meta)
    por_id = {t["id"]: t for t in temas}

    def sugerencias(ids):
        return [por_id[i]["q"] for i in ids if i in por_id and por_id[i]["q"]]

    norm = normalizar(texto)
    palabras = norm.split()

    # 0) la pregunta es exactamente la de un botón del chat
    for t in temas:
        if t["q"] and normalizar(t["q"]) == norm:
            return dict(texto=t["resp"], tema=t["id"], sug=sugerencias(t["sug"]))

    # 1) una variable concreta
    v = _buscar_variable(norm, definiciones)
    if v:
        if v in ELIMINADAS:
            t = f"**{v}** ({ELIMINADAS[v]}) se eliminó del modelo por tener un nivel con menos del 1 % de las posiciones."
            return dict(texto=t, tema="eliminadas", sug=sugerencias(["supuestos", "variables"]))
        t = f"**{v}**: {definiciones[v]}"
        if v in DATOS_VAR:
            t += "\n\n" + DATOS_VAR[v]
        return dict(texto=t, tema="variable", sug=sugerencias(["top_vars", "cramer", "permutacion"]))

    # 2) un grupo de variables
    for clave, (titulo, lista) in GRUPOS.items():
        if clave in norm and "variables" in norm:
            t = f"**{titulo}**: " + ", ".join(lista) + ". Escribe el nombre de cualquiera para ver su significado."
            return dict(texto=t, tema="variables", sug=sugerencias(["variables", "top_vars"]))

    # 3) "explícame más" sobre el tema anterior
    if any(m in norm for m in _MAS):
        t = por_id.get(tema_previo)
        if t and t.get("mas"):
            return dict(texto=t["mas"], tema=t["id"], sug=sugerencias(t["sug"]))
        if t:
            return dict(texto="De ese tema no tengo más detalle; prueba con alguna de estas preguntas.", tema=t["id"], sug=sugerencias(t["sug"]))

    # 4) el tema con más coincidencias
    ranking = sorted(((_puntaje(norm, palabras, t["claves"]), i, t) for i, t in enumerate(temas)),
                     key=lambda x: (-x[0], x[1]))
    mejor = ranking[0]
    if mejor[0] >= 2:
        t = mejor[2]
        return dict(texto=t["resp"], tema=t["id"], sug=sugerencias(t["sug"]))

    # 5) coincidencia débil: "¿quisiste decir...?"
    debiles = [t for p, _, t in ranking[:3] if p >= 1 and t["q"]]
    if debiles:
        return dict(texto="No estoy seguro de haber entendido. ¿Quizá querías preguntar alguna de estas?", tema=None,
                    sug=[t["q"] for t in debiles])

    ayuda = ("No encontré una respuesta a eso. Puedo ayudarte con el **dataset**, las **variables** (escribe el nombre de una, por ejemplo "
             "*rimmx*), el **EDA**, la **elección y evaluación del modelo**, el **predictor** y la **importancia del proyecto**.")
    return dict(texto=ayuda, tema=None, sug=sugerencias(SUG_INICIAL))


def sugerencias_iniciales(meta=None):
    por_id = {t["id"]: t for t in _temas(meta)}
    return [por_id[i]["q"] for i in SUG_INICIAL]