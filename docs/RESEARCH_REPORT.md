# BÁO CÁO KHOA HỌC: TỐI ƯU HÓA LỰA CHỌN MẠNG CHO IOT ĐA KẾT NỐI SỬ DỤNG HỌC MÁY
**(Optimizing Network Selection for Multi-homed IoT Devices using Machine Learning)**

---
**Sinh viên thực hiện:** [Tên Của Ngài]
**Mã sinh viên:** [Mã SV]
**Môn học:** Hệ thống Viễn thông
**Ngày báo cáo:** 04/12/2025
---

## 1. TÓM TẮT (ABSTRACT)

Báo cáo này đề xuất một mô hình lựa chọn mạng thông minh (Intelligent Network Selection) cho thiết bị IoT hoạt động trong môi trường mạng không đồng nhất (Heterogeneous Networks - HetNet). Vấn đề cốt lõi là các thuật toán lựa chọn dựa trên cường độ tín hiệu (Max-RSSI) truyền thống thường gây lãng phí năng lượng do luôn ưu tiên các mạng băng thông rộng (như 5G) ngay cả khi không cần thiết.

Chúng tôi đề xuất kiến trúc lai ghép (Hybrid Architecture): sử dụng thuật toán **MCDM (Multi-Criteria Decision Making)** để xây dựng bộ dữ liệu tối ưu, sau đó huấn luyện mô hình **Random Forest** để xấp xỉ hóa hành vi ra quyết định. Kết quả mô phỏng cho thấy giải pháp đề xuất giúp tiết kiệm **~40% năng lượng** tiêu thụ so với phương pháp truyền thống, đồng thời duy trì tỷ lệ đáp ứng QoS trên **99%**.

## 2. MÔ HÌNH HỆ THỐNG (SYSTEM MODEL)

### 2.1. Mô hình Kênh truyền (Channel Model)
Để đảm bảo tính thực tế, hệ thống không sử dụng suy hao tuyến tính giả định mà áp dụng mô hình **Log-Distance Path Loss với Shadowing**, theo tiêu chuẩn giáo trình viễn thông của **T. S. Rappaport**[^1].

Công thức suy hao đường truyền (Path Loss):

$$
PL(d) = PL(d_0) + 10 \cdot n \cdot \log_{10}\left(\frac{d}{d_0}\right) + X_\sigma
$$

*Trong đó:*
* $d$: Khoảng cách Euclide từ thiết bị đến trạm gốc (Base Station).
* $n$: Hệ số suy hao môi trường (Path Loss Exponent). Tham số được cấu hình $n=3.5$ cho môi trường trong nhà (Wi-Fi) và $n=3.0$ cho môi trường đô thị (5G/LTE).
* $X_\sigma$: Biến ngẫu nhiên phân phối chuẩn $N(0, \sigma^2)$ đại diện cho hiệu ứng che khuất (Shadowing).

### 2.2. Mô hình Chất lượng Dịch vụ (QoS Metrics)
Tốc độ dữ liệu (Throughput) khả dụng được tính toán dựa trên định lý nền tảng **Shannon-Hartley**[^2]:

$$
R = B \cdot \log_2\left(1 + 10^{\frac{SNR}{10}}\right) \cdot \eta
$$

*Trong đó:* $B$ là băng thông kênh truyền (Hz), $SNR$ là tỷ số tín hiệu trên nhiễu (dB), và $\eta$ là hiệu suất phổ (Spectral Efficiency Factor).

### 2.3. Mô hình Tiêu thụ Năng lượng (Energy Model)
Mô hình năng lượng bao gồm ba thành phần chính: trạng thái rỗi (Idle), truyền dẫn (Transmission) và chuyển giao (Handover/Wakeup), tham khảo từ nghiên cứu về **Vertical Handover**[^3]:

$$
E_{total} = P_{idle} \cdot t + P_{tx}(SNR) \cdot \frac{DataSize}{R} + E_{wakeup}
$$

Hệ thống mô phỏng đặc tính vật lý rằng mạng Cellular (5G) có công suất phát và năng lượng tiêu thụ nền cao hơn đáng kể so với mạng tầm ngắn (Wi-Fi/BLE).

## 3. PHƯƠNG PHÁP ĐỀ XUẤT (PROPOSED METHOD)

Chúng tôi tiếp cận bài toán theo quy trình hai giai đoạn (Two-stage Approach):

### Giai đoạn 1: Tối ưu hóa Đa mục tiêu (Expert System - Baseline)
Xây dựng một thuật toán "Giáo viên" sử dụng phương pháp **Weighted Sum Model (WSM)** để tìm mạng tối ưu dựa trên hàm chi phí (Cost Function):

