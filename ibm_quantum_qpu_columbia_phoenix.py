"""
IBM QUANTUM QPU (COLUMBIA V PHOENIX)


"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from scipy.optimize import minimize
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import time

"""
run_joing_bi_city_qpu

Setup the qpu with the two datasets (Columbia and Phoenix)
"""
def run_joint_bi_city_qpu():
    # authenticate with local service
    service = QiskitRuntimeService()
    
    # load both cities
    df_col = pd.read_csv("csv_files/columbia_normalized.csv")
    df_phx = pd.read_csv("csv_files/phoenix_normalized.csv")
    
    # build a unified 6x5 grid graph (30 nodes = exactly 30 qubits)
    rows, cols = 6, 5
    G = nx.grid_2d_graph(rows, cols)
    n_nodes = len(G.nodes())
    
    print(f"[IBM Quantum QPU] Initializing Joint 30-Qubit Cross-City Network ({rows}x{cols} grid)...")
    
    node_mapping = list(G.nodes())
    for i, grid_key in enumerate(node_mapping):
        # harmonize databases: top half of the nodes go to Columbia, and the other half to Phoenix
        if i < 15:
            row = df_col.iloc[i % len(df_col)]
            weight = (row["traffic_volume"] * row["congestion_weight"] * 1.35) + (np.sin(i) * 100)
        else:
            row = df_phx.iloc[(i - 15) % len(df_phx)]
            weight = (row["traffic_volume"] * row["congestion_weight"] * 1.15) + (np.cos(i) * 100)
            
        G.nodes[grid_key]['traffic_weight'] = max(float(weight), 50.0)

    # reindex nodes to integers (0 to 29) for the quantum circuit
    mapping = {node: i for i, node in enumerate(G.nodes())}
    H = nx.relabel_nodes(G, mapping)

    # finally, find the least busy backend to run the program
    backend = service.least_busy(simulator=False, operational=True, min_num_qubits=n_nodes)
    print(f"[IBM Quantum QPU] Target Hardware Secured: {backend.name} ({backend.num_qubits} qubits available)")

    pm = generate_preset_pass_manager(optimization_level=1, backend=backend)

    """
    create_qaoa_circuit
    Create the qaoa circuit with rzz and rx gates.
    """
    def create_qaoa_circuit(gamma, beta):
        qc = QuantumCircuit(n_nodes)
        qc.h(range(n_nodes))
        for u, v in H.edges(): 
            qc.rzz(2 * gamma, u, v)
        for node in range(n_nodes): 
            qc.rx(2 * beta, node)
        qc.measure_all()
        return qc

    # execute optimization loop using Job mode (compatible with Open/Free plan)
    sampler = Sampler(mode=backend)

    """
    get_cost_qpu
    
    Get the cost from the qpu, and translate it to a binary string.
    """
    def get_cost_qpu(params):
        gamma, beta = params
        logical_qc = create_qaoa_circuit(gamma, beta)
        isa_circuit = pm.run(logical_qc)
        
        job = sampler.run([isa_circuit])
        pub_result = job.result()[0]
        counts = pub_result.data.meas.get_counts()
        total_shots = sum(counts.values())
        
        cost = 0.0
        for bitstring, count in counts.items():
            prob = count / total_shots
            clean_bits = bitstring[::-1]
            string_cost = sum(int(clean_bits[u]) * int(clean_bits[v]) * (H.nodes[u]['traffic_weight'] + H.nodes[v]['traffic_weight']) for u, v in H.edges())
            cost += prob * string_cost
        return cost

    print("[IBM Quantum QPU] Executing 30-qubit optimization loop in job mode...")
    start = time.time()
    result = minimize(get_cost_qpu, [np.pi/4, np.pi/4], method='COBYLA', options={'maxiter': 3})
    print(f"[IBM Quantum QPU] Finished in {time.time() - start:.2f}s.")
    
    # final execution to extract the optimal 30-bit string
    final_qc = create_qaoa_circuit(result.x[0], result.x[1])
    final_counts = sampler.run([pm.run(final_qc)]).result()[0].data.meas.get_counts()
    best_bitstring = max(final_counts, key=final_counts.get)[::-1]
    
    return H, best_bitstring, cols

"""
main

Run the program on the qpu, and use the results to draw a 
grid map.
"""
if __name__ == "__main__":
    graph, optimal_bits, grid_cols = run_joint_bi_city_qpu()
    print(f"\nJoint 30-Qubit Optimized Bi-City Configuration String:\n{optimal_bits}")

    # draw out the 30-qybit joint cross-city grid by utilizing matplot
    plt.figure(figsize=(10, 6))
    pos = {i: (i % grid_cols, i // grid_cols) for i in range(len(graph.nodes()))}
    
    # light blue = phase A timing
    # light green = phase B timing
    # QPU syncs green corridors that prevent adjacent bottlenecks across a massive
    # multi-city grid layout
    node_colors = ['lightblue' if bit == '0' else 'lightgreen' for bit in optimal_bits]
    nx.draw(
        graph, pos, 
        with_labels=True, 
        node_color=node_colors, 
        node_size=600, 
        font_size=8, 
        font_weight="bold", 
        edge_color="gray", 
        width=1.5
    )
    
    plt.title("IBM Quantum 30-Qubit Joint Bi-City Network (Columbia & Phoenix Harmonized)", fontsize=11)
    plt.tight_layout()
    plt.show()
