"""
Demo script cho hệ thống IoT Network Selection với Decision Logic Algorithm.

Tạo các kịch bản mô phỏng thực tế để demonstare thuật toán MCDM.
Chạy: python demo_system.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.schemas import TaskState, NetworkState, NetworkConfig, DeviceState
from app.core.decision_logic import (
    select_best_network, calculate_cost, TASK_WEIGHTS, QOS_REQUIREMENTS
)


def print_header(title: str):
    """In header đẹp cho mỗi section"""
    print("\n" + "=" * 70)
    print(f"🔥 {title}")
    print("=" * 70)


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
        "Ethernet": NetworkConfig(name="Ethernet", energy_tx=0.3, energy_idle=5.0, energy_wakeup=0.0)
    }
    
    office_networks = [
        NetworkState(name="Wi-Fi", bandwidth=100.0, latency=10, is_available=True),
        NetworkState(name="5G", bandwidth=200.0, latency=15, is_available=True), 
        NetworkState(name="Ethernet", bandwidth=1000.0, latency=5, is_available=True)
    ]
    
    print("🏢 Thiết bị IoT trong văn phòng - 3 mạng khả dụng:")
    for net in office_networks:
        print(f"  📶 {net.name}: {net.bandwidth} Mbps, {net.latency}ms")
    
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
        "4G": NetworkConfig(name="4G", energy_tx=0.8, energy_idle=12.0, energy_wakeup=3.0),
        "5G": NetworkConfig(name="5G", energy_tx=1.2, energy_idle=15.0, energy_wakeup=5.0)
    }
    
    # Kịch bản A: Wi-Fi yếu
    print("\n📍 Vị trí A: Gần router Wi-Fi")
    good_wifi = [
        NetworkState(name="Wi-Fi", bandwidth=80.0, latency=8, is_available=True),
        NetworkState(name="4G", bandwidth=30.0, latency=50, is_available=True)
    ]
    
    for task in TaskState:
        best_net, cost = select_best_network(good_wifi, configs, task)
        print(f"  {task.value}: Chọn {best_net.name} (cost: {cost:.2f})")
    
    # Kịch bản B: Xa router, chỉ có cellular  
    print("\n📍 Vị trí B: Xa Wi-Fi, chỉ có cellular")
    cellular_only = [
        NetworkState(name="4G", bandwidth=25.0, latency=60, is_available=True),
        NetworkState(name="5G", bandwidth=150.0, latency=25, is_available=True)
    ]
    
    for task in TaskState:
        best_net, cost = select_best_network(cellular_only, configs, task)
        print(f"  {task.value}: Chọn {best_net.name} (cost: {cost:.2f})")
    
    # Kịch bản C: Mạng quá tải
    print("\n📍 Vị trí C: Tất cả mạng đều chậm (congested)")
    congested_nets = [
        NetworkState(name="Wi-Fi", bandwidth=5.0, latency=200, is_available=True),   # Quá tải
        NetworkState(name="4G", bandwidth=2.0, latency=300, is_available=True),     # Rất chậm
        NetworkState(name="5G", bandwidth=10.0, latency=100, is_available=True)     # Chậm
    ]
    
    for task in TaskState:
        try:
            best_net, cost = select_best_network(congested_nets, configs, task)
            print(f"  {task.value}: Chọn {best_net.name} (cost: {cost:.2f}) ⚠️  High cost!")
        except Exception as e:
            print(f"  {task.value}: ❌ {e}")


def demo_scenario_3_iot_sensors():
    """Kịch bản 3: Cảm biến IoT với yêu cầu tiết kiệm năng lượng cao"""
    print_header("KỊCH BẢN 3: CẢM BIẾN IOT - TIẾT KIỆM NĂNG LƯỢNG")
    
    configs = {
        "Wi-Fi": NetworkConfig(name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0),
        "BLE": NetworkConfig(name="BLE", energy_tx=0.05, energy_idle=1.0, energy_wakeup=0.1),     # Rất tiết kiệm
        "LoRa": NetworkConfig(name="LoRa", energy_tx=0.02, energy_idle=0.5, energy_wakeup=0.05)   # Cực tiết kiệm
    }
    
    sensor_networks = [
        NetworkState(name="Wi-Fi", bandwidth=50.0, latency=15, is_available=True),
        NetworkState(name="BLE", bandwidth=1.0, latency=50, is_available=True),
        NetworkState(name="LoRa", bandwidth=0.05, latency=1000, is_available=True)  # Rất chậm nhưng tiết kiệm
    ]
    
    print("🔋 Mạng cho cảm biến IoT (pin sạc khó):")
    for net in sensor_networks:
        config = configs[net.name]
        print(f"  📡 {net.name}: BW={net.bandwidth} Mbps, Energy_TX={config.energy_tx} mJ/KB")
    
    print("\n🧪 Lựa chọn mạng cho từng task:")
    
    for task in TaskState:
        best_net, cost = select_best_network(sensor_networks, configs, task)
        config = configs[best_net.name]
        
        print(f"\n📋 {task.value}:")
        print(f"  ✅ Chọn: {best_net.name}")
        print(f"  💰 Chi phí: {cost:.2f}")
        print(f"  ⚡ Energy TX: {config.energy_tx} mJ/KB")
        print(f"  📶 Bandwidth: {best_net.bandwidth} Mbps")
        
        # Kiểm tra xem có phải lựa chọn hợp lý không
        if task == TaskState.IDLE_MONITORING and best_net.name in ["BLE", "LoRa"]:
            print("  ✅ Hợp lý: Chọn mạng tiết kiệm cho IDLE")
        elif task == TaskState.DATA_BURST_ALERT and best_net.bandwidth >= 5.0:
            print("  ✅ Hợp lý: Đủ bandwidth cho DATA_BURST") 
        elif task == TaskState.VIDEO_STREAMING and best_net.bandwidth < 10.0:
            print("  ⚠️  Cảnh báo: Bandwidth có thể không đủ cho VIDEO")


def demo_real_world_device_simulation():
    """Mô phỏng thiết bị thực tế di chuyển qua nhiều vùng mạng"""
    print_header("MÔ PHỎNG THIẾT BỊ THỰC TẾ - DI CHUYỂN")
    
    configs = {
        "Wi-Fi": NetworkConfig(name="Wi-Fi", energy_tx=0.5, energy_idle=10.0, energy_wakeup=2.0),
        "5G": NetworkConfig(name="5G", energy_tx=1.2, energy_idle=15.0, energy_wakeup=5.0),
        "BLE": NetworkConfig(name="BLE", energy_tx=0.1, energy_idle=2.0, energy_wakeup=0.5)
    }
    
    # Giả lập thiết bị di chuyển qua 5 vị trí khác nhau
    locations = [
        {
            "name": "🏠 Tại nhà", 
            "position": (0, 0),
            "networks": [
                NetworkState(name="Wi-Fi", bandwidth=100.0, latency=5, is_available=True),
                NetworkState(name="5G", bandwidth=80.0, latency=20, is_available=True)
            ]
        },
        {
            "name": "🚗 Trên xe", 
            "position": (50, 25),
            "networks": [
                NetworkState(name="5G", bandwidth=150.0, latency=15, is_available=True)
            ]
        },
        {
            "name": "🏢 Văn phòng",
            "position": (100, 50), 
            "networks": [
                NetworkState(name="Wi-Fi", bandwidth=200.0, latency=8, is_available=True),
                NetworkState(name="BLE", bandwidth=1.0, latency=30, is_available=True)
            ]
        },
        {
            "name": "☕ Quán café",
            "position": (75, 100),
            "networks": [
                NetworkState(name="Wi-Fi", bandwidth=20.0, latency=50, is_available=True),  # WiFi công cộng chậm
                NetworkState(name="5G", bandwidth=100.0, latency=25, is_available=True)
            ]
        },
        {
            "name": "🌳 Công viên",
            "position": (25, 150), 
            "networks": [
                NetworkState(name="5G", bandwidth=60.0, latency=40, is_available=True),    # Sóng yếu
                NetworkState(name="BLE", bandwidth=0.5, latency=100, is_available=True)
            ]
        }
    ]
    
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