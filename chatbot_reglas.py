"""Cerebro del asistente por reglas (sin IA externa, sin API key, sin costo).

Normaliza la pregunta (minúsculas, sin tildes) y busca la respuesta cuyo conjunto de
palabras clave coincida más. Para variables concretas (rimmx, wkna8...) arma la respuesta
con su definición. No depende de Dash, así que se puede probar solo.
"""
import re
import unicodedata

SALUDO = (
    "Hola, soy el asistente del proyecto KRKPA7. Puedo explicarte el dataset, las variables, "
    "el EDA, el modelo y cómo usar el predictor. ¿Qué quieres saber?"
)

AYUDA = (
    "No encontré una respuesta a eso. Puedo ayudarte con:\n\n"
    "- **Dataset**: qué es KRKPA7, cuántas posiciones y variables tiene\n"
    "- **won / nowin**: qué significa cada clase\n"
    "- **Variables**: escribe el nombre de una (por ejemplo *rimmx* o *wkna8*)\n"
    "- **EDA**: variables más relacionadas con el resultado, V de Cramér, residuos\n"
    "- **Modelo**: cuál se eligió y sus métricas\n"
    "- **Predictor**: cómo usarlo\n\n"
    "Prueba con una pregunta corta, por ejemplo: *¿qué es la V de Cramér?*"
)

# V de Cramér con class (EDA) y datos puntuales por variable
V_CLASS = {"rimmx": 0.45, "wxqsq": 0.38, "bknck": 0.365, "wkxbp": 0.233, "katri": 0.22}
DATOS_VAR = {
    "rimmx": "Es la variable más relacionada con la clase (V = 0,45): con rimmx = f se da el 100 % de los casos nowin.",
    "wxqsq": "V = 0,38 con la clase. wxqsq = t es 3,5 veces más frecuente en nowin (48,7 %) que en won (13,7 %).",
    "bknck": "V = 0,365 con la clase. bknck = t aparece en el 56,5 % de los nowin frente al 21,0 % de los won.",
    "wkxbp": "V = 0,233 con la clase. wkxbp = t: 31,8 % en nowin frente a 12,6 % en won.",
    "katri": "V = 0,22 con la clase. katri = w es más frecuente en won (20,9 %) que en nowin (6,4 %). Es la única variable ternaria (n/b/w).",
    "bkna8": "bkna8 = t es 5 veces más frecuente en nowin (10,2 %) que en won (1,2 %).",
    "rkxwp": "rkxwp = t: 23,9 % en won frente a 15,8 % en nowin.",
    "bkpos": "bkpos = t es algo más común en won (79,6 %) que en nowin (66,6 %); en total, 73,4 % de las posiciones.",
    "whxbp": "La torre blanca ataca al peón en el 38 % de las posiciones.",
    "cntxt": "El rey negro está en el borde (y no en a8) en el 43,1 % de las posiciones.",
    "wkna8": "wkna8 = f en el 96,2 % de las posiciones: casi nunca se da.",
    "wkblk": "wkblk = f en el 88,8 % de las posiciones: el rey blanco rara vez bloquea a su torre.",
    "wkxcr": "wkxcr = t en el 36,6 % de las posiciones.",
    "bkovl": "bkovl = t en el 37,2 % de las posiciones.",
    "skewr": "Hay posibilidad de clavada en el 30,7 % de las posiciones.",
}
ELIMINADAS = {
    "spcop": "oposición especial (0 % de las posiciones)",
    "skach": "clavada tras jaques (0,3 %)",
    "hdchk": "jaque oculto (0,5 %)",
    "reskd": "re-clavada diferida (0,8 %)",
}


def normalizar(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ\s]", " ", t)


def _texto_modelo(meta):
    m = (meta or {}).get("metricas_test", {})
    if not m:
        return ""
    s = (f"En el conjunto de prueba logró una exactitud de {m.get('Accuracy', 0) * 100:.1f} %, "
         f"F1 de {m.get('F1', 0):.3f} y AUC-ROC de {m.get('AUC_ROC', 0):.3f}.")
    ic = (meta or {}).get("ic95_accuracy")
    if ic:
        s += f" El IC 95 % de la exactitud es {ic[0] * 100:.1f}–{ic[1] * 100:.1f} %."
    return " " + re.sub(r"(\d)\.(\d)", r"\1,\2", s)


