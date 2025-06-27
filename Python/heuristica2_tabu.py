import numpy as np
import time
import random
from collections import deque
import re
import csv
# Fijar semillas para reproducibilidad
random.seed(42)
np.random.seed(42)

# === Leer archivo .dat con matriz de distancias ===
def extraer_matriz_distancias(dat_path: str):
    with open(dat_path, "r") as file:
        lines = file.readlines()

    matriz = {}
    nodos = []

    in_matrix = False
    for line in lines:
        line = line.strip()
        if line.startswith("param c :"):
            in_matrix = True
            columnas = list(map(int, re.findall(r'\d+', line)))
            continue
        if in_matrix:
            if line == ';':
                break
            partes = line.split()
            fila = int(partes[0])
            valores = list(map(float, partes[1:]))
            matriz[fila] = dict(zip(columnas, valores))
            nodos.append(fila)

    nodos = sorted(matriz.keys())
    size = len(nodos)
    dist_matrix = np.zeros((size, size))
    for i, ni in enumerate(nodos):
        for j, nj in enumerate(nodos):
            dist_matrix[i][j] = matriz[ni][nj]

    return dist_matrix, nodos

# === Costo de una ruta ===
def costo_ruta(ruta, distancias, nodos_dict):
    return sum(distancias[nodos_dict[ruta[i]]][nodos_dict[ruta[i+1]]] for i in range(len(ruta)-1)) + \
           distancias[nodos_dict[ruta[-1]]][nodos_dict[ruta[0]]]

# === Construcción voraz inicial (greedy NN) ===
def construir_ruta_greedy(clientes, distancias, nodos_dict):
    inicio = clientes[0]
    ruta = [inicio]
    restantes = set(clientes[1:])

    while restantes:
        ultimo = ruta[-1]
        siguiente = min(restantes, key=lambda x: distancias[nodos_dict[ultimo]][nodos_dict[x]])
        ruta.append(siguiente)
        restantes.remove(siguiente)

    return ruta

# === Tabu Search intensificado ===
def tabu_search_matriz(ruta_inicial, distancias, nodos_dict, max_iter=1000, lista_tabu_max=30, iter_sin_mejora_max=20):
    mejor_ruta = list(ruta_inicial)
    mejor_costo = costo_ruta(mejor_ruta, distancias, nodos_dict)
    actual = list(ruta_inicial)
    tabu_list = deque(maxlen=lista_tabu_max)
    iter_sin_mejora = 0
    checkpoint = list(actual)

    for _ in range(max_iter):
        vecinos = []
        for i in range(1, len(actual) - 2):
            for k in range(i + 1, len(actual) - 1):
                nuevo = actual[:i] + actual[i:k+1][::-1] + actual[k+1:]
                movimiento = (actual[i], actual[k])
                if movimiento not in tabu_list:
                    vecinos.append((nuevo, movimiento))

        if not vecinos:
            break

        vecinos.sort(key=lambda x: costo_ruta(x[0], distancias, nodos_dict))
        mejor_vecino, mov = vecinos[0]

        actual = mejor_vecino
        costo_actual = costo_ruta(actual, distancias, nodos_dict)

        tabu_list.append(mov)
        if costo_actual < mejor_costo:
            mejor_ruta = list(actual)
            mejor_costo = costo_actual
            iter_sin_mejora = 0
            checkpoint = list(actual)
        else:
            iter_sin_mejora += 1

        if iter_sin_mejora >= iter_sin_mejora_max:
            actual = list(checkpoint)
            iter_sin_mejora = 0

    return mejor_ruta

# === Asignación de clientes al depósito más cercano ===
def asignar_por_distancia(clientes, depositos, distancias, nodos_dict):
    clusters = {d: [] for d in depositos}
    for cliente in clientes:
        deposito_mas_cercano = min(depositos, key=lambda d: distancias[nodos_dict[cliente]][nodos_dict[d]])
        clusters[deposito_mas_cercano].append(cliente)
    return clusters

# === Algoritmo principal mejorado ===
def mdmtsp_mejorado(dat_path, k_depositos=10):
    distancias, nodos = extraer_matriz_distancias(dat_path)
    nodos_dict = {n: i for i, n in enumerate(nodos)}

    depositos = nodos[:k_depositos]
    clientes = nodos[k_depositos:]

    clusters = asignar_por_distancia(clientes, depositos, distancias, nodos_dict)

    rutas_finales = {}
    costo_total = 0
    tiempo_inicio = time.time()

    for deposito, clientes_cluster in clusters.items():
        if not clientes_cluster:
            continue
        ruta_inicial = construir_ruta_greedy(clientes_cluster, distancias, nodos_dict)
        ruta_opt = tabu_search_matriz(ruta_inicial, distancias, nodos_dict)
        rutas_finales[deposito] = ruta_opt
        costo_total += costo_ruta(ruta_opt, distancias, nodos_dict)

    duracion = time.time() - tiempo_inicio
    return rutas_finales, costo_total, duracion

# === Ejecutar todas las instancias y exportar CSV ===
def ejecutar_mejorado_y_exportar(instancias_dict, archivo_csv="resultados_mejorados.csv"):
    resultados = []
    for nombre, ruta in instancias_dict.items():
        k = int(nombre.split("-")[-1])
        print(f"🧪 Ejecutando {nombre} con {k} depósitos...")
        rutas, costo_total, tiempo = mdmtsp_mejorado(ruta, k_depositos=k)

        print(f"✅ Costo total: {round(costo_total)}")
        print(f"⏱️ Tiempo de ejecución: {round(tiempo, 2)} segundos\n")

        for d, r in rutas.items():
            print(f"Depósito {d}: {r}")
        print("\n" + "-" * 50 + "\n")

        resultados.append({
            "Instancia": nombre,
            "Depósitos": k,
            "Costo Total Mejorado": round(costo_total),
            "Tiempo (s)": round(tiempo, 2)
        })

    # Exportar a CSV
    with open(archivo_csv, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Instancia", "Depósitos", "Costo Total Mejorado", "Tiempo (s)"])
        writer.writeheader()
        writer.writerows(resultados)
    print(f"📁 Resultados exportados a {archivo_csv}")

# === Ejecutar ===
if __name__ == "__main__":
    instancias = {
        "Christ100-10": "Christ100-10-f_ampl.dat",
        "Das150-10": "Das150-10-f_ampl.dat",
        "Gaspelle36-5": "Gaspelle36-5-f_ampl.dat",
        "Min134-8": "Min134-8-f_ampl.dat",
        "Or117-14": "Or117-14-f_ampl.dat",
    }

    print("\n===== Resultados versión MEJORADA con CSV =====\n")
    ejecutar_mejorado_y_exportar(instancias)
