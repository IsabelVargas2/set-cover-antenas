"""Genera las figuras del informe a partir de resultados/*.json"""
import json, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from setcover_datos import cargar_datos
A, c = cargar_datos()
ga = json.load(open("resultados/ga_experimentos.json")); ex = json.load(open("resultados/exacto.json"))
ext = json.load(open("resultados/ga_extendido.json")); ref = json.load(open("resultados/referencias.json"))
ga["extendido (pop=200, pmut=2/n)"] = ext
base = ga["base (pop=100, pmut=1/n)"]["corridas"]
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": .3})

# 1) convergencia (corridas base)
fig, ax = plt.subplots(figsize=(6.5, 3.6))
for k in base: ax.plot(k["hist_mejor"], alpha=.55, lw=1)
ax.plot(np.mean([np.pad(k["hist_mejor"], (0, 300 - len(k["hist_mejor"])), "edge") for k in base], 0)[:111], "k", lw=2, label="media de 10 corridas")
if ex["x"] is not None: ax.axhline(ex["costo"], color="r", ls="--", label=f"exacto ({ex['costo']:.0f})")
ax.set_xlim(0, 110); ax.set_xlabel("Generación"); ax.set_ylabel("Mejor costo"); ax.legend(); fig.tight_layout()
fig.savefig("informe/figuras/convergencia.png", dpi=200); plt.close(fig)

# 2) boxplot por configuracion
fig, ax = plt.subplots(figsize=(6.5, 3.6))
etq = list(ga); ax.boxplot([[k["costo"] for k in ga[e]["corridas"]] for e in etq], tick_labels=[e.split(" (")[0] + "\n(" + e.split("(")[1] for e in etq])
if ex["x"] is not None: ax.axhline(ex["costo"], color="r", ls="--", label="exacto"); ax.legend()
ax.set_ylabel("Costo final"); ax.tick_params(axis="x", labelsize=8); fig.tight_layout()
fig.savefig("informe/figuras/boxplot_config.png", dpi=200); plt.close(fig)

# 3) costo vs tiempo
fig, ax = plt.subplots(figsize=(6.5, 3.6))
for e in etq: ax.scatter([k["tiempo"] for k in ga[e]["corridas"]], [k["costo"] for k in ga[e]["corridas"]], s=18, label=e)
if ex["x"] is not None: ax.scatter([ex["tiempo"]], [ex["costo"]], marker="*", s=200, c="r", label="exacto", zorder=5)
ax.set_xscale("log"); ax.set_xlabel("Tiempo (s, escala log)"); ax.set_ylabel("Costo"); ax.legend(fontsize=7); fig.tight_layout()
fig.savefig("informe/figuras/costo_vs_tiempo.png", dpi=200); plt.close(fig)

# 4) datos
fig, ax = plt.subplots(1, 2, figsize=(6.5, 3))
ax[0].hist(c, bins=30, color="#4a78d6"); ax[0].set_xlabel("Costo de la antena"); ax[0].set_ylabel("Frecuencia")
ax[1].hist(A.sum(1), bins=20, color="#2a9d8f"); ax[1].set_xlabel("Antenas que cubren a un cliente")
fig.tight_layout(); fig.savefig("informe/figuras/datos.png", dpi=200); plt.close(fig)
print("figuras ok")

# 5) comparacion global de costos
fig, ax = plt.subplots(figsize=(6.5, 3.6))
cs_ext = [k["costo"] for k in ext["corridas"]]; cs_b = [k["costo"] for k in base]
nombres = ["Cota LP\n(relajación)", "Voraz\n(Chvátal)", "GA base\n(mejor)", "GA extendido\n(mejor)", "Solver exacto\n(600 s)"]
vals = [ref["lp"]["costo"], ref["voraz"]["costo"], min(cs_b), min(cs_ext), ex["costo"]]
cols = ["#bbbbbb", "#e9c46a", "#4a78d6", "#2a4d9b", "#222222"]
ax.bar(nombres, vals, color=cols)
for i, v in enumerate(vals): ax.text(i, v + 400, f"{v:,.0f}".replace(",", "."), ha="center", fontsize=8)
ax.set_ylabel("Costo"); ax.tick_params(axis="x", labelsize=8); fig.tight_layout()
fig.savefig("informe/figuras/comparacion.png", dpi=200); plt.close(fig)
