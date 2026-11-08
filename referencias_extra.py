"""Calcula (a) la heuristica voraz de Chvatal y (b) la relajacion lineal (cota inferior)."""
import json, time, numpy as np
from scipy.optimize import linprog
from setcover_datos import cargar_datos
from algoritmo_genetico import SetCoverGA
A, c = cargar_datos()
t0 = time.time(); ga = SetCoverGA(A, c, seed=0)
xg = ga.reparar(np.zeros(A.shape[1], dtype=bool)); tg = time.time() - t0
t0 = time.time()
lp = linprog(c, A_ub=-A, b_ub=-np.ones(A.shape[0]), bounds=(0, 1), method="highs"); tl = time.time() - t0
out = {"voraz": {"costo": float(c @ xg), "antenas": int(xg.sum()), "tiempo": tg, "valida": bool((A @ xg >= 1).all())},
       "lp": {"costo": float(lp.fun), "tiempo": tl}}
json.dump(out, open("resultados/referencias.json", "w"), indent=1); print(out)
