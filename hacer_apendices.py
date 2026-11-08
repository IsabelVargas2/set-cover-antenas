"""Genera informe/secciones/apendices.tex a partir de los resultados y del codigo (para no copiar numeros a mano)."""
import json, numpy as np
from setcover_datos import cargar_datos

A, c = cargar_datos()
ex = json.load(open("resultados/exacto.json"))
base = json.load(open("resultados/ga_experimentos.json"))["base (pop=100, pmut=1/n)"]["corridas"]
ext = json.load(open("resultados/ga_extendido.json"))["corridas"]
sel = [j for j, v in enumerate(ex["x"], 1) if v > 0.5]
cov = A.sum(1)
f = lambda v: f"{v:,.0f}".replace(",", "\\,")

L = []
L.append(r"""\appendix
\section*{Anexos y apéndices}
\addcontentsline{toc}{section}{Anexos y apéndices}
\renewcommand{\thesubsection}{\Alph{subsection}}
En el \textbf{Anexo} se describe el material entregado por el docente (los datos de la instancia). Los \textbf{Apéndices} contienen material elaborado por los autores: resultados completos, la solución exacta, el código fuente y las instrucciones para reproducir todo.

\subsection*{Anexo A. Instancia entregada por el docente}
\addcontentsline{toc}{subsection}{Anexo A. Instancia entregada por el docente}
""")
L.append(rf"""La instancia consiste en una matriz binaria $A$ de {A.shape[0]}$\times${A.shape[1]} (filas: clientes; columnas: antenas), donde $a_{{ij}}=1$ si la antena $j$ cubre al cliente $i$, y un vector de costos $c_j$ por antena. La Tabla~\ref{{tab:instancia}} resume sus características.
\begin{{table}}[H]
\centering
\caption{{Características de la instancia}}
\label{{tab:instancia}}
\begin{{tabular}}{{lr}}
\toprule
Característica & Valor \\
\midrule
Clientes (restricciones) & {A.shape[0]} \\
Antenas (variables) & {A.shape[1]} \\
Densidad de la matriz (proporción de unos) & {A.mean():.3f} \\
Antenas que cubren a cada cliente (mín. / media / máx.) & {cov.min()} / {cov.mean():.1f} / {cov.max()} \\
Clientes que cubre cada antena (mín. / media / máx.) & {A.sum(0).min()} / {A.sum(0).mean():.1f} / {A.sum(0).max()} \\
Costo por antena (mín. / media / máx.) & {f(c.min())} / {f(c.mean())} / {f(c.max())} \\
Costo de instalar todas las antenas & {f(c.sum())} \\
\bottomrule
\end{{tabular}}
\end{{table}}
""")
def tabla(corr, tit, lab):
    s = [rf"\begin{{table}}[H]", r"\centering", rf"\caption{{{tit}}}", rf"\label{{{lab}}}", r"\begin{tabular}{rrrrr}", r"\toprule",
         r"Semilla & Costo & Antenas & Generaciones & Tiempo (s) \\", r"\midrule"]
    for r in corr:
        s.append(f"{r['seed']} & {f(r['costo'])} & {r['antenas']} & {r['gens']} & {r['tiempo']:.1f} \\\\")
    cs = np.array([r['costo'] for r in corr])
    s += [r"\midrule", f"Mejor / media / peor & \\multicolumn{{4}}{{r}}{{{f(cs.min())} / {f(cs.mean())} / {f(cs.max())}}} \\\\",
          r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(s)
L.append(r"""\subsection*{Apéndice A. Resultados del Algoritmo Genético por corrida}
\addcontentsline{toc}{subsection}{Apéndice A. Resultados del Algoritmo Genético por corrida}
""")
L.append(tabla(base, "Configuración base (población 100, mutación $1/n$): resultado de cada corrida", "tab:ap_base"))
L.append(tabla(ext, "Configuración extendida (población 200, mutación $2/n$): resultado de cada corrida", "tab:ap_ext"))
L.append(rf"""
\subsection*{{Apéndice B. Mejor solución entera del método exacto}}
\addcontentsline{{toc}}{{subsection}}{{Apéndice B. Mejor solución entera del método exacto}}
HiGHS terminó por límite de tiempo ({ex['limite_tiempo']:.0f} s), por lo que esta solución es la mejor encontrada y no está certificada como óptima: costo {f(ex['costo'])}, cota inferior {f(ex['cota'])} y brecha {100*ex['gap']:.2f}\,\%. Las {len(sel)} antenas seleccionadas (numeradas desde 1) son:

\begin{{quote}}
{", ".join(map(str, sel))}.
\end{{quote}}

\subsection*{{Apéndice C. Código fuente}}
\addcontentsline{{toc}}{{subsection}}{{Apéndice C. Código fuente}}
Se incluyen los tres módulos centrales. El código completo (experimentos, figuras e interfaz) está en el repositorio indicado en el Apéndice D.
""")
for fn, tit in [("setcover_datos.py", "Carga de datos"), ("solucion_exacta.py", "Solución exacta con HiGHS"), ("algoritmo_genetico.py", "Algoritmo Genético con reparación")]:
    L.append(rf"\lstinputlisting[caption={{{tit} (\texttt{{{fn.replace('_', chr(92)+'_')}}})}}]{{codigo/{fn}}}")
L.append(r"""
\subsection*{Apéndice D. Reproducibilidad y repositorio}
\addcontentsline{toc}{subsection}{Apéndice D. Reproducibilidad y repositorio}
Todo el código, los datos y los resultados están publicados en GitHub: \url{https://github.com/USUARIO/REPOSITORIO}. Para reproducir los resultados:
\begin{enumerate}
\item Instalar las dependencias: \texttt{pip install -r requirements.txt}.
\item Resolver con el método exacto: \texttt{python correr\_exacto.py}.
\item Ejecutar los experimentos del Algoritmo Genético: \texttt{python experimentos\_ga.py} y \texttt{python experimento\_extendido.py}.
\item Generar las figuras: \texttt{python hacer\_figuras.py}.
\item Abrir la interfaz visual: \texttt{streamlit run app.py}.
\end{enumerate}
Los tiempos dependen del equipo; los costos del Algoritmo Genético dependen de la semilla, que se fija en cada corrida para que los resultados se puedan repetir.
""")
open("informe/secciones/apendices.tex", "w", encoding="utf-8").write("\n".join(L))
print("ok", len(sel), "antenas")
