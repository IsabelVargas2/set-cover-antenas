"""Carga de datos del proyecto Set Cover (antenas / clientes)."""
import os
import numpy as np
import pandas as pd
import openpyxl

BASE = os.path.dirname(os.path.abspath(__file__))

def cargar_datos(ruta_csv=None, ruta_xlsx=None):
    """Devuelve A (clientes x antenas, 0/1) y c (costo por antena)."""
    ruta_csv = ruta_csv or os.path.join(BASE, "datos", "set_cover_500x500.csv")
    ruta_xlsx = ruta_xlsx or os.path.join(BASE, "datos", "Costo_S.xlsx")
    A = pd.read_csv(ruta_csv).values.astype(np.int8)      # fila i = cliente, columna j = antena
    ws = openpyxl.load_workbook(ruta_xlsx, data_only=True).active
    fila_costos = list(ws.iter_rows(values_only=True))[1]
    c = np.array([v for v in fila_costos[1:] if v is not None], dtype=float)
    assert A.shape[1] == len(c), "numero de antenas distinto al numero de costos"
    return A, c
