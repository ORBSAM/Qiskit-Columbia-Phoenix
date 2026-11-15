"""
LOCAL COLUMBIA & PHOENIX SYNC


"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize
import time

"""
run_local_city

Run the emulation, locally. Utilizes "classical" math rather than randomization.
"""
def run_local_city(csv_filename, city_name, rows=4, cols=5):
    df = pd.read_csv(csv_filename)
    # emulate 20 qubits for this instances.
    # anything greater, and the computer struggles with linear algebra
    n_nodes = rows * cols  # 20 qubits -> 2^20 = 1,048,576 states
    df_subset = df.head(n_nodes)
    
    print(f"\n[Local Emulator - {city_name}] Building {rows}x{cols} grid ({n_nodes} qubits / 2^{n_nodes} states)...")
    G = nx.grid_2d_graph(rows, cols)
    id_col = "station_id" if "station_id" in df.columns else "intersection_id"
    
    city_modifier = 1.35 if "columbia" in city_name.lower() else 1.10
    
    node_mapping = list(G.nodes())
    for i, (idx, row) in enumerate(df_subset.iterrows()):
        if i >= n_nodes: break
        grid_key = node_mapping[i]
        weight = (row["traffic_volume"] * row["congestion_weight"] * city_modifier) + (np.sin(i) * 120)
        G.nodes[grid_key]['traffic_weight'] = max(float(weight), 50.0)

    mapping = {node: i for i, node in enumerate(G.nodes())}
    H = nx.relabel_nodes(G, mapping)

    # pre-calculate edge weights for speed
    edge_weights = [(u, v, H.nodes[u]['traffic_weight'] + H.nodes[v]['traffic_weight']) for u, v in H.edges()]

    """
    get_cost
    
    Calculate the cost per simulated gate (rzz and rx).
    """
    def get_cost(params):
        gamma, beta = params
        qc = QuantumCircuit(n_nodes)
        qc.h(range(n_nodes))
        for u, v in H.edges(): qc.rzz(2 * gamma, u, v)
        for node in range(n_nodes): qc.rx(2 * beta, node)
        
        state = Statevector.from_instruction(qc)
        probs = state.probabilities()
        
        cost = 0.0
        for i, p in enumerate(probs):
            if p > 1e-8:
                string_cost = sum(((i >> u) & 1) * ((i >> v) & 1) * w_sum for u, v, w_sum in edge_weights)
                cost += p * string_cost
        return cost

    start = time.time()
    result = minimize(get_cost, [np.pi/4, np.pi/4], method='COBYLA', options={'maxiter': 25})
    print(f"[Local Emulator - {city_name}] Finished in {time.time() - start:.2f}s.")
    
    # get optimal state bitstring
    final_qc = QuantumCircuit(n_nodes)
    final_qc.h(range(n_nodes))
    for u, v in H.edges(): final_qc.rzz(2 * result.x[0], u, v)
    for node in range(n_nodes): final_qc.rx(2 * result.x[1], node)
    
    final_probs = Statevector.from_instruction(final_qc).probabilities()
    best_bitstring = format(np.argmax(final_probs), f'0{n_nodes}b')
    return H, best_bitstring, cols

# now, execute the local simulation, and plot it
col_graph, col_bits, c_cols = run_local_city("csv_files/columbia_normalized.csv", "Columbia", rows=4, cols=5)
phx_graph, phx_bits, p_cols = run_local_city("csv_files/phoenix_normalized.csv", "Phoenix", rows=4, cols=5)

# side-by-side 2D-grid visualization
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
col_pos = {i: (i % c_cols, i // c_cols) for i in range(len(col_graph.nodes()))}
phx_pos = {i: (i % p_cols, i // p_cols) for i in range(len(phx_graph.nodes()))}


# light blue = phase A timing
# light green = phase B timing
# QPU syncs green corridors that prevent adjacent bottlenecks across a massive
# multi-city grid layout
col_colors = ['lightblue' if bit == '0' else 'lightgreen' for bit in col_bits]
nx.draw(col_graph, col_pos, ax=axes[0], with_labels=True, node_color=col_colors, node_size=600, font_size=7, font_weight="bold", edge_color="gray")
axes[0].set_title("Columbia, SC (20-Qubit Local Emulator)", fontsize=11)

phx_colors = ['lightblue' if bit == '0' else 'lightgreen' for bit in phx_bits]
nx.draw(phx_graph, phx_pos, ax=axes[1], with_labels=True, node_color=phx_colors, node_size=600, font_size=7, font_weight="bold", edge_color="gray")
axes[1].set_title("Phoenix, AZ (20-Qubit Local Emulator)", fontsize=11)

plt.suptitle("Local Quantum Emulator: 20-Qubit ($2^{20}$ States) Traffic Grid", fontsize=13)
plt.tight_layout()
plt.show()