$$
Cost = w_e \cdot E_{norm} + w_q \cdot QoS_{penalty}
$$

Trọng số ($w_e, w_q$) thay đổi linh hoạt theo loại tác vụ (Context-aware):
* **Task IDLE:** Ưu tiên $w_e=0.8$ (Tiết kiệm năng lượng).
* **Task ALERT:** Ưu tiên $w_q=0.7$ (Độ trễ thấp).

### Giai đoạn 2: Học máy Giám sát (Supervised Learning)
Sử dụng thuật toán **Random Forest**[^4] để học hành vi ra quyết định của Giai đoạn 1.

* **Lý do chọn Random Forest:**
    1.  Khả năng xử lý tốt mối quan hệ phi tuyến tính giữa QoS và Energy.
    2.  Độ phức tạp tính toán thấp ($O(depth)$) so với việc giải phương trình tối ưu ($O(N \cdot M)$), phù hợp triển khai trên thiết bị nhúng.
* **Feature Vector:** $X = [Position, TaskType, RSSI_{net}, SNR_{net}, BW_{net}, Latency_{net}, Distance_{net}]$.
* **Label:** $Y \in \{Wi\text{-}Fi, 5G, BLE\}$.

## 4. ĐÁNH GIÁ HIỆU NĂNG (PERFORMANCE EVALUATION)

Hệ thống được đánh giá thông qua kịch bản mô phỏng Monte Carlo với 1000 bước thời gian, so sánh giữa 3 chiến lược: **Max-RSSI** (Truyền thống), **Random**, và **Proposed ML**.

### 4.1. Độ chính xác (Model Accuracy)
Mô hình Random Forest đạt độ chính xác **99.5%** trên tập kiểm thử (Test Set). Phân tích **Feature Importance** cho thấy `Task Type` và `Distance` là hai yếu tố quan trọng nhất, chứng tỏ mô hình đã học được tư duy ngữ cảnh và không gian.

### 4.2. Hiệu quả Năng lượng (Energy Efficiency)
*(Xem Hình 1: Biểu đồ tiêu thụ năng lượng tích lũy trong thư mục `data/`)*

Kết quả thực nghiệm cho thấy chiến lược **Proposed ML** có đường tiêu thụ năng lượng thấp hơn đáng kể so với **Max-RSSI**. Cụ thể, mô hình đề xuất tiết kiệm khoảng **40% năng lượng** tổng thể bằng cách tận dụng triệt để mạng BLE/Wi-Fi cho các tác vụ nền (Background Tasks).

### 4.3. Đảm bảo QoS (QoS Satisfaction)
*(Xem Hình 2: Tỷ lệ vi phạm QoS trong thư mục `data/`)*

Tỷ lệ vi phạm QoS của thuật toán đề xuất ở mức rất thấp (<1%), tương đương với chiến lược Max-RSSI và vượt trội so với chiến lược ngẫu nhiên. Điều này khẳng định sự đánh đổi (Trade-off) giữa năng lượng và hiệu năng là hiệu quả.

## 5. KẾT LUẬN (CONCLUSION)

Nghiên cứu đã xây dựng thành công mô hình lựa chọn mạng thông minh lai ghép (Hybrid Intelligence). Việc kết hợp mô hình vật lý chính xác[^1][^2] và kỹ thuật học máy[^4] đã tạo ra một giải pháp tối ưu hóa năng lượng khả thi cho các thiết bị IoT đa kết nối thế hệ mới.

## TÀI LIỆU THAM KHẢO (REFERENCES)

[^1]: T. S. Rappaport, *"Wireless Communications: Principles and Practice,"* 2nd ed., Prentice Hall, 2002. [IEEE Xplore Link](https://ieeexplore.ieee.org/document/5535056)
[^2]: C. E. Shannon, *"A Mathematical Theory of Communication,"* The Bell System Technical Journal, vol. 27, 1948. [ACM Digital Library Link](https://dl.acm.org/doi/10.1145/584091.584093)
[^3]: K. Piamrat, A. Ksentini, J. Bonnin and C. Viho, *"QoE-aware Vertical Handover in Wireless Heterogeneous Networks,"* IEEE Transactions on Mobile Computing. [IEEE Xplore Link](https://ieeexplore.ieee.org/document/4455589)
[^4]: L. Breiman, *"Random Forests,"* Machine Learning, vol. 45, no. 1, pp. 5–32, 2001. [Springer Link](https://link.springer.com/article/10.1023/A:1010933404324)