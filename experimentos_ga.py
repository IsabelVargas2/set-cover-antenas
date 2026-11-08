"""Experimentos del GA: 10 corridas independientes por configuracion + convergencia."""
import json, numpy as np
from setcover_datos import cargar_datos
from algoritmo_genetico import SetCoverGA

A, c = cargar_datos()
configs = {
    "base (pop=100, pmut=1/n)":  dict(pop=100, max_gen=300, paciencia=80),
    "pob. pequena (pop=30)":     dict(pop=30,  max_gen=300, paciencia=80),
    "pob. grande (pop=300)":     dict(pop=300, max_gen=300, paciencia=80),
    "mutacion alta (pmut=5/n)":  dict(pop=100, max_gen=300, paciencia=80, p_mut=5/500),
}
out = {}
for nombre, par in configs.items():
    corridas = []
    for s in range(10):
        r = SetCoverGA(A, c, seed=s, **par).ejecutar()
        assert (A @ r["x"] >= 1).all()
        corridas.append({"seed": s, "costo": r["costo"], "tiempo": r["tiempo"], "gens": r["generaciones"],
                         "antenas": int(r["x"].sum()), "hist_mejor": r["hist_mejor"], "hist_medio": r["hist_medio"],
                         "x": r["x"].tolist()})
    cs = np.array([k["costo"] for k in corridas]); ts = np.array([k["tiempo"] for k in corridas])
    print(f"{nombre:28s} mejor={cs.min():.0f} media={cs.mean():.1f} peor={cs.max():.0f} std={cs.std():.1f} t_medio={ts.mean():.1f}s")
    out[nombre] = {"par": par, "corridas": corridas}
json.dump(out, open("resultados/ga_experimentos.json", "w"))
