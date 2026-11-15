# Quantum Cross-City Traffic Optimization (Columbia, SC & Phoenix, AZ)
A hybrid quantum-classical traffic optimization pipeline utilizing the Quantum Approximate Optimization Algorithm (QAOA) via Qiskit. 
This project compares local statevector emulation against real-world cloud execution on IBM Quantum superconducting hardware (ibm_fez) to harmonize traffic networks across multiple cities.

## Overview
Urban traffic gridlock scales exponentially (2^N).This project explores whether quantum computing can help synchronize and optimize intersection phases across different city layouts:
- Columbia, SC: Modeled as dense, winding corridor networks.
- Phoenix, AZ: Modeled as a sprawling, uniform arterial grid.

I implemented a dual-workflow architecture:Local Emulator (local_qaoa_columbia_phoenix.py): 
- A fast 20-qubit ($4 \times 5$ grid) statevector simulation running locally on CPU RAM to rapidly prototype and visualize individual city layouts (2^20 states).
- Real Quantum QPU (ibm_quantum_qpu_columbia_phoenix.py): A massive 30-qubit joint bi-city network ($6 \times 5$ grid) executed directly on IBM Quantum hardware (ibm_fez), exploring over 1.07 billion states (2^30) in ~3 seconds of active QPU time.

## Key Technical Features
- Bitwise Memory Optimization: Bypassed the 65+ GiB memory wall associated with Qiskit's default string dictionary allocations by evaluating cost functions directly from raw probability arrays using bitwise integer shifts ((i >> u) & 1).
- IBM Quantum Integration: Authenticated via QiskitRuntimeService and optimized for IBM's Open Plan tier constraints using standard Job mode execution.
- Spatial Feature Engineering: Augmented normalized CSV traffic volumes and congestion weights with regional urban multipliers and spatial sine/cosine wave functions.
- Network Visualization: Built automated 2D grid renderers using NetworkX and Matplotlib to display phase assignments (0 vs 1) across nodes.

## Tech Stack
- Language: Python 3.14
- Quantum Framework: Qiskit, Qiskit IBM Runtime
- Optimization: SciPy (COBYLA)
- Data & Graph Analytics: Pandas, NumPy, NetworkX
- Visualization: Matplotlib

# Getting Started

## Prerequisites
Make sure you have your environment set up with Qiskit and IBM Runtime:

```
pip install qiskit qiskit-ibm-runtime pandas numpy networkx matplotlib scipy
```

## Configuration (For Real Hardware Runs)
Save your IBM Quantum API key locally once via Python:
```
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    token="YOUR_IBM_QUANTUM_API_KEY",
    instance="YOUR_INSTANCE_NAME",
    channel="ibm_quantum_platform",
    set_as_default=True,
    overwrite=True
)
```

## Running the Scripts
Run Local 20-Qubit Emulator & Plot:
```
python local_qaoa_columbia_phoenix.py
```

Run 30-Qubit Joint Bi-City Network on IBM Quantum (ibm_fez):
```
python ibm_quantum_qpu_columbia_phoenix.py
```

# Results Summary

**Local Emulator:** Produced clean, symmetrical checkerboard dispersion patterns across independent 20-qubit city grids after ~120 seconds of CPU emulation.

**IBM Quantum QPU (ibm_fez):** Harmonized both city databases simultaneously across a unified 30-qubit joint matrix, yielding an asymmetric, organic multi-city synchronization layout in ~3 seconds of active QPU execution time.

# Author
Sam Urgo - University of South Carolina Student
