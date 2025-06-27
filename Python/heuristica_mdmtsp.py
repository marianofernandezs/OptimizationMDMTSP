import re
import numpy as np
from sklearn.cluster import KMeans
import glob
import os
import random

def process_mdmtsp_dat(dat_path, seed=None):
    """
    Procesa un archivo .dat de MDMTSP y aplica KMeans + Nearest Neighbor.
    Devuelve el costo total y las rutas por vendedor.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # Leer archivo
    with open(dat_path, "r") as f:
        content = f.read()

    # Extraer conjuntos
    clientes = list(map(int, re.search(r"set CLIENTES :=\s*(.*?);", content, re.S).group(1).split()))
    depositos = list(map(int, re.search(r"set DEPOSITOS :=\s*(.*?);", content, re.S).group(1).split()))
    num_depots = len(depositos)

    # Matriz de costos
    c_section = re.search(r"param c :.*?:=(.*?);", content, re.S).group(1).strip()
    lines = [line.strip() for line in c_section.splitlines() if line.strip()]
    n = len(lines)
    cost_matrix = np.zeros((n, n), dtype=int)
    for i, line in enumerate(lines):
        vals = list(map(int, line.split()))
        cost_matrix[i, :] = vals[1:]

    # Features: distancia a cada depósito
    features = np.array([
        [cost_matrix[dep-1, cli-1] for dep in depositos]
        for cli in clientes
    ])

    # K-Means clustering
    kmeans = KMeans(n_clusters=num_depots, n_init=10, random_state=np.random.randint(10000))
    labels = kmeans.fit_predict(features)
    centroids = kmeans.cluster_centers_

    # Asignación de clusters a depósitos
    cluster_to_depot = {
        j: depositos[int(np.argmin(centroids[j]))]
        for j in range(num_depots)
    }

    # Agrupación de clientes
    clusters = {j: [] for j in range(num_depots)}
    for cli, lbl in zip(clientes, labels):
        clusters[lbl].append(cli)

    # Rutas por Nearest Neighbor
    routes = {}
    total_cost = 0
    for j in range(num_depots):
        depot = cluster_to_depot[j]
        unvisited = clusters[j].copy()
        current = depot
        route = [depot]
        while unvisited:
            next_node = min(unvisited, key=lambda x: cost_matrix[current-1, x-1])
            route.append(next_node)
            total_cost += cost_matrix[current-1, next_node-1]
            current = next_node
            unvisited.remove(next_node)
        route.append(depot)
        total_cost += cost_matrix[current-1, depot-1]
        routes[depot] = route

    return total_cost, routes

def main():
    num_runs = 10
    seed = 123  # Semilla base

    dat_files = sorted(glob.glob("*_ampl.dat"))
    for dat_file in dat_files:
        best_cost = float('inf')
        best_routes = None

        for i in range(num_runs):
            cost, routes = process_mdmtsp_dat(dat_file, seed + i)
            if cost < best_cost:
                best_cost = cost
                best_routes = routes

        print(f"\nInstancia: {os.path.basename(dat_file)}")
        print(f"Mejor TotalCost (de {num_runs} ejecuciones): {best_cost}")
        for depot, route in best_routes.items():
            route_str = " -> ".join(map(str, route))
            print(f"  Vendedor {depot}: {route_str}")

if __name__ == "__main__":
    main()
