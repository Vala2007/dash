import os
import pandas as pd

COLUMNAS = [
    "wkblk", "wknwy", "wkna8", "wkona", "wkspr", "wkxbq", "wkxcr", "wkxbp",
    "whxbp", "wxqsq", "cntxt", "dsopp", "dwipd", "hdchk", "katri", "mulch",
    "qxmsq", "r2ar8", "reskd", "reskr", "rimmx", "rkxwp", "rxmsq", "simpl",
    "skach", "skewr", "skrxp", "spcop", "stlmt", "thrsk", "bkcti", "bkna8",
    "bknck", "bkovl", "bkpos", "btoeg", "class"
]

DATA_PATH = os.path.join(os.path.dirname(__file__), "kr-vs-kp.data")


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, header=None, names=COLUMNAS)
    return df