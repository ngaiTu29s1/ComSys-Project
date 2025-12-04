"""
Demo script cho hệ thống IoT Network Selection với Decision Logic Algorithm.

Tạo các kịch bản mô phỏng thực tế để demonstare thuật toán MCDM.
Chạy: python demo_system.py
"""

import sys
import os
import math
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.schemas import TaskState, NetworkState, NetworkConfig, DeviceState
from app.core.decision_logic import (
    select_best_network, calculate_cost, TASK_WEIGHTS, QOS_REQUIREMENTS
)
from app.services.network_physics import NetworkPhysics


def print_header(title: str):
    """In header đẹp cho mỗi section"""
    print("\n" + "=" * 70)
    print(f"🔥 {title}")
    print("=" * 70)


def create_network_state_from_distance(network_type: str, distance: float) -> NetworkState:
    """Create realistic NetworkState based on distance using physics model.
    
    Args:
        network_type: Type of network (Wi-Fi, 5G, BLE)
        distance: Distance from base station (meters)
    
    Returns:
        NetworkState with realistic QoS metrics
    """
    qos = NetworkPhysics.calculate_qos(network_type, distance)
    
    return NetworkState(
        name=network_type,
        bandwidth=round(qos["bandwidth"], 1),
        latency=qos["latency"],
        is_available=qos["is_available"]
    )


def demo_basic_algorithm():
    """Demo thuật toán cơ bản"""
    print_header("DEMO THUẬT TOÁN CƠ SỞ - MCDM")
    
    # Cấu hình networks
    configs = {
        "Wi-Fi": NetworkConfig(
            name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0
        ),
        "5G": NetworkConfig(
            name="5G", energy_tx=1.2, energy_idle=15.0, energy_wakeup=5.0
        ),
        "BLE": NetworkConfig(
            name="BLE", energy_tx=0.1, energy_idle=2.0, energy_wakeup=0.5
        )
    }
    
    print("📊 Cấu hình mạng:")
    for name, config in configs.items():
        print(f"  {name}: TX={config.energy_tx} mJ/KB, Idle={config.energy_idle} mW")
    
    print("\n🎯 Trọng số cho các tasks:")
    for task, weights in TASK_WEIGHTS.items():
        print(f"  {task.value}: Energy={weights['w_energy']}, QoS={weights['w_qos']}")
    
    print("\n📋 Yêu cầu QoS tối thiểu:")
    for task, req in QOS_REQUIREMENTS.items():
        print(f"  {task.value}: BW>={req['min_bandwidth']} Mbps, Latency<={req['max_latency']} ms")


def demo_scenario_1_office_environment():
    """Kịch bản 1: Môi trường văn phòng với nhiều mạng"""
    print_header("KỊCH BẢN 1: MÔI TRƯỜNG VĂN PHÒNG")
    
    # Setup
    configs = {
        "Wi-Fi": NetworkConfig(name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0),
        "5G": NetworkConfig(name="5G", energy_tx=1.2, energy_idle=15.0, energy_wakeup=5.0),
        "BLE": NetworkConfig(name="BLE", energy_tx=0.1, energy_idle=2.0, energy_wakeup=0.5)
    }
    
    # Device at office desk: close to Wi-Fi (30m), moderate 5G (80m), close to BLE beacon (15m)
    print("🏢 Thiết bị IoT tại bàn làm việc - Tính QoS dựa trên khoảng cách thực tế:")
    print("  📍 Wi-Fi router: 30m | 5G tower: 80m | BLE beacon: 15m\n")
    
    office_networks = [
        create_network_state_from_distance("Wi-Fi", 30),
        create_network_state_from_distance("5G", 80),
        create_network_state_from_distance("BLE", 15)
    ]
    
    print("📶 QoS metrics (calculated by physics model):")
    for net in office_networks:
        status = "✅" if net.is_available else "❌"
        print(f"  {status} {net.name}: {net.bandwidth} Mbps, {net.latency}ms")
    
    print("\n🧪 Test các tasks khác nhau:")
    
    for task in TaskState:
        print(f"\n📋 Task: {task.value}")
        
        try:
            best_net, cost = select_best_network(office_networks, configs, task)
            print(f"  ✅ Chọn: {best_net.name} (chi phí: {cost:.2f})")
            
            # Hiển thị chi phí của tất cả networks
            all_costs = []
            for net in office_networks:
                if net.name in configs:
                    net_cost = calculate_cost(net, configs[net.name], task)
                    all_costs.append((net.name, net_cost))
            
            all_costs.sort(key=lambda x: x[1])  # Sort by cost
            print("  📊 So sánh chi phí:")
            for name, cost in all_costs:
                status = "👑" if name == best_net.name else "  "
                print(f"    {status} {name}: {cost:.2f}")
                
        except Exception as e:
            print(f"  ❌ Lỗi: {e}")


