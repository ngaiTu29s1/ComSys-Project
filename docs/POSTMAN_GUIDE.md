# IoT Network Selection - Postman Collection Guide

## 📥 Import Collection

1. **Mở Postman**
2. **Import Collection**:
   - Click `Import` button
   - Choose `File` → Select `docs/IoT-Network-Selection.postman_collection.json`
   - Hoặc drag & drop file vào Postman

3. **Set Environment Variables**:
   - Collection sử dụng variable `{{baseUrl}}`
   - Default: `http://localhost:8000`
   - Có thể thay đổi trong Collection Variables

## 🚀 Quick Start Testing

### Bước 1: Khởi động API Server
```bash
# Terminal 1: Start server
conda activate comsys-project
uvicorn app.main:app --reload --port 8000
```

### Bước 2: Test theo thứ tự
```
1️⃣ Health Check          ← Kiểm tra API hoạt động
2️⃣ System Status         ← Xem trạng thái hệ thống  
3️⃣ Run Simulation Step   ← Test simulation engine
4️⃣ Make Decision - IDLE  ← Test MCDM algorithm
5️⃣ Integrated Workflow   ← Test end-to-end
```

## 📋 Collection Structure

### 🏥 **1. Health & Status**
- **Health Check**: Kiểm tra API có running không
- **Root Info**: Thông tin cơ bản về endpoints
- **System Status**: Trạng thái chi tiết simulation và network configs

**Expected**: Status 200, response time < 5s

### 🎮 **2. Simulation Engine** 
- **Run Simulation Step**: Di chuyển thiết bị IoT, cập nhật networks
- **Get Current State**: Xem trạng thái hiện tại (không thay đổi)
- **Reset Simulation**: Reset về vị trí mới (x=100, y=200)

**Test Cases**:
- Device movement trên map 1000x1000
- Network availability theo khoảng cách
- Task state transitions

### 🧠 **3. Network Decision Making**

#### **IDLE_MONITORING Task**
```json
{
  "position": [250, 350],
  "current_task": "IDLE_MONITORING", 
  "available_networks": [
    {"name": "Wi-Fi", "bandwidth": 50.0, "latency": 15},
    {"name": "BLE", "bandwidth": 1.0, "latency": 50},
    {"name": "5G", "bandwidth": 120.0, "latency": 20}
  ]
}
```
**Expected Winner**: BLE (energy efficiency priority)

#### **DATA_BURST_ALERT Task**
```json
{
  "current_task": "DATA_BURST_ALERT",
  "available_networks": [
    {"name": "Wi-Fi", "bandwidth": 80.0, "latency": 12},
    {"name": "4G", "bandwidth": 25.0, "latency": 45},
    {"name": "BLE", "bandwidth": 1.0, "latency": 60}
  ]
}
```
**Expected Winner**: Wi-Fi (BLE fails min 5 Mbps requirement)

#### **VIDEO_STREAMING Task**
```json
{
  "current_task": "VIDEO_STREAMING",
  "available_networks": [
    {"name": "Wi-Fi", "bandwidth": 100.0, "latency": 8},
    {"name": "5G", "bandwidth": 200.0, "latency": 15},
    {"name": "4G", "bandwidth": 15.0, "latency": 80}
  ]
}
```
**Expected Winner**: 5G (4G fails min 25 Mbps requirement)

#### **Edge Cases**
- **No Networks**: Empty `available_networks` → HTTP 400 error
- **Poor QoS**: All networks fail QoS requirements → Chọn best available với high cost

### 🔄 **4. Integrated Workflows**
- **Simulation Step + Decision**: Chạy simulation → Tự động quyết định network
- One-call API cho production workflows

## 📊 Response Analysis

### Simulation Step Response
```json
{
  "step_number": 123,
  "device_state": {
    "position": [456, 789],
    "current_task": "DATA_BURST_ALERT", 
    "available_networks": [...]
  },
  "simulation_info": {
    "networks_count": 2,
    "networks_list": ["Wi-Fi", "5G"]
  }
}
```

### Decision Response
```json
{
  "optimal_network": "Wi-Fi",
  "optimal_cost": 12.45,
  "device_info": {...},
  "all_network_costs": {
    "Wi-Fi": 12.45,
    "5G": 18.23,
    "BLE": 25.67
  },
  "cost_analysis": {...},
  "decision_summary": {
    "total_networks_evaluated": 3,
    "cost_difference": 13.22,
    "algorithm": "MCDM_Energy_QoS"
  }
}
```

## 🧪 Advanced Testing

### Performance Testing
- Run multiple simulation steps liên tiếp
- Measure response times
- Check memory usage consistency

### Error Handling
- Test với invalid task states
- Test với negative coordinates
- Test với malformed JSON

### Algorithm Validation
- Verify cost calculation logic
- Check QoS penalty implementation
- Validate energy vs QoS trade-offs

## 🔍 Debugging Tips

### Console Logs
- Postman Console tab shows request/response logs
- Pre-request và Test scripts log detailed info
- Response body preview for large JSON

### Common Issues
1. **Connection Refused**: API server not running
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. **404 Not Found**: Check endpoint URLs match exactly

3. **422 Validation Error**: Check request body JSON format

4. **500 Internal Server Error**: Check server logs for Python errors

### Validation Checklist
- [ ] All health endpoints return 200
- [ ] Simulation steps advance device position
- [ ] Decision algorithm selects expected networks
- [ ] Error cases return appropriate HTTP codes
- [ ] Response times < 5 seconds
- [ ] JSON schema validation passes

## 📈 Performance Expectations

**Good Performance**:
- Health Check: < 100ms
- Simulation Step: < 500ms  
- Decision Making: < 1000ms
- Integrated Workflow: < 1500ms

**Load Testing** (if needed):
- Run collection with Collection Runner
- Set iterations = 50-100
- Monitor response times và error rates

## 🎯 Production Checklist

Before deploying:
- [ ] All test cases pass
- [ ] Performance meets requirements  
- [ ] Error handling works correctly
- [ ] Documentation matches API behavior
- [ ] Edge cases handled gracefully

---

**Happy Testing! 🚀**

Import collection và follow workflow testing để validate toàn bộ IoT Network Selection System.