set V;                    # Conjunto de todos los nodos (clientes ∪ depósitos)
set CLIENTES within V;    # Sólo los nodos de clientes
set DEPOSITOS within V;   # Sólo los nodos de depósitos
set K;                    # Índice de vendedores (1..numVendedores)

# Parámetros
param c {i in V, j in V} >= 0;            # Costo de i→j (asimétrico permitido)
param depot_num {k in K} integer >= 1, <= card(V);
                                         # Depósito (número de nodo) de salida de cada vendedor k
param retornar default 1 binary;         # 1 = obligar retorno al depósito; 0 = opcional

# Parámetro auxiliar para MTZ
param nC := card(CLIENTES);

# Variables de decisión
var x {i in V, j in V, k in K} binary;
    # 1 si vendedor k recorre el arco i→j

var u {i in CLIENTES, k in K} integer >= 1, <= nC;
    # Variables MTZ para eliminar subtours entre clientes

# Objetivo: minimizar costo total
minimize TotalCost:
    sum {k in K, i in V, j in V: i <> j} c[i,j] * x[i,j,k];

# 1) Cada cliente visitado exactamente una vez
s.t. VisitOnce {j in CLIENTES}:
    sum {k in K, i in V: i <> j} x[i,j,k] = 1;

# 2) Flujo balanceado en cada nodo para cada vendedor
s.t. FlowBalance {k in K, i in V}:
    sum {j in V: j <> i} x[i,j,k]
  = sum {j in V: j <> i} x[j,i,k];

# 3) Salida única desde el depósito de cada vendedor
s.t. StartAtDepot {k in K}:
    sum {j in V: j <> depot_num[k]} x[depot_num[k], j, k] = 1;

# 4) (Opcional) Retorno al depósito
#    Se activa si retornar = 1
s.t. ReturnToDepot {k in K}:
    sum {i in V: i <> depot_num[k]} x[i, depot_num[k], k] = retornar;

# 5) Evitar self-loops
s.t. NoSelfLoop {i in V, k in K}:
    x[i,i,k] = 0;

# 6) Subtour elimination (MTZ) — sólo sobre clientes
s.t. MTZ {k in K, i in CLIENTES, j in CLIENTES: i <> j}:
    u[i,k] - u[j,k] + nC * x[i,j,k] <= nC - 1;
