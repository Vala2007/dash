"""Asistente del dashboard KRKPA7: chat flotante por reglas (gratis, sin API key).

La lógica de las respuestas está en chatbot_reglas.py; aquí solo está la interfaz.
"""
from dash import ALL, Input, Output, State, callback, clientside_callback, ctx, dcc, html, no_update

from chatbot_reglas import SALUDO, responder, sugerencias_iniciales
from tabs.modelo import DEFINICIONES, cargar_meta

MAX_CARACTERES = 300


def widget():
    """Botón flotante + panel de chat. Se agrega una sola vez en app.layout."""
    return html.Div(
        [
            html.Button("💬", id="chat-fab", className="krk-chat-fab", n_clicks=0,
                        title="Preguntar al asistente", **{"aria-label": "Abrir asistente"}),
            html.Div(
                [
                    html.Div(
                        [html.Span("Asistente KRKPA7", className="krk-chat-title"),
                         html.Span(
                             [html.Button("Nueva", id="chat-nuevo", className="krk-chat-nuevo", n_clicks=0,
                                          title="Empezar una conversación nueva"),
                              html.Button("✕", id="chat-cerrar", className="krk-chat-close", n_clicks=0,
                                          **{"aria-label": "Cerrar"})],
                             className="krk-chat-acciones")],
                        className="krk-chat-head",
                    ),
                    html.Div(id="chat-mensajes", className="krk-chat-msgs"),
                    html.Div(
                        [dcc.Input(id="chat-input", type="text", placeholder="Escribe tu pregunta…",
                                   maxLength=MAX_CARACTERES, debounce=False, n_submit=0,
                                   autoComplete="off", className="krk-chat-input"),
                         html.Button("Enviar", id="chat-enviar", className="krk-chat-send", n_clicks=0)],
                        className="krk-chat-form",
                    ),
                ],
                id="chat-panel", className="krk-chat-panel krk-chat-oculto",
            ),
            dcc.Store(id="chat-historial", data=[]),
        ]
    )


def _burbuja(m):
    if m["role"] == "user":
        return html.Div(m["content"], className="krk-msg krk-msg-user")
    return html.Div(dcc.Markdown(m["content"]), className="krk-msg krk-msg-bot")


def _sugerencias_actuales(historial):
    """Preguntas relacionadas con la última respuesta (o las iniciales si no hay conversación)."""
    for m in reversed(historial or []):
        if m["role"] == "assistant":
            return m.get("sug") or sugerencias_iniciales(cargar_meta())
    return sugerencias_iniciales(cargar_meta())


@callback(Output("chat-panel", "className"),
          Input("chat-fab", "n_clicks"), Input("chat-cerrar", "n_clicks"),
          State("chat-panel", "className"), prevent_initial_call=True)
def abrir_cerrar(n_fab, n_cerrar, clase):
    abierto = "krk-chat-oculto" not in clase
    if ctx.triggered_id == "chat-cerrar" or abierto:
        return "krk-chat-panel krk-chat-oculto"
    return "krk-chat-panel"


@callback(Output("chat-historial", "data"), Output("chat-input", "value"),
          Input("chat-enviar", "n_clicks"), Input("chat-input", "n_submit"),
          Input({"type": "chat-sug", "i": ALL}, "n_clicks"),
          State("chat-input", "value"), State("chat-historial", "data"),
          prevent_initial_call=True)
def enviar(_n1, _n2, clics_sug, texto, historial):
    historial = list(historial or [])
    disparador = ctx.triggered_id
    if isinstance(disparador, dict):                      # clic en una pregunta sugerida
        if not any(clics_sug or []):
            return no_update, no_update
        sugeridas = _sugerencias_actuales(historial)
        if disparador["i"] >= len(sugeridas):
            return no_update, no_update
        texto = sugeridas[disparador["i"]]
    texto = (texto or "").strip()[:MAX_CARACTERES]
    if not texto:
        return no_update, no_update

    tema_previo = next((m.get("tema") for m in reversed(historial) if m["role"] == "assistant"), None)
    r = responder(texto, DEFINICIONES, cargar_meta(), tema_previo)
    historial.append({"role": "user", "content": texto})
    historial.append({"role": "assistant", "content": r["texto"], "tema": r["tema"], "sug": r["sug"]})
    return historial[-40:], ""


@callback(Output("chat-historial", "data", allow_duplicate=True),
          Input("chat-nuevo", "n_clicks"), prevent_initial_call=True)
def nueva_conversacion(n):
    return [] if n else no_update


@callback(Output("chat-mensajes", "children"), Input("chat-historial", "data"))
def pintar(historial):
    burbujas = [_burbuja({"role": "assistant", "content": SALUDO})]
    burbujas += [_burbuja(m) for m in (historial or [])]
    chips = [html.Button(q, id={"type": "chat-sug", "i": i}, className="krk-chat-chip", n_clicks=0)
             for i, q in enumerate(_sugerencias_actuales(historial))]
    if chips:
        burbujas.append(html.Div(chips, className="krk-chat-chips"))
    return burbujas


# baja el scroll al último mensaje
clientside_callback(
    """
    function(children) {
        var el = document.getElementById("chat-mensajes");
        if (el) { setTimeout(function(){ el.scrollTop = el.scrollHeight; }, 50); }
        return window.dash_clientside.no_update;
    }
    """,
    Output("chat-mensajes", "title"),
    Input("chat-mensajes", "children"),
)