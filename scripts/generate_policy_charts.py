"""
Generate comparison charts for network selection policies:
- Max-RSSI
- Random
- Proposed (MCDM baseline)

Outputs:
- models/policy_energy.png
- models/policy_qos_penalty.png
- models/policy_total_cost.png
"""
import os
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt

# Ensure project root is on sys.path when running as a script
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.simulation import SimulationEngine
from app.core.decision_logic import (
    calculate_energy_cost,
    calculate_qos_penalty,
    calculate_cost,
    select_best_network,
)

PolicyName = str


def pick_max_rssi(networks):
    return max(networks, key=lambda n: (n.rssi if n.rssi is not None else -999.0, n.bandwidth))


def pick_random(networks):
    return random.choice(networks)


def compute_metrics(sim: SimulationEngine, net, task) -> Tuple[float, float, float]:
    cfg = sim.network_configs.get(net.name)
    if not cfg:
        return None
    energy = calculate_energy_cost(cfg, net, task)
    qos_penalty = calculate_qos_penalty(net, task)
    total = calculate_cost(net, cfg, task)
    return energy, qos_penalty, total


def simulate(steps: int = 600):
    sim = SimulationEngine()
    metrics: Dict[PolicyName, List[Tuple[float, float, float]]] = {
        "Max-RSSI": [],
        "Random": [],
        "Proposed": [],
    }

    for _ in range(steps):
        state = sim.run_simulation_step()
        nets = state.available_networks
        task = state.current_task

        if not nets:
            continue

        # Proposed (MCDM)
        try:
            best_net, _ = select_best_network(nets, sim.network_configs, task)
            m = compute_metrics(sim, best_net, task)
            if m:
                metrics["Proposed"].append(m)
        except Exception:
            pass

        # Max-RSSI
        try:
            net = pick_max_rssi(nets)
            m = compute_metrics(sim, net, task)
            if m:
                metrics["Max-RSSI"].append(m)
        except Exception:
            pass

        # Random
        try:
            net = pick_random(nets)
            m = compute_metrics(sim, net, task)
            if m:
                metrics["Random"].append(m)
        except Exception:
            pass

    return metrics


def aggregate(metrics: Dict[PolicyName, List[Tuple[float, float, float]]]):
    agg = {}
    for name, vals in metrics.items():
        if not vals:
            agg[name] = (0.0, 0.0, 0.0)
            continue
        energy = sum(v[0] for v in vals) / len(vals)
        qos = sum(v[1] for v in vals) / len(vals)
        total = sum(v[2] for v in vals) / len(vals)
        agg[name] = (energy, qos, total)
    return agg


def plot_bar(data: Dict[PolicyName, float], title: str, ylabel: str, output_path: str):
    names = list(data.keys())
    values = [data[k] for k in names]
    plt.figure(figsize=(6, 4))
    bars = plt.bar(names, values, color=["#8884d8", "#82ca9d", "#ff7f50"])
    plt.title(title)
    plt.ylabel(ylabel)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    for bar, val in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01, f"{val:.2f}", ha="center")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def main():
    metrics = simulate(steps=800)
    agg = aggregate(metrics)

    energy_data = {k: v[0] for k, v in agg.items()}
    qos_data = {k: v[1] for k, v in agg.items()}
    total_data = {k: v[2] for k, v in agg.items()}

    plot_bar(energy_data, "Avg Energy Cost (mJ)", "mJ", "models/policy_energy.png")
    plot_bar(qos_data, "Avg QoS Penalty", "Penalty", "models/policy_qos_penalty.png")
    plot_bar(total_data, "Avg Total Cost", "Cost", "models/policy_total_cost.png")

    print("✅ Charts generated in models/:")
    for f in ["policy_energy.png", "policy_qos_penalty.png", "policy_total_cost.png"]:
        print(f"  - models/{f}")


if __name__ == "__main__":
    main()
