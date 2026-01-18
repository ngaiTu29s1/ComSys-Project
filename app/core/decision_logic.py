"""
Thuật toán cơ sở để tính toán chi phí lựa chọn mạng cho hệ thống IoT.

Sử dụng phương pháp MCDM (Multi-Criteria Decision Making) với hàm chi phí:
Cost = w_energy * Energy_Cost + w_qos * QoS_Penalty

Module này cung cấp các hàm tính toán để hỗ trợ việc ra quyết định
lựa chọn mạng tối ưu dựa trên trạng thái tác vụ hiện tại.
"""

from typing import Dict, Any
from app.models.schemas import TaskState, NetworkState, NetworkConfig
from app.core.constants import (
    TASK_WEIGHTS,
    QOS_REQUIREMENTS,
    QoSPenaltyCoefficients,
    get_task_data_size
)


def calculate_energy_cost(
    network_config: NetworkConfig,
    network_state: NetworkState,
    task: TaskState,
) -> float:
    """
    Tính chi phí năng lượng dựa trên thời gian truyền dữ liệu.

    Logic mới (time-based):
    1) throughput_mbps = network_state.bandwidth (clamp tối thiểu 0.01)
    2) time_tx_s = data_size(Mb) / throughput_mbps ; 1 KB = 0.008 Mb
    3) power_total_mw = power_tx + power_idle
    4) energy_tx_mj = power_total_mw * time_tx_s
    5) total_cost = energy_tx_mj + energy_wakeup
    """

    # 1) Throughput (Mbps) với ngưỡng tối thiểu tránh chia cho 0
    throughput_mbps = max(network_state.bandwidth, 0.01)

    # 2) Thời gian truyền (s) với data_size tính từ task (KB -> Mb)
    data_size_kb = get_task_data_size(task)
    data_size_mb = data_size_kb * 0.008  # 1 KB = 0.008 Mb
    time_tx_s = data_size_mb / throughput_mbps

    # 3) Tổng công suất (mW == mJ/s)
    power_total_mw = network_config.power_tx + network_config.power_idle

    # 4) Năng lượng truyền (mJ)
    energy_tx_mj = power_total_mw * time_tx_s

    # 5) Tổng chi phí năng lượng (mJ)
    total_cost = energy_tx_mj + network_config.energy_wakeup

    return float(total_cost)


def calculate_qos_penalty(network_state: NetworkState, task: TaskState) -> float:
    """
    Tính toán phí phạt QoS dựa trên yêu cầu của tác vụ.
    
    Args:
        network_state: Trạng thái mạng hiện tại
        task: Loại tác vụ cần thực hiện
        
    Returns:
        Phí phạt QoS (0 nếu đáp ứng, 1000 nếu không đáp ứng)
    """
    # Lấy yêu cầu QoS cho tác vụ này
    requirements = QOS_REQUIREMENTS.get(task)
    if not requirements:
        return 0.0  # Không có yêu cầu đặc biệt
    
    # Kiểm tra mạng có khả dụng không
    if requirements["must_be_available"] and not network_state.is_available:
        return QoSPenaltyCoefficients.UNAVAILABLE_PENALTY
    
    penalty = 0.0
    
    # Kiểm tra băng thông
    if network_state.bandwidth < requirements["min_bandwidth"]:
        bandwidth_deficit = requirements["min_bandwidth"] - network_state.bandwidth
        penalty += bandwidth_deficit * QoSPenaltyCoefficients.BANDWIDTH_DEFICIT_FACTOR
    
    # Kiểm tra độ trễ
    if network_state.latency > requirements["max_latency"]:
        latency_excess = network_state.latency - requirements["max_latency"]
        penalty += latency_excess * QoSPenaltyCoefficients.LATENCY_EXCESS_FACTOR
    
    # Nếu vi phạm nghiêm trọng, trả về penalty cao
    if penalty > QoSPenaltyCoefficients.SEVERE_VIOLATION_THRESHOLD:
        return QoSPenaltyCoefficients.UNAVAILABLE_PENALTY
    
    return penalty


def calculate_cost(network_state: NetworkState, 
                  network_config: NetworkConfig, 
                  task: TaskState) -> float:
    """
    Tính toán tổng chi phí lựa chọn mạng cho một tác vụ cụ thể.
    
    Sử dụng công thức MCDM:
    Total_Cost = w_energy * Energy_Cost + w_qos * QoS_Penalty
    
    Args:
        network_state: Trạng thái động của mạng
        network_config: Cấu hình tĩnh của mạng  
        task: Loại tác vụ cần thực hiện
        
    Returns:
        Tổng chi phí (số càng nhỏ càng tốt)
    """
    # Lấy trọng số cho tác vụ này
    weights = TASK_WEIGHTS.get(task)
    if not weights:
        raise ValueError(f"Không tìm thấy trọng số cho task: {task}")
    
    # Tính chi phí năng lượng
    energy_cost = calculate_energy_cost(network_config, network_state, task)
    
    # Tính phí phạt QoS
    qos_penalty = calculate_qos_penalty(network_state, task)
    
    # Tính tổng chi phí theo công thức MCDM
    total_cost = (weights["w_energy"] * energy_cost + 
                  weights["w_qos"] * qos_penalty)
    
    return total_cost


def select_best_network(available_networks: list[NetworkState],
                       network_configs: Dict[str, NetworkConfig], 
                       task: TaskState) -> tuple[NetworkState, float]:
    """
    Lựa chọn mạng tối ưu từ danh sách các mạng khả dụng.
    
    Args:
        available_networks: Danh sách mạng khả dụng
        network_configs: Dictionary mapping tên mạng -> cấu hình
        task: Tác vụ cần thực hiện
        
    Returns:
        Tuple (mạng được chọn, chi phí tương ứng)
        
    Raises:
        ValueError: Nếu không có mạng nào khả dụng hoặc không tìm thấy config
    """
    if not available_networks:
        raise ValueError("Không có mạng nào khả dụng")
    
    best_network = None
    min_cost = float('inf')
    min_energy = float('inf')
    
    for network in available_networks:
        # Lấy cấu hình tương ứng
        config = network_configs.get(network.name)
        if not config:
            print(f"Cảnh báo: Không tìm thấy config cho mạng {network.name}")
            continue
        
        # Tính chi phí
        cost = calculate_cost(network, config, task)
        energy = calculate_energy_cost(config, network, task)
        
        # Cập nhật mạng tốt nhất
        # Ưu tiên: cost thấp nhất; nếu gần bằng nhau (epsilon) thì chọn energy thấp hơn
        epsilon = 1e-9
        if cost < min_cost or (abs(cost - min_cost) < epsilon and energy < min_energy):
            min_cost = cost
            min_energy = energy
            best_network = network
    
    if best_network is None:
        raise ValueError("Không thể tìm thấy mạng phù hợp")
    
    return best_network, min_cost