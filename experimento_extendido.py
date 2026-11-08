"""GA con presupuesto de busqueda mayor (10 corridas)."""
import json, numpy as np
from setcover_datos import cargar_datos
from algoritmo_genetico import SetCoverGA
A, c = cargar_datos()
par = dict(pop=200, max_gen=3000, paciencia=400, p_mut=2/500)
corridas = []
for s in range(10):
    r = SetCoverGA(A, c, seed=100 + s, **par).ejecutar()
    assert (A @ r["x"] >= 1).all()
    corridas.append({"seed": 100 + s, "costo": r["costo"], "tiempo": r["tiempo"], "gens": r["generaciones"],
                     "antenas": int(r["x"].sum()), "hist_mejor": r["hist_mejor"], "x": r["x"].tolist()})
    print(s, r["costo"], round(r["tiempo"], 1), r["generaciones"], flush=True)
cs = np.array([k["costo"] for k in corridas])
print("mejor", cs.min(), "media", cs.mean(), "std", cs.std())
json.dump({"par": par, "corridas": corridas}, open("resultados/ga_extendido.json", "w"))