def _reglas(meta):
    mod = _texto_modelo(meta)
    return [
        (["hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "hey", "saludos"],
         "¡Hola! " + "¿Qué quieres saber del proyecto: dataset, variables, EDA, modelo o predictor?"),
        (["gracias", "muchas gracias", "genial", "perfecto", "chao", "adios", "hasta luego"],
         "¡Con gusto! Si tienes otra duda del proyecto, aquí estoy."),
        (["won", "nowin", "no win", "clase", "class", "significa won", "significan"],
         "**won**: gana el bando del peón (negras). **nowin**: las blancas (bando de la torre) detienen al peón, "
         "o no hay victoria del peón (incluye tablas). La variable objetivo es *class*."),
        (["que es krkpa7", "krkpa7", "dataset", "base de datos", "datos", "shapiro", "cuantas posiciones", "cuantas filas", "de donde"],
         "**KRKPA7** tiene 3.196 posiciones del final Rey + Torre (blancas) contra Rey + Peón (negras) en a7, con el peón "
         "a punto de coronar. Lo generó Alen D. Shapiro en su tesis de 1983 (*Structured Induction in Expert Systems*, "
         "Universidad de Edimburgo). Cada posición tiene 36 variables categóricas y la clase won/nowin."),
        (["cuantas variables", "numero de variables", "tipos de variables", "binarias", "categoricas", "predictoras"],
         "Hay **36 variables categóricas**; casi todas son binarias (t/f). Excepciones: *dwipd* (g/l), *btoeg* (n/t) y "
         "*katri* (n/b/w). Para el modelo se usan 32, porque se eliminaron 4 con algún nivel de menos del 1 %."),
        (["eliminaron", "eliminadas", "quitaron", "descartaron", "menos del 1", "raras", "spcop", "skach", "hdchk", "reskd"],
         "Se eliminaron 4 variables porque algún nivel tenía menos del 1 % de las posiciones: **spcop** (0 %), "
         "**skach** (0,3 %), **hdchk** (0,5 %) y **reskd** (0,8 %). Quedaron 32 para el modelo."),
        (["distribucion de la clase", "balance", "balanceada", "cuantos won", "cuantos nowin", "proporcion", "porcentaje de won"],
         "La clase está casi balanceada: **1669 won (52,2 %)** y **1527 nowin (47,8 %)**, solo 4,4 puntos de diferencia."),
        (["mas influye", "mas importante", "mas relacionada", "mas relacionadas", "mejor variable", "variable clave", "top 5",
          "influye", "determinante", "relacion con la clase"],
         "Las más relacionadas con la clase (V de Cramér): **rimmx (0,45)**, **wxqsq (0,38)**, **bknck (0,365)**, "
         "**wkxbp (0,233)** y **katri (0,22)**. La clave es rimmx: con rimmx = f se da el 100 % de los casos nowin."),
        (["v de cramer", "cramer", "asociacion", "asociacion entre variables"],
         "La **V de Cramér** mide la fuerza de asociación entre dos variables categóricas, de 0 (independientes) a 1 "
         "(asociación perfecta). Se calcula a partir del chi-cuadrado y sirve para comparar tablas de distinto tamaño. "
         "Aquí se usa con la clase y entre predictoras."),
        (["residuo", "residuos", "estandarizados", "pearson"],
         "Los **residuos estandarizados** comparan lo observado con lo esperado bajo independencia. Un valor mayor a 2 en "
         "valor absoluto indica que esa celda aporta a la asociación; mayor a 3, una desviación fuerte."),
        (["redundan", "entre predictoras", "pares", "correlacion entre", "multicolinealidad"],
         "Los pares más asociados son **whxbp–wkxbp (0,67)**, **rkxwp–whxbp (0,639)**, **bkovl–r2ar8 (0,591)**, "
         "**cntxt–skewr (0,579)** y **wkxbp–wkxcr (0,564)**. Ninguno supera 0,7: no hay variables muy redundantes."),
        (["eda", "analisis exploratorio", "conclusiones", "hallazgos", "resultados del analisis"],
         "Conclusiones del EDA: la clase está balanceada (52,2 % won); casi todas las variables son binarias; las tácticas "
         "avanzadas son rarísimas; la más determinante es **rimmx** (V = 0,45); y no hay redundancia fuerte entre "
         "predictoras (ninguna pasa de 0,7)."),
        (["mejor modelo", "que modelo", "cual modelo", "modelo elegido", "modelo se eligio", "catboost", "que tan bueno",
          "exactitud", "accuracy", "metricas", "f1", "auc", "precision del modelo", "desempeno"],
         "El mejor modelo fue **CatBoost**." + mod + " Se compararon también Regresión logística, Árbol de decisión y "
         "Random Forest, con validación cruzada, Accuracy y F1."),
        (["comparaste", "comparacion de modelos", "otros modelos", "random forest", "regresion logistica", "arbol de decision", "algoritmos"],
         "Se evaluaron cuatro algoritmos: **Regresión logística, Árbol de decisión, Random Forest y CatBoost**, con las "
         "variables codificadas con One-Hot. El mejor, según Accuracy y F1 con validación cruzada, fue CatBoost."),
        (["one hot", "onehot", "codificacion", "codificaron"],
         "Como todas las variables son categóricas, se codificaron con **One-Hot** (una columna 0/1 por cada nivel) antes de entrenar."),
        (["predictor", "como uso", "como se usa", "como predigo", "predecir", "prediccion", "posicion aleatoria", "probabilidad"],
         "En **Modelado predictivo**, elige el valor de cada variable (debajo de cada selector está su significado) o pulsa "
         "*Posición aleatoria del dataset* y luego **Predecir**. Verás la probabilidad de won y nowin; con posiciones "
         "reales del dataset también se indica si el modelo acertó."),
        (["error", "se equivoca", "limitaciones", "confiable", "puedo confiar", "es un motor", "motor de ajedrez"],
         "La probabilidad es una estimación, no una garantía: el modelo aprendió de las 3.196 posiciones y puede fallar en "
         "casos raros. No es un motor de ajedrez; una combinación de valores que no corresponde a una posición real puede "
         "dar una respuesta sin sentido."),
        (["blancas", "negras", "convencion", "quien gana", "bando", "prefijo"],
         "Convención del proyecto: el prefijo **w** corresponde al bando de la torre (blancas) y **b** al bando del peón "
         "(negras). *won* = gana el peón (negras); *nowin* = las blancas lo detienen."),
        (["ajedrez", "final de ajedrez", "rey torre", "peon", "a7", "a8", "coronar"],
         "El final es **Rey + Torre (blancas) contra Rey + Peón (negras)**, con el peón negro en a7 a punto de coronar en "
         "a8. Las blancas intentan detenerlo; las negras ganan si logran coronar o capturan la torre."),
        (["referencias", "bibliografia", "fuentes", "autores", "citas"],
         "Las referencias están en la pestaña **Referencias**: Shapiro (1983), Agresti (2002), Cohen (1988), Cramér (1946), "
         "Dvoretsky (2003), Nunn (2010) y Russell y Norvig (2020)."),
        (["objetivo", "objetivos", "para que sirve", "de que trata", "proyecto"],
         "El objetivo es analizar el final Rey + Torre vs Rey + Peón con EDA, visualización interactiva y modelado "
         "predictivo, para identificar qué patrones determinan si el peón gana (won) o las blancas lo detienen (nowin)."),
        (["autores", "quien hizo", "quienes hicieron", "hicieron", "integrantes", "creadores", "equipo"],
         "El proyecto lo hicieron **Valamy Donado** y **Abraham Navarro** (2026)."),
        (["donde", "pestana", "pagina", "menu", "navegar", "secciones"],
         "El dashboard tiene cuatro secciones: **Introducción**, **EDA**, **Modelado predictivo** (con el predictor) y "
         "**Referencias**. Las secciones se despliegan con un clic. Usa el menú de arriba para moverte."),
    ]


def _buscar_variable(norm, definiciones):
    for v in list(definiciones) + list(ELIMINADAS):
        if re.search(rf"\b{v}\b", norm):
            return v
    return None


def _respuesta_variable(v, definiciones):
    if v in ELIMINADAS:
        return (f"**{v}** ({ELIMINADAS[v]}) se eliminó del modelo por tener un nivel con menos del 1 % de las posiciones.")
    t = f"**{v}**: {definiciones[v]}"
    if v in DATOS_VAR:
        t += "\n\n" + DATOS_VAR[v]
    return t


def responder(texto, definiciones, meta=None):
    norm = " " + normalizar(texto) + " "
    palabras = norm.split()
    v = _buscar_variable(norm, definiciones)
    if v:
        return _respuesta_variable(v, definiciones)

    mejor, puntaje = None, 0
    for claves, resp in _reglas(meta):
        p = 0
        for k in claves:
            kn = normalizar(k).strip()
            if (" " + kn + " ") in norm:
                p += 2 + len(kn.split())          # frase o palabra completa
            elif " " not in kn and any(w.startswith(kn) for w in palabras if len(kn) >= 5):
                p += 1                            # coincidencia parcial (plurales, etc.)
        if p > puntaje:
            mejor, puntaje = resp, p
    return mejor if puntaje > 0 else AYUDA