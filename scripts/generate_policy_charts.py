"""
Generate comparison charts for network selection policies:
- Max-RSSI
- Random
- Proposed (MCDM baseline)
- Min-Energy (Greedy Energy)
- Min-QoS-Penalty (Greedy QoS)
- Rule-Based Context-Aware

Outputs:
- models/policy_energy_mean.png
- models/policy_energy_p95.png
- models/policy_qos_violation_latency.png
- models/policy_qos_violation_bandwidth.png
- models/policy_energy_per_task.png
- models/policy_network_usage.png
"""
import os
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

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
from app.models.schemas import TaskState
from app.core.constants import QOS_REQUIREMENTS

PolicyName = str


def pick_max_rssi(networks):
    return max(networks, key=lambda n: (n.rssi if n.rssi is not None else -999.0, n.bandwidth))


def pick_random(networks):
    return random.choice(networks)

def pick_min_energy(networks, sim: SimulationEngine, task):
    best = None
    best_val = float("inf")
    for n in networks:
        cfg = sim.network_configs.get(n.name)
        if not cfg:
            continue
        val = calculate_energy_cost(cfg, n, task)
        if val < best_val:
            best_val, best = val, n
    return best

def pick_min_qos(networks, task):
    best = None
    best_val = float("inf")
    for n in networks:
        val = calculate_qos_penalty(n, task)
        if val < best_val:
            best_val, best = val, n
    return best

def pick_rule_based(networks, task):
    order = []
    if task == TaskState.VIDEO_STREAMING:
        order = ["5G", "Wi-Fi", "BLE"]
    elif task == TaskState.DATA_BURST_ALERT:
        order = ["Wi-Fi", "5G", "BLE"]
    else:
        order = ["BLE", "Wi-Fi", "5G"]
    # choose first available in order
    for name in order:
        for n in networks:
            if n.name == name:
                return n
    return None


def compute_metrics(sim: SimulationEngine, net, task):
    if net is None:
        return None
    cfg = sim.network_configs.get(net.name)
    if not cfg:
        return None
    energy = calculate_energy_cost(cfg, net, task)
    qos_penalty = calculate_qos_penalty(net, task)
    total = calculate_cost(net, cfg, task)
    req = QOS_REQUIREMENTS.get(task, {"min_bandwidth": 0.0, "max_latency": float("inf")})
    viol_latency = 1 if (net.latency is not None and net.latency > req["max_latency"]) else 0
    viol_bw = 1 if (net.bandwidth is not None and net.bandwidth < req["min_bandwidth"]) else 0
    return {
        "energy": energy,
        "qos": qos_penalty,
        "total": total,
        "latency": net.latency,
        "bandwidth": net.bandwidth,
        "net": net.name,
        "task": task,
        "viol_latency": viol_latency,
        "viol_bw": viol_bw,
    }


