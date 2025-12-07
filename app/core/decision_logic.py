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


def calculate_energy_cost(network_config: NetworkConfig, 
                         network_state: NetworkState,
                         task: TaskState) -> float:
    """
    Tính toán chi phí năng lượng dự kiến cho một mạng và tác vụ.
    
    CÔNG THỨC ĐƠN GIẢN HÓA (Option A - Simplified):
    E_total = (energy_tx × DataSize) + E_wakeup
    
    Giả định: energy_tx (mJ/KB) ĐÃ BAO GỒM cả RF power + circuit overhead.
    Không cần nhân thêm với T_tx vì đã được normalize theo KB.
    
    Args:
        network_config: Cấu hình tĩnh của mạng
        network_state: Trạng thái động hiện tại (chứa bandwidth khả dụng)
        task: Loại tác vụ đang thực hiện
        
    Returns:
        Chi phí năng lượng (đơn vị: mJ)
    """
    # Lấy ước tính kích thước dữ liệu từ constants
    estimated_data_kb = get_task_data_size(task)
    
    # Năng lượng truyền (bao gồm RF + circuit)
    transmission_energy = estimated_data_kb * network_config.energy_tx  # mJ
    
    # Chi phí khởi động radio
    wakeup_energy = network_config.energy_wakeup  # mJ
    
    # Tổng chi phí năng lượng
    total_energy_mj = transmission_energy + wakeup_energy
    
    return total_energy_mj


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
    
    for network in available_networks:
        # Lấy cấu hình tương ứng
        config = network_configs.get(network.name)
        if not config:
            print(f"Cảnh báo: Không tìm thấy config cho mạng {network.name}")
            continue
        
        # Tính chi phí
        cost = calculate_cost(network, config, task)
        
        # Cập nhật mạng tốt nhất
        if cost < min_cost:
            min_cost = cost
            best_network = network
    
    if best_network is None:
        raise ValueError("Không thể tìm thấy mạng phù hợp")
    
    return best_network, min_cost