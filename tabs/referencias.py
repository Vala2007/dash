from dash import html
import dash_bootstrap_components as dbc


REFERENCIAS = [
    "Shapiro, A. D. (1983). Structured Induction in Expert Systems. Tesis doctoral, University of Edinburgh.",
    "Agresti, A. (2002). Categorical Data Analysis (2nd ed.). Wiley.",
    "Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Lawrence Erlbaum Associates.",
    "Cramér, H. (1946). Mathematical Methods of Statistics. Princeton University Press.",
    "Dvoretsky, M. (2003). Dvoretsky's Endgame Manual. Russell Enterprises.",
    "Nunn, J. (2010). Nunn's Chess Endings, Volume 2. Gambit Publications.",
    "Russell, S., y Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4th ed.). Pearson.",
]


def layout():
    return dbc.Container([
        html.H2("Referencias"),
        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
            html.Ul([html.Li(r) for r in REFERENCIAS])
        ])))),
    ], fluid=True)