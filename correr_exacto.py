"""Corre el solver exacto y guarda el resultado en resultados/exacto.json"""
import json, sys
from setcover_datos import cargar_datos
from solucion_exacta import resolver_exacto
A, c = cargar_datos()
lim = float(sys.argv[1]) if len(sys.argv) > 1 else 600
r = resolver_exacto(A, c, limite_tiempo=lim)
r["x"] = None if r["x"] is None else r["x"].tolist()
r["limite_tiempo"] = lim
json.dump(r, open("resultados/exacto.json", "w"), default=float)
print({k: v for k, v in r.items() if k != "x"})
