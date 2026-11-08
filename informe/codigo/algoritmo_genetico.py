"""Algoritmo genetico (GA) para el Set Cover con costos.

Representacion : cromosoma binario de longitud n (x_j = 1 si se instala la antena j).
Fitness        : costo total de la solucion YA REPARADA (minimizar).
Inicializacion : individuos aleatorios (prob. p_init de cada gen) + reparacion.
Seleccion      : torneo de tamano k.
Cruce          : uniforme (cada gen del hijo viene de un padre al azar), prob. p_cruce.
Mutacion       : bit-flip independiente por gen con prob. p_mut.
Reparacion     : (1) agrega antenas por la mejor razon costo / clientes nuevos cubiertos
                 hasta cubrir a todos; (2) elimina antenas redundantes, de la mas cara a la mas barata.
Elitismo       : los n_elite mejores pasan sin cambios.
Parada         : max_gen generaciones, o paciencia sin mejora, o limite de tiempo.
"""
import time
import numpy as np

PARAMS_DEFECTO = dict(pop=100, max_gen=300, p_cruce=0.9, p_mut=None, torneo=3,
                      n_elite=2, p_init=0.05, paciencia=80, limite_tiempo=None)

class SetCoverGA:
    def __init__(self, A, c, seed=0, **params):
        self.A = np.asarray(A, dtype=np.float32)          # clientes x antenas
        self.c = np.asarray(c, dtype=float)
        self.m, self.n = self.A.shape
        self.p = {**PARAMS_DEFECTO, **params}
        if self.p["p_mut"] is None:
            self.p["p_mut"] = 1.0 / self.n                # ~1 gen mutado por hijo
        self.rng = np.random.default_rng(seed)
        self.cubre = [np.flatnonzero(self.A[:, j]) for j in range(self.n)]  # clientes que cubre cada antena

    # ---------- reparacion ----------
    def reparar(self, x):
        x = x.astype(bool).copy()
        cnt = (self.A @ x.astype(np.float32))              # veces que se cubre cada cliente
        while True:
            sin = cnt < 0.5
            if not sin.any():
                break
            ganancia = sin.astype(np.float32) @ self.A     # clientes nuevos que aporta cada antena
            ganancia[x] = 0
            idx = np.flatnonzero(ganancia > 0)
            j = idx[np.argmin(self.c[idx] / ganancia[idx])]
            x[j] = True
            cnt[self.cubre[j]] += 1
        for j in sorted(np.flatnonzero(x), key=lambda k: -self.c[k]):   # eliminar redundantes
            if (cnt[self.cubre[j]] >= 2).all():
                x[j] = False
                cnt[self.cubre[j]] -= 1
        return x

    def costo(self, x):
        return float(self.c @ x)

    # ---------- operadores ----------
    def seleccion_torneo(self, costos):
        cand = self.rng.integers(0, len(costos), size=self.p["torneo"])
        return cand[np.argmin(costos[cand])]

    def cruce_uniforme(self, a, b):
        mascara = self.rng.random(self.n) < 0.5
        return np.where(mascara, a, b)

    def mutacion(self, x):
        flip = self.rng.random(self.n) < self.p["p_mut"]
        return np.logical_xor(x, flip)

    # ---------- bucle principal ----------
    def ejecutar(self):
        P = self.p
        t0 = time.time()
        pob = [self.reparar(self.rng.random(self.n) < P["p_init"]) for _ in range(P["pop"])]
        costos = np.array([self.costo(x) for x in pob])
        mejor_x, mejor_c = pob[int(np.argmin(costos))].copy(), costos.min()
        hist_mejor, hist_medio, hist_t = [mejor_c], [costos.mean()], [time.time() - t0]
        sin_mejora = 0
        for g in range(1, P["max_gen"] + 1):
            orden = np.argsort(costos)
            nueva = [pob[i].copy() for i in orden[:P["n_elite"]]]          # elitismo
            while len(nueva) < P["pop"]:
                a = pob[self.seleccion_torneo(costos)]
                b = pob[self.seleccion_torneo(costos)]
                hijo = self.cruce_uniforme(a, b) if self.rng.random() < P["p_cruce"] else a.copy()
                hijo = self.reparar(self.mutacion(hijo))
                nueva.append(hijo)
            pob = nueva
            costos = np.array([self.costo(x) for x in pob])
            if costos.min() < mejor_c - 1e-9:
                mejor_c, mejor_x, sin_mejora = costos.min(), pob[int(np.argmin(costos))].copy(), 0
            else:
                sin_mejora += 1
            hist_mejor.append(mejor_c); hist_medio.append(costos.mean()); hist_t.append(time.time() - t0)
            if sin_mejora >= P["paciencia"]:
                break
            if P["limite_tiempo"] and time.time() - t0 > P["limite_tiempo"]:
                break
        return {"x": mejor_x.astype(int), "costo": float(mejor_c), "tiempo": time.time() - t0,
                "generaciones": g, "hist_mejor": hist_mejor, "hist_medio": hist_medio, "hist_t": hist_t}

if __name__ == "__main__":
    from setcover_datos import cargar_datos
    A, c = cargar_datos()
    r = SetCoverGA(A, c, seed=1).ejecutar()
    print("Costo GA:", r["costo"], "| antenas:", int(r["x"].sum()), "| gens:", r["generaciones"],
          "| %.1f s" % r["tiempo"], "| valida:", bool((A @ r["x"] >= 1).all()))