def demo_scenario_2_mobile_environment():
    """Kịch bản 2: Thiết bị di động với mạng không ổn định"""
    print_header("KỊCH BẢN 2: THIẾT BỊ DI ĐỘNG - MẠNG KHÔNG ỔN ĐỊNH")
    
    configs = {
        "Wi-Fi": NetworkConfig(name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0),
        "5G": NetworkConfig(name="5G", energy_tx=1.2, energy_idle=15.0, energy_wakeup=5.0)
    }
    
    # Kịch bản A: Gần router Wi-Fi
    print("\n📍 Vị trí A: Gần router Wi-Fi (20m from Wi-Fi, 100m from 5G)")
    good_wifi = [
        create_network_state_from_distance("Wi-Fi", 20),
        create_network_state_from_distance("5G", 100)
    ]
    
    print("  📶 Available networks:")
    for net in good_wifi:
        if net.is_available:
            print(f"    {net.name}: {net.bandwidth} Mbps, {net.latency}ms")
    
    for task in TaskState:
        available = [n for n in good_wifi if n.is_available]
        if available:
            best_net, cost = select_best_network(available, configs, task)
            print(f"  {task.value}: Chọn {best_net.name} (cost: {cost:.2f})")
    
    # Kịch bản B: Xa router, chỉ có cellular
    print("\n📍 Vị trí B: Xa Wi-Fi, chỉ có cellular (200m from Wi-Fi, 50m from 5G)")
    cellular_only = [
        create_network_state_from_distance("Wi-Fi", 200),
        create_network_state_from_distance("5G", 50)
    ]
    
    print("  📶 Available networks:")
    for net in cellular_only:
        if net.is_available:
            print(f"    {net.name}: {net.bandwidth} Mbps, {net.latency}ms")
    
    for task in TaskState:
        available = [n for n in cellular_only if n.is_available]
        if available:
            best_net, cost = select_best_network(available, configs, task)
            print(f"  {task.value}: Chọn {best_net.name} (cost: {cost:.2f})")
    
    # Kịch bản C: Rất xa tất cả stations
    print("\n📍 Vị trí C: Ở rìa vùng phủ sóng (150m from Wi-Fi, 300m from 5G)")
    far_distance = [
        create_network_state_from_distance("Wi-Fi", 150),
        create_network_state_from_distance("5G", 300)
    ]
    
    print("  📶 Available networks:")
    available_nets = [n for n in far_distance if n.is_available]
    if available_nets:
        for net in available_nets:
            print(f"    {net.name}: {net.bandwidth} Mbps, {net.latency}ms")
    else:
        print("    ❌ No networks available!")
    
    for task in TaskState:
        try:
            if available_nets:
                best_net, cost = select_best_network(available_nets, configs, task)
                print(f"  {task.value}: Chọn {best_net.name} (cost: {cost:.2f}) ⚠️  Weak signal!")
            else:
                print(f"  {task.value}: ❌ No network available")
        except Exception as e:
            print(f"  {task.value}: ❌ {e}")