def simulate(steps: int = 800):
    sim = SimulationEngine()
    metrics: Dict[PolicyName, List[Dict]] = {
        "Proposed": [],
        "Max-RSSI": [],
        "Random": [],
        "Min-Energy": [],
        "Min-QoS-Penalty": [],
        "Rule-Based": [],
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

        # Min-Energy
        try:
            net = pick_min_energy(nets, sim, task)
            m = compute_metrics(sim, net, task)
            if m:
                metrics["Min-Energy"].append(m)
        except Exception:
            pass

        # Min-QoS-Penalty
        try:
            net = pick_min_qos(nets, task)
            m = compute_metrics(sim, net, task)
            if m:
                metrics["Min-QoS-Penalty"].append(m)
        except Exception:
            pass

        # Rule-Based Context-Aware
        try:
            net = pick_rule_based(nets, task)
            m = compute_metrics(sim, net, task)
            if m:
                metrics["Rule-Based"].append(m)
        except Exception:
            pass

    return metrics


def summarize_overall(metrics: Dict[PolicyName, List[Dict]]):
    energy_mean, energy_p95 = {}, {}
    viol_latency_pct, viol_bw_pct = {}, {}
    qos_mean = {}
    network_usage: Dict[PolicyName, Dict[str, float]] = {}
    for name, rows in metrics.items():
        if not rows:
            energy_mean[name] = 0.0
            energy_p95[name] = 0.0
            viol_latency_pct[name] = 0.0
            viol_bw_pct[name] = 0.0
            qos_mean[name] = 0.0
            network_usage[name] = {"Wi-Fi": 0.0, "5G": 0.0, "BLE": 0.0}
            continue
        e = np.array([r["energy"] for r in rows])
        q = np.array([r["qos"] for r in rows])
        vl = np.array([r["viol_latency"] for r in rows])
        vb = np.array([r["viol_bw"] for r in rows])
        energy_mean[name] = float(e.mean())
        energy_p95[name] = float(np.percentile(e, 95))
        viol_latency_pct[name] = float(vl.mean() * 100.0)
        viol_bw_pct[name] = float(vb.mean() * 100.0)
        qos_mean[name] = float(q.mean())

        # Network usage distribution (%)
        counts = {"Wi-Fi": 0, "5G": 0, "BLE": 0}
        for r in rows:
            counts[r["net"]] = counts.get(r["net"], 0) + 1
        total = sum(counts.values()) or 1
        network_usage[name] = {k: (v / total) * 100.0 for k, v in counts.items()}
    return energy_mean, energy_p95, viol_latency_pct, viol_bw_pct, qos_mean, network_usage

def summarize_per_task(metrics: Dict[PolicyName, List[Dict]]):
    tasks_labels = {
        TaskState.VIDEO_STREAMING: "Video",
        TaskState.DATA_BURST_ALERT: "Alert",
        TaskState.IDLE_MONITORING: "Monitor",
    }
    per_task_energy: Dict[str, Dict[str, float]] = {}
    for policy, rows in metrics.items():
        per_task_energy[policy] = {"Video": 0.0, "Alert": 0.0, "Monitor": 0.0}
        # compute means per task
        for tstate, tlabel in tasks_labels.items():
            vals = [r["energy"] for r in rows if r["task"] == tstate]
            per_task_energy[policy][tlabel] = float(np.mean(vals)) if vals else 0.0
    return per_task_energy


def plot_bar(data: Dict[PolicyName, float], title: str, ylabel: str, output_path: str):
    names = list(data.keys())
    values = [data[k] for k in names]
    plt.figure(figsize=(6, 4))
    colors = plt.cm.Set2(np.linspace(0.2, 0.9, len(names)))
    bars = plt.bar(names, values, color=colors)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    for bar, val in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01, f"{val:.2f}", ha="center")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_grouped_per_task(per_task_energy: Dict[PolicyName, Dict[str, float]], output_path: str):
    policies = list(per_task_energy.keys())
    tasks = ["Video", "Alert", "Monitor"]
    x = np.arange(len(tasks))
    width = 0.08
    plt.figure(figsize=(10, 5))
    colors = plt.cm.tab20(np.linspace(0.1, 0.9, len(policies)))
    for idx, policy in enumerate(policies):
        vals = [per_task_energy[policy].get(t, 0.0) for t in tasks]
        plt.bar(x + idx * width, vals, width, label=policy, color=colors[idx])
        for xi, v in zip(x + idx * width, vals):
            plt.text(xi, v * 1.01 if v != 0 else 0.01, f"{v:.2f}", ha="center", fontsize=8)
    plt.xticks(x + (len(policies) - 1) * width / 2, tasks)
    plt.ylabel("Avg Energy (mJ)")
    plt.title("Per-Task Energy Breakdown")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_network_usage(network_usage: Dict[PolicyName, Dict[str, float]], output_path: str):
    policies = list(network_usage.keys())
    nets = ["Wi-Fi", "5G", "BLE"]
    x = np.arange(len(policies))
    width = 0.22
    plt.figure(figsize=(10, 5))
    colors = ["#4C78A8", "#E45756", "#72B7B2"]
    for j, net in enumerate(nets):
        vals = [network_usage[p].get(net, 0.0) for p in policies]
        plt.bar(x + j * width, vals, width, label=net, color=colors[j])
        for xi, v in zip(x + j * width, vals):
            plt.text(xi, v * 1.01 if v != 0 else 0.5, f"{v:.1f}%", ha="center", fontsize=8)
    plt.xticks(x + width, policies, rotation=15)
    plt.ylabel("Selection Share (%)")
    plt.title("Network Usage Distribution")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def main():
    metrics = simulate(steps=800)
    energy_mean, energy_p95, viol_latency_pct, viol_bw_pct, qos_mean, network_usage = summarize_overall(metrics)
    per_task_energy = summarize_per_task(metrics)

    plot_bar(energy_mean, "Avg Energy Cost (mJ)", "mJ", "models/policy_energy_mean.png")
    plot_bar(energy_p95, "95th Percentile Energy (mJ)", "mJ", "models/policy_energy_p95.png")
    plot_bar(viol_latency_pct, "QoS Violation Rate - Latency", "%", "models/policy_qos_violation_latency.png")
    plot_bar(viol_bw_pct, "QoS Violation Rate - Bandwidth", "%", "models/policy_qos_violation_bandwidth.png")
    plot_grouped_per_task(per_task_energy, "models/policy_energy_per_task.png")
    plot_network_usage(network_usage, "models/policy_network_usage.png")

    print("✅ Charts generated in models/:")
    for f in [
        "policy_energy_mean.png",
        "policy_energy_p95.png",
        "policy_qos_violation_latency.png",
        "policy_qos_violation_bandwidth.png",
        "policy_energy_per_task.png",
        "policy_network_usage.png",
    ]:
        print(f"  - models/{f}")


if __name__ == "__main__":
    main()
