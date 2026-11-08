"""Solucion exacta del Set Cover como PLE binario con HiGHS (scipy.optimize.milp)."""
import time
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from setcover_datos import cargar_datos

def resolver_exacto(A, c, limite_tiempo=600, gap_rel=0.0, verbose=False):
    m, n = A.shape
    t0 = time.time()
    res = milp(c=c,
               constraints=LinearConstraint(A, lb=np.ones(m), ub=np.inf),  # cada cliente cubierto >= 1 vez
               integrality=np.ones(n),                                    # x_j entero
               bounds=Bounds(0, 1),                                       # x_j binario
               options={"time_limit": limite_tiempo, "mip_rel_gap": gap_rel, "disp": verbose})
    t = time.time() - t0
    x = np.round(res.x).astype(int) if res.x is not None else None
    return {"x": x, "costo": res.fun, "tiempo": t, "estado": res.message,
            "optimo": res.status == 0, "cota": getattr(res, "mip_dual_bound", None),
            "gap": getattr(res, "mip_gap", None)}

if __name__ == "__main__":
    A, c = cargar_datos()
    r = resolver_exacto(A, c, verbose=True)
    print("Estado:", r["estado"])
    print("Costo optimo:", r["costo"], "| antenas:", int(r["x"].sum()), "| tiempo: %.2f s" % r["tiempo"])
    print("Cobertura valida:", bool((A @ r["x"] >= 1).all()))
