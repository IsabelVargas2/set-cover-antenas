"""Interfaz visual: Set Cover (solucion exacta vs Algoritmo Genetico).
Ejecutar con:   streamlit run app.py
"""
import numpy as np, pandas as pd, streamlit as st
import matplotlib.pyplot as plt
from setcover_datos import cargar_datos
from solucion_exacta import resolver_exacto
from algoritmo_genetico import SetCoverGA

st.set_page_config(page_title="Set Cover: exacto vs GA", layout="wide")
st.title("Set Cover de antenas: solución exacta vs Algoritmo Genético")

@st.cache_data
def datos():
    return cargar_datos()
A, c = datos()
m, n = A.shape

with st.sidebar:
    st.header("Solver exacto")
    t_lim = st.number_input("Límite de tiempo (s)", 10, 3600, 300, step=30)
    st.header("Algoritmo genético")
    pop = st.slider("Tamaño de población", 10, 500, 100, step=10)
    max_gen = st.slider("Máx. generaciones", 20, 1000, 300, step=10)
    p_cruce = st.slider("Prob. de cruce", 0.0, 1.0, 0.9, step=0.05)
    mult_mut = st.slider("Mutación (múltiplos de 1/n)", 0.5, 10.0, 1.0, step=0.5)
    torneo = st.slider("Tamaño del torneo", 2, 10, 3)
    paciencia = st.slider("Paciencia (gens. sin mejora)", 10, 300, 80, step=10)
    n_ejec = st.slider("Corridas del GA", 1, 20, 5)
    semilla = st.number_input("Semilla base", 0, 10_000, 0)

tabs = st.tabs(["Datos", "Solución exacta", "Algoritmo genético", "Comparación"])

with tabs[0]:
    c1, c2, c3 = st.columns(3)
    c1.metric("Clientes (filas)", m); c2.metric("Antenas (columnas)", n)
    c3.metric("Densidad de la matriz", f"{A.mean():.3f}")
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.4))
    ax[0].hist(c, bins=30, color="#4a78d6"); ax[0].set_title("Costos de las antenas"); ax[0].set_xlabel("costo")
    ax[1].hist(A.sum(1), bins=20, color="#2a9d8f"); ax[1].set_title("Antenas que cubren a cada cliente")
    st.pyplot(fig)

with tabs[1]:
    if st.button("Resolver con el solver exacto (HiGHS)"):
        with st.spinner("Resolviendo..."):
            st.session_state["exacto"] = resolver_exacto(A, c, limite_tiempo=t_lim)
    r = st.session_state.get("exacto")
    if r and r["x"] is not None:
        a, b, d = st.columns(3)
        a.metric("Costo", f"{r['costo']:.0f}"); b.metric("Antenas", int(r["x"].sum())); d.metric("Tiempo", f"{r['tiempo']:.1f} s")
        st.write("Estado:", r["estado"], "| ¿Óptimo probado?:", "Sí" if r["optimo"] else "No (límite de tiempo)")
        if r.get("gap") is not None: st.write(f"Gap del solver: {r['gap']:.4%}")
        st.write("Cobertura válida:", bool((A @ r["x"] >= 1).all()))
        st.dataframe(pd.DataFrame({"antena": np.flatnonzero(r["x"]), "costo": c[np.flatnonzero(r["x"])]}))

with tabs[2]:
    if st.button("Ejecutar el Algoritmo Genético"):
        res = []
        barra = st.progress(0.0)
        for k in range(n_ejec):
            res.append(SetCoverGA(A, c, seed=int(semilla) + k, pop=pop, max_gen=max_gen, p_cruce=p_cruce,
                                  p_mut=mult_mut / n, torneo=torneo, paciencia=paciencia).ejecutar())
            barra.progress((k + 1) / n_ejec)
        st.session_state["ga"] = res
    res = st.session_state.get("ga")
    if res:
        costos = np.array([r["costo"] for r in res]); tiempos = np.array([r["tiempo"] for r in res])
        a, b, d, e = st.columns(4)
        a.metric("Mejor costo", f"{costos.min():.0f}"); b.metric("Costo medio", f"{costos.mean():.1f}")
        d.metric("Desv. estándar", f"{costos.std():.1f}"); e.metric("Tiempo medio", f"{tiempos.mean():.1f} s")
        fig, ax = plt.subplots(figsize=(9, 4))
        for r in res: ax.plot(r["hist_mejor"], alpha=.6)
        if "exacto" in st.session_state and st.session_state["exacto"]["x"] is not None:
            ax.axhline(st.session_state["exacto"]["costo"], color="k", ls="--", label="Solución exacta"); ax.legend()
        ax.set_xlabel("Generación"); ax.set_ylabel("Mejor costo"); ax.set_title("Convergencia del GA (una línea por corrida)")
        ax.grid(alpha=.3); st.pyplot(fig)
        st.dataframe(pd.DataFrame({"corrida": range(len(res)), "costo": costos, "antenas": [int(r['x'].sum()) for r in res],
                                   "generaciones": [r["generaciones"] for r in res], "tiempo (s)": tiempos.round(2)}))

with tabs[3]:
    ex, ga = st.session_state.get("exacto"), st.session_state.get("ga")
    if not ex or not ga:
        st.info("Ejecuta primero el solver exacto y el GA en sus pestañas.")
    else:
        mejor = min(ga, key=lambda r: r["costo"])
        gap = (mejor["costo"] - ex["costo"]) / ex["costo"] * 100
        tabla = pd.DataFrame({"Método": ["Exacto (HiGHS)", "GA (mejor corrida)", "GA (media)"],
                              "Costo": [ex["costo"], mejor["costo"], np.mean([r["costo"] for r in ga])],
                              "Tiempo (s)": [ex["tiempo"], mejor["tiempo"], np.mean([r["tiempo"] for r in ga])]})
        st.dataframe(tabla.round(2))
        st.metric("Brecha del mejor GA respecto al exacto", f"{gap:.2f} %")
        comun = int(((ex["x"] == 1) & (mejor["x"] == 1)).sum())
        st.write(f"Antenas en común: {comun} (exacto: {int(ex['x'].sum())}, GA: {int(mejor['x'].sum())})")
        fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
        ax[0].bar(tabla["Método"], tabla["Costo"], color=["#222", "#4a78d6", "#8fb0f0"]); ax[0].set_title("Costo")
        ax[1].bar(tabla["Método"], tabla["Tiempo (s)"], color=["#222", "#4a78d6", "#8fb0f0"]); ax[1].set_title("Tiempo (s)")
        for a in ax: a.tick_params(axis="x", rotation=15)
        st.pyplot(fig)
