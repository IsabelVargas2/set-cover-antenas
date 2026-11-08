# Cobertura de clientes con antenas: Set Cover, solución exacta y Algoritmo Genético

Proyecto de **Investigación de Operaciones I** — Universidad Autónoma de Bucaramanga (UNAB).
Autores: María Isabel Vargas Mendoza y *[nombre del segundo integrante]*.

## Problema
Una empresa de telefonía debe cubrir a **500 clientes** instalando un subconjunto de **500 antenas** candidatas, cada una con un costo.
Un cliente queda cubierto si al menos una de las antenas instaladas lo cubre. Se busca el **menor costo total**: es el *Set Cover*,
un problema NP-completo. Se formula como programación lineal entera binaria:

```
min  Σ_j c_j x_j
s.a. Σ_j a_ij x_j ≥ 1      para cada cliente i
     x_j ∈ {0,1}           para cada antena j
```

## Qué se implementó
| Método | Archivo | Descripción |
|---|---|---|
| Solución exacta | `solucion_exacta.py`, `correr_exacto.py` | Branch & bound con HiGHS (`scipy.optimize.milp`), límite de 600 s |
| Algoritmo Genético | `algoritmo_genetico.py` | Cromosoma binario, selección por torneo, cruce uniforme, mutación, elitismo y reparación de soluciones |
| Heurística voraz y cota LP | `referencias_extra.py` | Chvátal y relajación lineal como referencias |
| Experimentos | `experimentos_ga.py`, `experimento_extendido.py` | 10 corridas con semillas distintas por configuración |
| Figuras | `hacer_figuras.py` | Gráficas del informe |
| Interfaz visual | `app.py` | Aplicación en Streamlit para explorar y comparar |
| Versión MATLAB | `setcover_matlab.m` | Cota LP, voraz y solución exacta con `intlinprog` |

## Resultados principales (instancia 500×500)
| Método | Costo | Antenas |
|---|---|---|
| Cota inferior (relajación lineal) | 27 860 | — |
| Heurística voraz | 52 063 | 23 |
| Exacto (HiGHS, 600 s, no certificado óptimo) | 50 119 | 22 |
| Algoritmo Genético base (mejor de 10) | 48 878 | 22 |
| Algoritmo Genético extendido (mejor de 10) | 49 678 | 22 |

El solver exacto no cerró la brecha en 600 s (38,5 %), mientras que el Algoritmo Genético encontró soluciones de menor costo en pocos segundos.
Los tiempos dependen del equipo. El detalle completo está en `informe/` (PDF y fuentes LaTeX).

## Cómo ejecutar
```bash
pip install -r requirements.txt
python correr_exacto.py           # método exacto  -> resultados/exacto.json
python experimentos_ga.py         # Algoritmo Genético (4 configuraciones x 10 semillas)
python experimento_extendido.py   # configuración extendida
python hacer_figuras.py           # figuras del informe
streamlit run app.py              # interfaz visual
```
En MATLAB: abrir la carpeta del proyecto y ejecutar `setcover_matlab.m` (requiere Optimization Toolbox).

## Estructura
```
datos/        instancia (set_cover_500x500.csv), costos (Costo_S.xlsx, costos.csv)
resultados/   salidas en JSON de los experimentos
informe/      informe en LaTeX (main.tex, secciones/, figuras/) y PDF
```

## Referencias
Las referencias completas están en el informe (Karp 1972, Garey y Johnson 1979, Chvátal 1979, Feige 1998, Beasley y Chu 1996,
Caprara, Fischetti y Toth 2000, entre otras).