def demo_scenario_3_iot_sensors():
    """Kịch bản 3: Cảm biến IoT với yêu cầu tiết kiệm năng lượng cao"""
    print_header("KỊCH BẢN 3: CẢM BIẾN IOT - TIẾT KIỆM NĂNG LƯỢNG")
    
    configs = {
        "Wi-Fi": NetworkConfig(name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0),
        "BLE": NetworkConfig(name="BLE", energy_tx=0.05, energy_idle=1.0, energy_wakeup=0.1),     # Rất tiết kiệm
        "5G": NetworkConfig(name="5G", energy_tx=1.2, energy_idle=15.0, energy_wakeup=5.0)
    }
    
    # Sensor trong nhà: Wi-Fi (40m), BLE beacon (10m), 5G (120m)
    print("🔋 Cảm biến IoT trong nhà (pin sạc khó):")
    print("  📍 Wi-Fi: 40m | BLE beacon: 10m | 5G tower: 120m\n")
    
    sensor_networks = [
        create_network_state_from_distance("Wi-Fi", 40),
        create_network_state_from_distance("BLE", 10),
        create_network_state_from_distance("5G", 120)
    ]
    
    print("📡 QoS metrics (physics-based):")
    for net in sensor_networks:
        if net.is_available:
            config = configs[net.name]
            print(f"  ✅ {net.name}: BW={net.bandwidth} Mbps, Latency={net.latency}ms, Energy_TX={config.energy_tx} mJ/KB")
        else:
            print(f"  ❌ {net.name}: Out of range")
    
    print("\n🧪 Lựa chọn mạng cho từng task:")
    
    available = [n for n in sensor_networks if n.is_available]
    
    for task in TaskState:
        if available:
            best_net, cost = select_best_network(available, configs, task)
            config = configs[best_net.name]
            
            print(f"\n📋 {task.value}:")
            print(f"  ✅ Chọn: {best_net.name}")
            print(f"  💰 Chi phí: {cost:.2f}")
            print(f"  ⚡ Energy TX: {config.energy_tx} mJ/KB")
            print(f"  📶 Bandwidth: {best_net.bandwidth} Mbps")
            print(f"  🕐 Latency: {best_net.latency} ms")
            
            # Kiểm tra xem có phải lựa chọn hợp lý không
            if task == TaskState.IDLE_MONITORING and best_net.name == "BLE":
                print("  ✅ Hợp lý: Chọn BLE tiết kiệm năng lượng cho IDLE")
            elif task == TaskState.DATA_BURST_ALERT and best_net.bandwidth >= 5.0:
                print("  ✅ Hợp lý: Đủ bandwidth cho DATA_BURST") 
            elif task == TaskState.VIDEO_STREAMING and best_net.bandwidth < 10.0:
                print(f"  ⚠️  Cảnh báo: Bandwidth {best_net.bandwidth} Mbps có thể không đủ cho VIDEO")
        else:
            print(f"\n📋 {task.value}: ❌ No networks available")


def demo_real_world_device_simulation():
    """Mô phỏng thiết bị thực tế di chuyển qua nhiều vùng mạng"""
    print_header("MÔ PHỎNG THIẾT BỊ THỰC TẾ - DI CHUYỂN")
    
    configs = {
        "Wi-Fi": NetworkConfig(name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0),
        "5G": NetworkConfig(name="5G", energy_tx=1.2, energy_idle=15.0, energy_wakeup=5.0),
        "BLE": NetworkConfig(name="BLE", energy_tx=0.1, energy_idle=2.0, energy_wakeup=0.5)
    }
    
    # Base station positions (fixed)
    base_stations = {
        "wifi_home": (10, 10),
        "wifi_office": (100, 60),
        "5g_tower1": (0, 0),
        "5g_tower2": (80, 30),
        "ble_home": (5, 5),
        "ble_office": (95, 55)
    }
    
    # Device movement trajectory with distances calculated
    def calculate_distance(pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    # Giả lập thiết bị di chuyển qua 5 vị trí khác nhau
    device_positions = [
        {"name": "🏠 Tại nhà", "position": (15, 12)},
        {"name": "🚗 Trên xe", "position": (50, 25)},
        {"name": "🏢 Văn phòng", "position": (105, 58)},
        {"name": "☕ Quán café", "position": (75, 100)},
        {"name": "🌳 Công viên", "position": (25, 150)}
    ]
    
    locations = []
    for dev_pos in device_positions:
        # Calculate QoS based on real distances
        networks = []
        
        # Check Wi-Fi availability from both routers
        wifi_home_dist = calculate_distance(dev_pos["position"], base_stations["wifi_home"])
        wifi_office_dist = calculate_distance(dev_pos["position"], base_stations["wifi_office"])
        wifi_dist = min(wifi_home_dist, wifi_office_dist)
        wifi_qos = NetworkPhysics.calculate_qos("Wi-Fi", wifi_dist)
        if wifi_qos["is_available"]:
            networks.append(NetworkState(
                name="Wi-Fi",
                bandwidth=round(wifi_qos["bandwidth"], 1),
                latency=wifi_qos["latency"],
                is_available=True
            ))
        
        # Check 5G availability from both towers
        tower1_dist = calculate_distance(dev_pos["position"], base_stations["5g_tower1"])
        tower2_dist = calculate_distance(dev_pos["position"], base_stations["5g_tower2"])
        fiveg_dist = min(tower1_dist, tower2_dist)
        fiveg_qos = NetworkPhysics.calculate_qos("5G", fiveg_dist)
        if fiveg_qos["is_available"]:
            networks.append(NetworkState(
                name="5G",
                bandwidth=round(fiveg_qos["bandwidth"], 1),
                latency=fiveg_qos["latency"],
                is_available=True
            ))
        
        # Check BLE availability from both beacons
        ble_home_dist = calculate_distance(dev_pos["position"], base_stations["ble_home"])
        ble_office_dist = calculate_distance(dev_pos["position"], base_stations["ble_office"])
        ble_dist = min(ble_home_dist, ble_office_dist)
        ble_qos = NetworkPhysics.calculate_qos("BLE", ble_dist)
        if ble_qos["is_available"]:
            networks.append(NetworkState(
                name="BLE",
                bandwidth=round(ble_qos["bandwidth"], 1),
                latency=ble_qos["latency"],
                is_available=True
            ))
        
        locations.append({
            "name": dev_pos["name"],
            "position": dev_pos["position"],
            "networks": networks
        })
    
    # Tasks mà thiết bị cần thực hiện ở mỗi vị trí
    location_tasks = [
        TaskState.IDLE_MONITORING,    # Tại nhà
        TaskState.DATA_BURST_ALERT,   # Trên xe  
        TaskState.VIDEO_STREAMING,    # Văn phòng
        TaskState.DATA_BURST_ALERT,   # Quán café
        TaskState.IDLE_MONITORING     # Công viên
    ]
    
    print("🗺️  Thiết bị IoT di chuyển qua 5 vị trí:")
    
    total_cost = 0.0
    
    for i, (location, task) in enumerate(zip(locations, location_tasks)):
        print(f"\n📍 Vị trí {i+1}: {location['name']} {location['position']}")
        print(f"📋 Task: {task.value}")
        print(f"📶 Networks khả dụng: {[n.name for n in location['networks']]}")
        
        try:
            device_state = DeviceState(
                position=location['position'],
                current_task=task,
                available_networks=location['networks']
            )
            
            best_net, cost = select_best_network(
                device_state.available_networks, configs, device_state.current_task
            )
            
            total_cost += cost
            
            print(f"  ✅ Quyết định: Chọn {best_net.name}")
            print(f"  💰 Chi phí: {cost:.2f}")
            print(f"  📊 Tích lũy: {total_cost:.2f}")
            
        except Exception as e:
            print(f"  ❌ Lỗi: {e}")
    
    print(f"\n🎯 TỔNG KẾT:")
    print(f"💰 Tổng chi phí: {total_cost:.2f}")
    print(f"📍 Số vị trí: {len(locations)}")
    print(f"⚡ Chi phí trung bình/vị trí: {total_cost/len(locations):.2f}")


def main():
    """Chạy toàn bộ demo"""
    print("🚀 DEMO HỆ THỐNG IOT NETWORK SELECTION")
    print("Thuật toán: Multi-Criteria Decision Making (MCDM)")
    print("Công thức: Cost = w_energy * Energy_Cost + w_qos * QoS_Penalty")
    
    demo_basic_algorithm()
    demo_scenario_1_office_environment() 
    demo_scenario_2_mobile_environment()
    demo_scenario_3_iot_sensors()
    demo_real_world_device_simulation()
    
    print_header("KẾT LUẬN")
    print("🎉 Demo hoàn tất!")
    print("\n✅ Thuật toán MCDM hoạt động hiệu quả:")
    print("  - Tự động chọn mạng tiết kiệm năng lượng cho IDLE")
    print("  - Ưu tiên QoS cho DATA_BURST và VIDEO_STREAMING")
    print("  - Xử lý được nhiều kịch bản thực tế")
    print("  - Có thể mở rộng với thêm loại mạng và tasks")
    
    print("\n📈 Bước tiếp theo:")
    print("  1. Thu thập dữ liệu từ thuật toán này")
    print("  2. Huấn luyện mô hình Random Forest")
    print("  3. So sánh hiệu suất ML vs Rule-based")
    print("  4. Tích hợp vào hệ thống IoT thực tế")


if __name__ == "__main__":
    main()