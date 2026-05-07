|               |               | ĐẠI HỌC          | BÁCH KHOA      | HÀ          | NỘI          |
| ------------- | ------------- | ---------------- | -------------- | ----------- | ------------ |
|               |               | ENERGY-EFFICIENT |                |             | AND          |
| CONTEXT-AWARE |               |                  | NETWORK        |             | SELECTION    |
| IN            | HETEROGENEOUS |                  |                | NETWORKS    |              |
|               | Sinh          | viên thực hiện:  | Nguyễn         | Trọng Phúc  | 20224099     |
|               |               |                  | Phạm           | Đăng Bách   | 20223871     |
|               |               |                  | Trần Tuấn      | Tú 20223819 |              |
|               | Giảng         | viên hướng       | dẫn: PGS. TS.  | Nguyễn      | Thành Chuyên |
|               | Bộ môn:       |                  | Hệ thống       | viễn thông  |              |
|               | Mã            | lớp học:         | 163175         |             |              |
|               | Trường:       |                  | Điện -         | Điện tử     |              |
|               |               |                  | HÀ NỘI, 1/2026 |             |              |

| Phân công  | nhiệm | vụ       | chi tiết | các thành | viên      | trong  | nhóm: |     |     |            |
| ---------- | ----- | -------- | -------- | --------- | --------- | ------ | ----- | --- | --- | ---------- |
| Thành viên |       |          |          |           | Nhiệm     | vụ chi | tiết  |     |     |            |
| Trần Tuấn  | Tú    |          |          |           |           |        |       |     |     |            |
|            |       | • Nghiên | cứu      | mô        | hình năng | lượng  | và    | hàm | chi | phí tối ưu |
(Cost).
|     |     | • Áp dụng | kiến   | trúc    | Student-Teacher; |        |       | nghiên | cứu       | thuật toán |
| --- | --- | --------- | ------ | ------- | ---------------- | ------ | ----- | ------ | --------- | ---------- |
|     |     | Random    | Forest | và      | xây dựng         | vector | đặc   | trưng  | 18-D.     |            |
|     |     | • Huấn    | luyện  | mô hình | AI,              | kiểm   | chứng | số     | liệu thực | nghiệm     |
|     |     | và đánh   | giá    | hiệu    | năng.            |        |       |        |           |            |
Nguyễn Trọng
|     |     | • Nghiên | cứu | phương | trình | toán | học mô | hình | suy | hao Log- |
| --- | --- | -------- | --- | ------ | ----- | ---- | ------ | ---- | --- | -------- |
Phúc
Distance.
Phạm Đăng
Bách
|     |     | • Nghiên | cứu      | hàm  | xấp xỉ  | Sigmoid                       | cho   | tỉ lệ      | mất     | gói (PLR) |
| --- | --- | -------- | -------- | ---- | ------- | ----------------------------- | ----- | ---------- | ------- | --------- |
|     |     | và mô    | hình hóa | độ   | trễ BLE | dựa                           | trên  | Connection |         | Interval. |
|     |     | • Làm    | báo cáo  | tổng | hợp đề  | tài.                          |       |            |         |           |
|     |     |          |          |      |         |                               | Thông | tin        | liên hệ | của nhóm: |
|     |     |          |          |      | Email:  | phuc.nt224099@sis.hust.edu.vn |       |            |         |           |
2

MỤC LỤC
| CHƯƠNG | 1. TỔNG           | QUAN       | VÀ MÔ HÌNH | HÓA | HỆ THỐNG | 1   |
| ------ | ----------------- | ---------- | ---------- | --- | -------- | --- |
| 1 Đặt  | vấn đề và Động    | lực nghiên | cứu        |     |          | 1   |
| 2 Mô   | hình hóa hệ thống |            |            |     |          | 2   |
2.1 Thiết lập môi trường mô phỏng . . . . . . . . . . . . . . . . . . . 3
2.2 Tham số và biến số mạng . . . . . . . . . . . . . . . . . . . . . . 3
| 3 Mô | hình vật lý kênh | truyền |     |     |     | 3   |
| ---- | ---------------- | ------ | --- | --- | --- | --- |
3.1 Mô hình suy hao đường truyền . . . . . . . . . . . . . . . . . . . 3
3.2 Chất lượng tín hiệu thu và Mô hình tỷ lệ mất gói . . . . . . . . . . 4
3.3 Mô hình độ trễ tổng hợp . . . . . . . . . . . . . . . . . . . . . . 5
| 4 Mô | hình năng lượng | và chất | lượng dịch | vụ (QoS) |     | 6   |
| ---- | --------------- | ------- | ---------- | -------- | --- | --- |
4.1 Băng thông thực tế và đặc thù tác vụ . . . . . . . . . . . . . . . . 6
4.2 Mô hình tiêu thụ năng lượng . . . . . . . . . . . . . . . . . . . . 6
| CHƯƠNG   | 2. PHƯƠNG     | PHÁP   | NGHIÊN      | CỨU ĐỀ | XUẤT | 8   |
| -------- | ------------- | ------ | ----------- | ------ | ---- | --- |
| 1 Cơ chế | ra quyết định | đa mục | tiêu (MCDM) |        |      | 8   |
1.1 Hàm chi phí tổng quát . . . . . . . . . . . . . . . . . . . . . . . . 8
1.2 Cơ chế tính toán thành phần Penalty . . . . . . . . . . . . . . . . 8
| 2 Kiến | trúc Trí tuệ | nhân tạo đề | xuất |     |     | 9   |
| ------ | ------------ | ----------- | ---- | --- | --- | --- |
2.1 Biện luận lựa chọn thuật toán Random Forest . . . . . . . . . . . 9
2.2 Quy trình thu thập dữ liệu . . . . . . . . . . . . . . . . . . . . . . 10
2.3 Kỹ thuật đặc trưng (Feature Engineering) . . . . . . . . . . . . . 11
2.4 Huấn luyện và Kiểm chứng . . . . . . . . . . . . . . . . . . . . . 12
| CHƯƠNG | 3. KẾT | QUẢ THỰC | NGHIỆM | VÀ PHÂN | TÍCH | 14  |
| ------ | ------ | -------- | ------ | ------- | ---- | --- |

| 1 Hiệu | quả tối ưu | năng lượng |     |     | 14  |
| ------ | ---------- | ---------- | --- | --- | --- |
1.1 Phân tích mức tiêu thụ năng lượng trung bình . . . . . . . . . . . 14
1.2 Cơ chế tối ưu thông minh . . . . . . . . . . . . . . . . . . . . . . 14
1.3 Trình bày kết quả đồ thị . . . . . . . . . . . . . . . . . . . . . . . 14
| 2 Đảm   | bảo QoS      |       |                   |            | 15  |
| ------- | ------------ | ----- | ----------------- | ---------- | --- |
| CHƯƠNG  | 4. KẾT       | LUẬN  | VÀ HƯỚNG          | PHÁT TRIỂN | 17  |
| 1 Kết   | luận         |       |                   |            | 17  |
| 2 Hạn   | chế hiện tại |       |                   |            | 17  |
| 3 Hướng | phát triển   | tương | lai (Scalability) |            | 17  |

| CHƯƠNG | 1.     | TỔNG    | QUAN |            | VÀ MÔ | HÌNH | HÓA | HỆ THỐNG |
| ------ | ------ | ------- | ---- | ---------- | ----- | ---- | --- | -------- |
| 1 Đặt  | vấn đề | và Động |      | lực nghiên |       | cứu  |     |          |
Trong bối cảnh bùng nổ của kỷ nguyên Internet vạn vật, xu hướng tích hợp
đa kết nối (Multi-homed IoT) đang trở thành một lộ trình phát triển tất yếu. Việc
các thiết bị IoT sở hữu khả năng truy cập mạng thông qua nhiều giao thức và giao
diện truyền dẫn khác nhau không chỉ tăng cường tính linh hoạt mà còn đảm bảo sự
| ổn định | của kết nối | trong | các môi | trường | biến | động. |     |     |
| ------- | ----------- | ----- | ------- | ------ | ---- | ----- | --- | --- |
Tuy nhiên, việc quản lý và khai thác hiệu quả các hệ thống đa kết nối này vẫn
| đối mặt | với những | thách | thức | đáng kể: |     |     |     |     |
| ------- | --------- | ----- | ---- | -------- | --- | --- | --- | --- |
• Hạn chế của thuật toán truyền thống: Các cơ chế lựa chọn mạng phổ
biến hiện nay, điển hình là thuật toán dựa trên cường độ tín hiệu nhận
được lớn nhất (Max-RSSI), thường chỉ tập trung vào chất lượng đường
truyền vật lý mà bỏ qua yếu tố tiêu thụ năng lượng – một chỉ số sinh tồn
|     | đối với các | thiết | bị IoT | hoạt | động bằng | pin. |     |     |
| --- | ----------- | ----- | ------ | ---- | --------- | ---- | --- | --- |
• Sự thiếu đồng bộ trong điều phối: Hiện đang tồn tại một khoảng cách
lớn giữa yêu cầu đặc thù của từng tác vụ (Task Context) và khả năng đáp
ứng thực tế của hạ tầng mạng. Việc thiếu một cơ chế điều phối thông
minh dẫn đến tình trạng lãng phí tài nguyên mạng hoặc không đáp ứng
|     | được các | tiêu chuẩn |     | kỹ thuật | cần thiết | cho từng | loại | dữ liệu. |
| --- | -------- | ---------- | --- | -------- | --------- | -------- | ---- | -------- |
Xuất phát từ những thực trạng trên, nghiên cứu này tập trung vào mục tiêu
xây dựng một bộ máy ra quyết định (Decision Engine) tối ưu với các khả năng cốt
lõi sau:
• Tối ưu hóa năng lượng: Thiết lập cơ chế cân bằng thông minh nhằm
duy trì mức tiêu thụ năng lượng ở ngưỡng thấp nhất có thể, từ đó kéo dài
|     | tuổi thọ | vận hành | của | thiết bị. |     |     |     |     |
| --- | -------- | -------- | --- | --------- | --- | --- | --- | --- |
• Đảm bảo chất lượng dịch vụ (QoS): Đáp ứng nghiêm ngặt các ngưỡng
chấtlượngdịchvụkhácnhautùytheođặcthùcủatừngloạitácvụcụthể
như truyền tải video (đòi hỏi băng thông), cảnh báo khẩn cấp (đòi hỏi độ
|     | trễ thấp) | hoặc | giám | sát định | kỳ (đòi | hỏi sự ổn | định). |     |
| --- | --------- | ---- | ---- | -------- | ------- | --------- | ------ | --- |
1

|      |          | Hình     | 1.1 Mô hình | hệ thống | IoT đa        | kết nối   |
| ---- | -------- | -------- | ----------- | -------- | ------------- | --------- |
|      | Hình     | 1.2 Bảng | các giá     | trị mặc  | định của từng | loại mạng |
| 2 Mô | hình hóa | hệ       | thống       |          |               |           |
Trong phần này, chúng tôi trình bày các thiết lập về môi trường mô phỏng và
các tham số mạng cơ sở được sử dụng để đánh giá hiệu năng của hệ thống ra quyết
định.
2

2.1 Thiết lập môi trường mô phỏng
Để phục vụ cho việc thực nghiệm và đánh giá thuật toán, một môi trường mô
phỏng không gian đã được xây dựng. Cụ thể, môi trường được thiết lập dựa trên
một bản đồ mô phỏng có kích thước 1000×1000 pixels. Trong không gian này, hệ
thống bố trí tổng cộng 12 trạm phát sóng (Base Stations/Access Points) tại các vị
trí cố định để đảm bảo vùng phủ sóng cho các thiết bị di động.
Cấu trúc hạ tầng mạng bao gồm sự kết hợp của ba loại công nghệ truyền dẫn
phổ biến, đại diện cho các đặc tính vật lý khác nhau:
• 04 trạm phát sóng mạng di động thế hệ thứ năm (5G).
• 04 trạm phát sóng mạng không dây nội bộ (Wi-Fi).
• 04 trạm phát sóng Bluetooth năng lượng thấp (BLE).
2.2 Tham số và biến số mạng
Các tham số mạng được thiết lập dựa trên các tiêu chuẩn kỹ thuật thực tế để
đảm bảo tính khách quan của mô hình. Các thông số cố định bao gồm băng thông
(B), công suất phát (P ) và độ trễ cơ sở (Base Latency) cho từng loại hình kết nối
tx
(5G, Wi-Fi, BLE).
Loại mạng B (MHz) P (dBm) Base Latency (ms)
tx
5G 100 43 10
WIFI 20 20 5
BLE 2 0 20
Bảng 2.1 Thông số mạng cố định cho các loại hình kết nối
Bên cạnh các thông số cố định, mô hình còn xem xét yếu tố biến động quan
trọng nhất trong hệ thống di động là khoảng cách (d) từ thiết bị IoT đến các trạm
phátsóng. Biếnsốnàyđóngvaitròquyếtđịnhtrongviệctínhtoánsuyhaotínhiệu
và xác định chất lượng đường truyền thực tế tại từng thời điểm.
3 Mô hình vật lý kênh truyền
3.1 Mô hình suy hao đường truyền
Để đánh giá chính xác chất lượng kết nối và mức tiêu thụ năng lượng trong
môi trường thực tế, hệ thống sử dụng mô hình suy hao Log-Distance. Đây là mô
hình phổ biến để ước tính sự suy giảm công suất tín hiệu theo khoảng cách truyền
dẫn trong các môi trường có vật cản và nhiễu shadowing.
3

Công thức tổng quát của mô hình suy hao đường truyền được xác định như
sau:
|     |     |     |            |     |     |          |     | (cid:18) d | (cid:19) |     |       |
| --- | --- | --- | ---------- | --- | --- | -------- | --- | ---------- | -------- | --- | ----- |
|     |     |     | PL(d)=PL(d |     |     | )+10nlog |     |            | +σ       |     | PT3.1 |
|     |     |     |            |     |     | 0        |     | 10         |          | sh  |       |
d
0
Trong đó, các thành phần của công thức được định nghĩa cụ thể:
• d: KhoảngcáchthựctếgiữathiếtbịIoTvàtrạmphátsóng(đơnvị: mét).
|     | •   | d : Khoảng | cách | tham | chiếu, | được | thiết | lập | mặc | định là 1m. |     |
| --- | --- | ---------- | ---- | ---- | ------ | ---- | ----- | --- | --- | ----------- | --- |
0
• PL(d ): Suyhaotạikhoảngcáchthamchiếu, đượctínhtoándựatrêntần
0
|     |     | số vận | hành | f và tốc | độ  | ánh sáng | c theo | công | thức: |                   |     |
| --- | --- | ------ | ---- | -------- | --- | -------- | ------ | ---- | ----- | ----------------- | --- |
|     |     |        |      |          |     |          |        |      |       | (cid:18) (cid:19) |     |
4π
|     |     |     | PL(d )=20log |     | (d  | )+20log |     | (f)+20log |     |      |       |
| --- | --- | --- | ------------ | --- | --- | ------- | --- | --------- | --- | ---- | ----- |
|     |     |     | 0            |     |     | 0       |     |           |     |      | PT3.2 |
|     |     |     |              |     | 10  |         |     | 10        |     | 10 c |       |
• n: Hệ số suy hao môi trường (Path Loss Exponent), phản ánh mức độ
|     |     | suy giảm | tín | hiệu | tùy thuộc | vào | địa hình | cụ  | thể. |     |     |
| --- | --- | -------- | --- | ---- | --------- | --- | -------- | --- | ---- | --- | --- |
• σ : Nhiễu shadowing ngẫu nhiên, đại diện cho hiện tượng che chắn của
sh
|     |     | các vật | thể trong | môi | trường | mô  | phỏng. |     |     |     |     |
| --- | --- | ------- | --------- | --- | ------ | --- | ------ | --- | --- | --- | --- |
Dựa trên các thông số kỹ thuật của từng loại hình mạng truyền dẫn, các giá
| trị thực | nghiệm |          | được thiết | lập  | trong   | mô hình | như     | sau: |      |              |     |
| -------- | ------ | -------- | ---------- | ---- | ------- | ------- | ------- | ---- | ---- | ------------ | --- |
|          |        |          | Loại       | mạng | PL(d    | )       | (dB)    | n    | σ    | (dB)         |     |
|          |        |          |            |      |         | 0       |         |      | sh   |              |     |
|          |        |          |            | 5G   |         | 44      |         | 3.0  | 2.5  |              |     |
|          |        |          |            | WIFI |         | 40      |         | 3.5  | 2.0  |              |     |
|          |        |          |            | BLE  |         | 40      |         | 3.5  | 1.5  |              |     |
|          |        | Bảng 3.2 | Thông      | số   | mô hình | suy     | hao cho | các  | loại | mạng kết nối |     |
Việc áp dụng mô hình này cho phép "Decision Engine" dự đoán được cường
độ tín hiệu và chất lượng kênh truyền một cách chính xác, từ đó đưa ra các quyết
định lựa chọn mạng tối ưu về cả năng lượng và hiệu năng truyền tải dữ liệu.
| 3.2 | Chất | lượng | tín | hiệu | thu và | Mô  | hình | tỷ lệ | mất | gói |     |
| --- | ---- | ----- | --- | ---- | ------ | --- | ---- | ----- | --- | --- | --- |
Chất lượng tín hiệu tại thiết bị thu là yếu tố tiên quyết ảnh hưởng đến hiệu
năng của hệ thống. Cường độ tín hiệu nhận được (RSSI) và Tỷ số tín hiệu trên
| nhiễu | (SNR) | được  | xác    | định | như sau: |      |        |        |     |     |       |
| ----- | ----- | ----- | ------ | ---- | -------- | ---- | ------ | ------ | --- | --- | ----- |
|       | •     | Cường | độ tín | hiệu | nhận     | được | (dBm): |        |     |     |       |
|       |       |       |        |      | RSSI     | =P   | =P     | −PL(d) |     |     | PT3.3 |
|       |       |       |        |      |          |      | rx     | tx     |     |     |       |
4

|     | • Tỷ | số tín | hiệu | trên | nhiễu | (dB):      |     |     |     |       |
| --- | ---- | ------ | ---- | ---- | ----- | ---------- | --- | --- | --- | ----- |
|     |      |        |      |      |       | SNR=RSSI−N |     |     |     | PT3.4 |
0
|     | Trong |     | đó, N là | nhiễu | nền | cố định của | môi | trường | truyền dẫn. |     |
| --- | ----- | --- | -------- | ----- | --- | ----------- | --- | ------ | ----------- | --- |
0
Để mô hình hóa độ tin cậy của kênh truyền, nghiên cứu sử dụng hàm xấp xỉ
Logistic để tính toán Tỷ lệ mất gói (Packet Loss Rate - PLR). Mô hình này phản
| ánh | chính xác | sự  | sụt giảm | chất | lượng | mạng khi | tín hiệu | yếu | đi: |     |
| --- | --------- | --- | -------- | ---- | ----- | -------- | -------- | --- | --- | --- |
1
|     |     |     |     | PLR= |               |     |     |     |     | PT3.5 |
| --- | --- | --- | --- | ---- | ------------- | --- | --- | --- | --- | ----- |
|     |     |     |     |      | 1+ek·(SNR−SNR |     |     | )   |     |       |
thresh
Trong đó, SNR là ngưỡng mà tại đó PLR đạt mức 50%, và k là hệ số quyết
threshold
định tốc độ suy giảm chất lượng. Trong thực tế, ngay cả khi điều kiện sóng tốt
nhất, vẫn tồn tại nhiễu ngẫu nhiên gây mất gói; do đó hệ thống thiết lập mức sàn
| (Clamp) | cho     | PLR  | là 0.1%.    |      |         |            |        |      |            |     |
| ------- | ------- | ---- | ----------- | ---- | ------- | ---------- | ------ | ---- | ---------- | --- |
|         |         |      | Loại        | mạng | N       | (dB) k     | SNR    | (dB) |            |     |
|         |         |      |             |      | 0       |            | thresh |      |            |     |
|         |         |      | 5G          |      | -95     | 1          |        | 5    |            |     |
|         |         |      | WIFI        |      | -90     | 1          |        | 10   |            |     |
|         |         |      | BLE         |      | -90     | 1          |        | 8    |            |     |
|         |         | Bảng | 3.3 Thông   | số   | mô hình | chất lượng | tín    | hiệu | và mất gói |     |
| 3.3     | Mô hình |      | độ trễ tổng |      | hợp     |            |        |      |            |     |
Độ trễ tổng hợp (Lat ) được cấu thành từ độ trễ vật lý cố định và độ trễ
total
| phát | sinh do | cơ chế | truyền | lại  | tại lớp            | MAC khi xảy | ra  | mất gói:    |     |       |
| ---- | ------- | ------ | ------ | ---- | ------------------ | ----------- | --- | ----------- | --- | ----- |
|      |         | Lat    | =Lat   |      | +(PLR·100·Overhead |             |     |             | )   | PT3.6 |
|      |         |        | total  | base |                    |             |     | per_percent |     |       |
|      | Trong   | đó:    |        |      |                    |             |     |             |     |       |
• Lat : Độ trễ vật lý cố định (Propagation + Processing delay) của từng
base
|     | chuẩn      |     | mạng. |     |                                           |     |     |     |     |     |
| --- | ---------- | --- | ----- | --- | ----------------------------------------- | --- | --- | --- | --- | --- |
|     | • Overhead |     |       | :   | HệsốtrễphátsinhdocơchếtruyềnlạitạilớpMAC. |     |     |     |     |     |
per_percent
Trong hệ thống này, cứ 1% mất gói sẽ gây thêm 10 ms trễ để gửi lại gói
tin đó.
Ý nghĩa của mô hình này cho thấy khi thiết bị di chuyển ra xa trạm phát, giá trị
SNR giảm dẫn đến PLR tăng theo hàm mũ, khiến tổng độ trễ hệ thống vọt lên cực
nhanh.
5

|     |     |     |     |     | Loại | mạng | Lat | (ms) |     |     |     |     |
| --- | --- | --- | --- | --- | ---- | ---- | --- | ---- | --- | --- | --- | --- |
base
|     |      |       |      |        | 5G        |         |         | 10      |       |          |     |     |
| --- | ---- | ----- | ---- | ------ | --------- | ------- | ------- | ------- | ----- | -------- | --- | --- |
|     |      |       |      |        | WIFI      |         |         | 5       |       |          |     |     |
|     |      |       |      |        | BLE       |         |         | 20      |       |          |     |     |
|     |      |       | Bảng | 3.4 Độ | trễ vật   | lý      | cố định | của các | chuẩn | mạng     |     |     |
| 4   | Mô   | hình  | năng | lượng  |           | và chất | lượng   | dịch    |       | vụ (QoS) |     |     |
| 4.1 | Băng | thông | thực |        | tế và đặc | thù     | tác vụ  |         |       |          |     |     |
Băngthôngthựctế(R)đượctínhtoándựatrêncôngthứcShannon,cóxétđến
| giới | hạn phần | cứng | và  | hiệu | suất     | phổ: |          |          |     |          |     |     |
| ---- | -------- | ---- | --- | ---- | -------- | ---- | -------- | -------- | --- | -------- | --- | --- |
|      |          |      |     |      | (cid:16) |      | (cid:16) | (cid:17) |     | (cid:17) |     |     |
SNR
|     |     |     |     | R=min | B·log |     | 1+10 |     | ·η,R |     |     | PT4.7 |
| --- | --- | --- | --- | ----- | ----- | --- | ---- | --- | ---- | --- | --- | ----- |
|     |     |     |     |       |       | 2   |      | 10  |      | max |     |       |
Trong đó:
|     | •   | η: Hiệu | suất | phổ | - hằng     | số. |     |     |     |     |     |     |
| --- | --- | ------- | ---- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
|     | •   | R :     | Giới | hạn | phần cứng. |     |     |     |     |     |     |     |
max
| 4.2 | Mô  | hình | tiêu | thụ | năng | lượng |     |     |     |     |     |     |
| --- | --- | ---- | ---- | --- | ---- | ----- | --- | --- | --- | --- | --- | --- |
Tổng năng lượng tiêu thụ (E ) cho mỗi tác vụ truyền tải được xác định bởi
total
công suất hoạt động, thời gian truyền và năng lượng đánh thức thiết bị:
Size
task
|     |     |     |     | E     | =(P | +P  | )·   |     | +E     |     |     | PT4.8 |
| --- | --- | --- | --- | ----- | --- | --- | ---- | --- | ------ | --- | --- | ----- |
|     |     |     |     | total | tx  |     | idle |     | wakeup |     |     |       |
R
Trong đó:
|     | •   | Size | : Dung | lượng | dữ  | liệu | cần truyền. |     |     |     |     |     |
| --- | --- | ---- | ------ | ----- | --- | ---- | ----------- | --- | --- | --- | --- | --- |
task
|     |     | Các  | giá trị | sử dụng  | trong  |       | mô phỏng: |     |        |        |          |     |
| --- | --- | ---- | ------- | -------- | ------ | ----- | --------- | --- | ------ | ------ | -------- | --- |
|     |     |      | –       | Monitor: | 1 kb   |       |           |     |        |        |          |     |
|     |     |      | –       | Alert:   | 50 kb  |       |           |     |        |        |          |     |
|     |     |      | –       | Video:   | 15 MB  |       |           |     |        |        |          |     |
|     | •   | P ,P | (mW)    | và       | E      | (mJ): | Là thông  |     | số đặc | tả của | chipset. |     |
|     |     | tx   | idle    |          | wakeup |       |           |     |        |        |          |     |
Dưới đây là các thông số đặc tả chipset được sử dụng trong mô phỏng:
6

| Mạng |      | P (mW)    | P (mW)      | E       | (mJ)    | η    | R    | (Mb/s) |
| ---- | ---- | --------- | ----------- | ------- | ------- | ---- | ---- | ------ |
|      |      | tx        | idle        | wakeup  |         |      | max  |        |
| 5G   |      | 300       | 15          |         | 5.0     | 0.8  |      | 200    |
| WIFI |      | 100       | 10          |         | 2.0     | 0.7  |      | 100    |
| BLE  |      | 10        | 2           |         | 0.5     | 0.5  |      | 2      |
|      | Bảng | 4.5 Thông | số kỹ thuật | chipset | và hiệu | suất | mạng |        |
7

CHƯƠNG 2. PHƯƠNG PHÁP NGHIÊN CỨU ĐỀ XUẤT
1 Cơ chế ra quyết định đa mục tiêu (MCDM)
Để giải quyết bài toán lựa chọn mạng tối ưu trong môi trường Multi-homed
IoT, nghiên cứu đề xuất áp dụng Phương pháp Quyết định Đa tiêu chí (Multi Cri-
teria Decision Method - MCDM). Phương pháp này cho phép hệ thống tìm kiếm
điểm cân bằng (trade-off) giữa hai yếu tố mâu thuẫn trực tiếp: tối ưu hóa mức tiêu
thụ năng lượng (Energy) và đảm bảo hiệu năng dịch vụ (QoS).
1.1 Hàm chi phí tổng quát
Hệ thống đưa ra quyết định dựa trên việc cực tiểu hóa hàm chi phí tổng quát
(Cost Function). Hàm này được thiết lập để phản ánh trọng số ưu tiên giữa năng
lượng và các hình phạt khi vi phạm cam kết chất lượng dịch vụ:
Cost =w ·E+w ·Penalty PT1.9
e q
Trong đó:
• E: Tổng năng lượng tiêu thụ dự tính cho tác vụ (đã được định nghĩa ở
chương 1).
• Penalty: Điểm phạt QoS, đại diện cho mức độ không đáp ứng được yêu
cầu của tác vụ.
• w ,w : Các trọng số điều chỉnh mức độ ưu tiên giữa năng lượng và chất
e q
lượng dịch vụ.
1.2 Cơ chế tính toán thành phần Penalty
Thành phần Penalty đóng vai trò then chốt trong việc duy trì ngưỡng QoS
khắt khe cho từng loại tác vụ. Điểm phạt này được cấu thành từ mức độ thiếu hụt
băng thông và mức độ vượt ngưỡng độ trễ:
Penalty=(∆ ·α)+(∆ ·β) PT1.10
BW Lat
Các tham số thành phần được định nghĩa cụ thể như sau:
• ∆ = max(0,BW −R): Độ thiếu hụt băng thông so với yêu cầu cụ
BW req
8

thể của tác vụ (đơn vị: Mbps). Nếu băng thông thực tế (R) đáp ứng đủ
|     |     | yêu cầu (BW |     | ), giá trị | này | bằng | 0.  |     |     |     |     |
| --- | --- | ----------- | --- | ---------- | --- | ---- | --- | --- | --- | --- | --- |
req
|     | •   | ∆ = max(0,Lat |     |      | −Lat | ):  | Độ trễ | vượt | ngưỡng cho | phép (đơn | vị: |
| --- | --- | ------------- | --- | ---- | ---- | --- | ------ | ---- | ---------- | --------- | --- |
|     |     | Lat           |     | curr |      | req |        |      |            |           |     |
ms).
=50.0(BandwidthFactor):
|     | •   | α             |     |     |     | Trọngsốphạtchomỗi1Mbpsbăngthông |     |     |     |     |     |
| --- | --- | ------------- | --- | --- | --- | ------------------------------- | --- | --- | --- | --- | --- |
|     |     | bị thiếu hụt. |     |     |     |                                 |     |     |     |     |     |
• β = 2.0 (Latency Factor): Trọng số phạt cho mỗi 1 ms độ trễ vượt mức
quy định.
|     |     | Tác vụ     |        | w   | w   | BW  | (Mb/s) |     | Lat (ms) |     |     |
| --- | --- | ---------- | ------ | --- | --- | --- | ------ | --- | -------- | --- | --- |
|     |     |            |        |     | e   | q   | min    |     | max      |     |     |
|     |     | Video      | Stream | 0.4 | 0.6 |     | 36.0   |     | 200      |     |     |
|     |     | Data       | Alert  | 0.3 | 0.7 |     | 5.0    |     | 100      |     |     |
|     |     | Monitoring |        | 0.8 | 0.2 |     | 0.1    |     | 1000     |     |     |
Bảng 1.1 Thông số trọng số và yêu cầu QoS cho từng loại tác vụ
| 2   | Kiến | trúc Trí | tuệ  | nhân  | tạo  | đề     | xuất |        |     |     |     |
| --- | ---- | -------- | ---- | ----- | ---- | ------ | ---- | ------ | --- | --- | --- |
| 2.1 | Biện | luận lựa | chọn | thuật | toán | Random |      | Forest |     |     |     |
Mặc dù thuật toán MCDM (Multi-Criteria Decision Method) mang lại độ
chính xác cao trong việc tối ưu hóa đa mục tiêu, tuy nhiên việc triển khai trực tiếp
trên các thiết bị IoT gặp nhiều hạn chế. Thuật toán này đòi hỏi các phép tính toán
vật lý và so sánh liên tục, gây tốn tài nguyên xử lý (CPU/RAM) và tăng mức tiêu
| thụ năng | lượng | của | chipset | IoT. |     |     |     |     |     |     |     |
| -------- | ----- | --- | ------- | ---- | --- | --- | --- | --- | --- | --- | --- |
Để giải quyết vấn đề này, nghiên cứu đề xuất chuyển đổi mô hình ra quyết
| định | sang | kiến trúc | AI dựa | trên | cách | tiếp cận | Student-Teacher: |     |     |     |     |
| ---- | ---- | --------- | ------ | ---- | ---- | -------- | ---------------- | --- | --- | --- | --- |
• Mô hình Teacher: Sử dụng thuật toán MCDM để thực hiện tính toán
|     |     | offlinetrên36.000kịchbảnmôphỏng, |       |     |     |     |     | từđódánnhãndữliệutốiưucho |     |     |     |
| --- | --- | -------------------------------- | ----- | --- | --- | --- | --- | ------------------------- | --- | --- | --- |
|     |     | từng ngữ                         | cảnh. |     |     |     |     |                           |     |     |     |
• Mô hình Student: Sử dụng thuật toán Random Forest Classifier để học
lại các quyết định từ tập dữ liệu đã dán nhãn. Mô hình này cho phép ra
quyết định nhanh chóng với độ phức tạp tính toán thấp, phù hợp với tài
|     |     | nguyên hạn | chế | của thiết | bị  | IoT. |     |     |     |     |     |
| --- | --- | ---------- | --- | --------- | --- | ---- | --- | --- | --- | --- | --- |
9

Việc lựa chọn thuật toán Random Forest (RF) làm mô hình thực thi cốt lõi
thayvìcáckiếntrúcmạngNeuralsâu(DeepLearning)đượcdựatrêncácphântích
| về tính | phù hợp với | hạ tầng | IoT | tài nguyên |     | thấp: |     |
| ------- | ----------- | ------- | --- | ---------- | --- | ----- | --- |
• Tối ưu hóa tài nguyên phần cứng: Các mạng Neural sâu thường đòi
|     | hỏicấuhìnhphần |     | cứngmạnhmẽđểxửlýcác |     |     |     | lớptíchchậphoặcmatrận |
| --- | -------------- | --- | ------------------- | --- | --- | --- | --------------------- |
trọng số lớn. Ngược lại, RF dựa trên các cấu trúc cây quyết định với các
phép toán so sánh nhị phân, giúp tiết kiệm đáng kể dung lượng bộ nhớ
|     | RAM và | giảm | thiểu | chu kỳ | xử lý | của CPU | trên thiết bị IoT. |
| --- | ------ | ---- | ----- | ------ | ----- | ------- | ------------------ |
• Khả năng đáp ứng thời gian thực: Nhờ quy trình suy luận đơn giản,
RF đảm bảo tốc độ ra quyết định chuyển mạch gần như tức thời. Điều
này đặc biệt quan trọng trong môi trường Multi-homed HetNet, nơi các
quyết định chọn mạng cần được đưa ra nhanh hơn tốc độ biến động của
|     | kênh truyền | để  | tránh | làm | gián đoạn | dịch vụ. |     |
| --- | ----------- | --- | ----- | --- | --------- | -------- | --- |
• Hiệu quả huấn luyện và tính ổn định: Với tập dữ liệu gồm 36,000
kịch bản mô phỏng, RF cho thấy khả năng hội tụ nhanh và tính ổn định
cao. Kết quả kiểm chứng chéo 5-fold (5-fold Cross-validation) với sai số
thấp (±0.0008) khẳng định mô hình có khả năng tổng quát hóa tốt mà
khônggặphiệntượngquákhớp(Overfitting),mộttháchthứcthườnggặp
|     | ở Deep Learning |     | khi | dữ liệu | không | đủ quy | mô. |
| --- | --------------- | --- | --- | ------- | ----- | ------ | --- |
• Tính minh bạch về đặc trưng: RF cho phép phân tích mức độ quan
trọng của các đặc trưng (Feature Importance). Qua đó, hệ thống chứng
minh được loại tác vụ (Task Type) chiếm trọng số cao nhất (31%) trong
quyết định, phù hợp với mục tiêu ưu tiên chất lượng dịch vụ (QoS) cho
|         | các tác vụ | nhạy | cảm. |         |     |     |     |
| ------- | ---------- | ---- | ---- | ------- | --- | --- | --- |
| 2.2 Quy | trình thu  | thập |      | dữ liệu |     |     |     |
Dữ liệu huấn luyện được xây dựng thông qua phương pháp lấy mẫu dựa trên
lưới (Grid-based sampling) để quét toàn bộ các vị trí khả thi trên bản đồ mô phỏng
| kích thước | 1000×1000 |     | pixels. | Quy | trình cụ | thể như | sau: |
| ---------- | --------- | --- | ------- | --- | -------- | ------- | ---- |
• Phân bổ tác vụ: Tập dữ liệu được chia đều (khoảng 33% cho mỗi loại)
giữa ba nhóm tác vụ chính: Video Streaming, Alert và Monitoring để
|     | đảm bảo | tính | tổng | quát. |     |     |     |
| --- | ------- | ---- | ---- | ----- | --- | --- | --- |
• Dán nhãn dữ liệu: Tổng cộng 36.000 mẫu dữ liệu sau khi thu thập được
gán nhãn bởi thuật toán MCDM, xác định mạng tối ưu nhất (5G, WiFi,
|     | hoặc BLE) | cho | từng | mẫu. |     |     |     |
| --- | --------- | --- | ---- | ---- | --- | --- | --- |
10

|        |           |       | Hình 2.1 | Hàm thực hiện |     |
| ------ | --------- | ----- | -------- | ------------- | --- |
| 2.3 Kỹ | thuật đặc | trưng | (Feature | Engineering)  |     |
Hệ thống sử dụng một vector đặc trưng 18 chiều (18-D) làm đầu vào cho mô
| hình Random | Forest. | Vector | này bao | gồm các thành | phần: |
| ----------- | ------- | ------ | ------- | ------------- | ----- |
• Ngữ cảnh thiết bị (Device Context - 3 chiều): Bao gồm tọa độ vị trí
|     | (x,y) và | loại tác | vụ hiện tại | (Task). |     |
| --- | -------- | -------- | ----------- | ------- | --- |
• Thông số mạng (Network Stats - 15 chiều): Đối với mỗi loại mạng
(5G, WiFi, BLE), hệ thống trích xuất 5 thông số chính: RSSI, SNR,
|     | Bandwidth, | Latency | và Distance. |     |     |
| --- | ---------- | ------- | ------------ | --- | --- |
• Xử lý mạng không khả dụng: Để mô hình nhận biết các mạng nằm
ngoài vùng phủ sóng, nghiên cứu thực hiện kỹ thuật dán nhãn giá trị
|     | biên: RSSI | =−999 | dBm | và Distance=9999 | m.  |
| --- | ---------- | ----- | --- | ---------------- | --- |
11

|     | Hình       | 2.2 Logic | hàm | trích xuất | đặc | trưng (extract_features) |
| --- | ---------- | --------- | --- | ---------- | --- | ------------------------ |
| 2.4 | Huấn luyện | và Kiểm   |     | chứng      |     |                          |
Quá trình huấn luyện mô hình Random Forest được thực hiện với các thiết
| lập nhằm | đảm bảo | khả năng | hội | tụ và tính | ổn  | định: |
| -------- | ------- | -------- | --- | ---------- | --- | ----- |
• Phân tách dữ liệu: Tập dữ liệu 36.000 mẫu được chia theo tỷ lệ 80%
|     | cho huấn                           | luyện | (Train) | và 20% | cho | kiểm tra (Test).          |
| --- | ---------------------------------- | ----- | ------- | ------ | --- | ------------------------- |
|     | • Kiểmchứngchéo(Cross-validation): |       |         |        |     | ÁpdụngphươngphápK-foldvới |
K = 5. Dữ liệu được chia thành 5 phần, luân phiên huấn luyện và kiểm
|     | chứng | để loại | bỏ hiện | tượng quá | khớp | (Overfitting). |
| --- | ----- | ------- | ------- | --------- | ---- | -------------- |
• Tham số mô hình: Cấu hình bộ phân loại bao gồm 100 cây quyết định
(Decision Trees) với độ sâu tối đa của mỗi cây được giới hạn ở mức 15
|     | để tối | ưu hóa | giữa độ | chính xác | và  | tốc độ thực thi. |
| --- | ------ | ------ | ------- | --------- | --- | ---------------- |
12

Hình2.3CấutrúcmãnguồnhuấnluyệnmôhìnhRandomForestvàthựchiệnCross
Validation.
| Hình 2.4 Kết | quả thực | thi kiểm chứng | chéo 5-fold |
| ------------ | -------- | -------------- | ----------- |
13

| CHƯƠNG |      |     | 3. KẾT | QUẢ  | THỰC  | NGHIỆM | VÀ  | PHÂN | TÍCH |
| ------ | ---- | --- | ------ | ---- | ----- | ------ | --- | ---- | ---- |
| 1      | Hiệu | quả | tối ưu | năng | lượng |        |     |      |      |
Sau khi huấn luyện và triển khai mô hình AI (Random Forest) dựa trên tri
thức từ bộ máy ra quyết định MCDM, chúng tôi tiến hành đánh giá hiệu năng hệ
thống thông qua các chỉ số tiêu thụ năng lượng thực tế trên từng tác vụ.
| 1.1 | Phân | tích | mức | tiêu thụ | năng | lượng trung | bình |     |     |
| --- | ---- | ---- | --- | -------- | ---- | ----------- | ---- | --- | --- |
Dựa trên kết quả thực nghiệm, thuật toán AI đề xuất đạt mức tiêu thụ năng
lượngtrungbìnhấntượnglà20.32mJchomỗitácvụ. Đểlàmrõưuthếcủaphương
pháp nghiên cứu, chúng tôi thực hiện so sánh đối chiếu với các thuật toán truyền
| thống | và  | các cơ | chế cơ | bản sau: |     |     |     |     |     |
| ----- | --- | ------ | ------ | -------- | --- | --- | --- | --- | --- |
• Max-RSSI: Lựa chọn mạng dựa trên cường độ tín hiệu mạnh nhất.
|     | •   | Random: | Lựa | chọn | mạng | ngẫu nhiên. |     |     |     |
| --- | --- | ------- | --- | ---- | ---- | ----------- | --- | --- | --- |
• Min Energy / Min Latency: Các phương pháp cực đoan chỉ tối ưu duy
|     |     | nhất một | chỉ số. |     |     |     |     |     |     |
| --- | --- | -------- | ------- | --- | --- | --- | --- | --- | --- |
• Rule-Based: Cơ chế chọn mạng theo quy tắc cố định dựa trên loại tác
|     |     | vụ(vídụ: | Videomặcđịnhdùng5G,AlertdùngWi-Fi, |     |     |     |     | Monitoringdùng |     |
| --- | --- | -------- | ---------------------------------- | --- | --- | --- | --- | -------------- | --- |
BLE).
Kết quả so sánh cho thấy mô hình AI không chỉ vượt trội về mặt năng lượng
trung bình mà còn duy trì được sự ổn định ở các ngưỡng tới hạn (95th Percentile
Energy).
| 1.2 | Cơ  | chế tối | ưu thông | minh |     |     |     |     |     |
| --- | --- | ------- | -------- | ---- | --- | --- | --- | --- | --- |
Sự khác biệt cốt lõi giúp thuật toán AI đạt hiệu quả cao nằm ở khả năng nhận
diện các vùng "Hotspot" – nơi có sự chồng lấn của nhiều loại sóng phủ. Thay vì
duy trì kết nối 5G công suất cao một cách liên tục như thuật toán Max-RSSI, AI
đề xuất chủ động chuyển hướng sang các giao diện Wi-Fi hoặc BLE ngay khi ngữ
cảnh tác vụ cho phép mà vẫn đảm bảo không vi phạm các ngưỡng QoS.
| 1.3 | Trình | bày | kết quả | đồ  | thị |     |     |     |     |
| --- | ----- | --- | ------- | --- | --- | --- | --- | --- | --- |
Dưới đây là các biểu đồ so sánh mức tiêu thụ năng lượng giữa phương pháp
| đề xuất | (Proposed) |     | và các | phương | pháp | đối chứng: |     |     |     |
| ------- | ---------- | --- | ------ | ------ | ---- | ---------- | --- | --- | --- |
14

| 2 Đảm | bảo QoS |     |
| ----- | ------- | --- |
Khả năng đáp ứng: Điểm phạt QoS (Penalty) của AI duy trì ở mức thấp
| ( 0.03), tương | đương | với Max-RSSI |
| -------------- | ----- | ------------ |
Phân tích Feature Importance: Loại tác vụ (Task_Type) chiếm trọng số quan
15

trọng nhất (31%) trong quyết định của AI, cho thấy mô hình đã học được cách ưu
| tiên QoS cho | các tác   | vụ nhạy cảm |
| ------------ | --------- | ----------- |
| Tiết         | kiệm năng | lượng       |
16

|     | CHƯƠNG |      | 4. KẾT | LUẬN |     | VÀ HƯỚNG |     | PHÁT TRIỂN |
| --- | ------ | ---- | ------ | ---- | --- | -------- | --- | ---------- |
| 1   | Kết    | luận |        |      |     |          |     |            |
Bên cạnh mục tiêu tiết kiệm năng lượng, khả năng duy trì chất lượng dịch vụ
(QoS) là tiêu chí quan trọng để đánh giá tính thực tiễn của mô hình. Các kết quả
thực nghiệm dưới đây so sánh thuật toán đề xuất (Proposed) với các phương pháp
| phổ | biến | khác. |     |     |     |     |     |     |
| --- | ---- | ----- | --- | --- | --- | --- | --- | --- |
Dựa trên dữ liệu thực nghiệm, thuật toán AI đề xuất đạt mức tiêu thụ năng
lượng trung bình chỉ 20.32 mJ/task. Khi so sánh với thuật toán Max-RSSI truyền
thống (22.70 mJ) và cơ chế Rule-Based (23.98 mJ), giải pháp đề xuất cho thấy sự
cải thiện đáng kể về mặt hiệu suất. Đặc biệt, tại phân vị thứ 95 (95th Percentile),
mô hình đề xuất duy trì mức 162.70 mJ, thấp hơn nhiều so với mức 194.00 mJ của
| các | phương | pháp | không | tối ưu. |     |     |     |     |
| --- | ------ | ---- | ----- | ------- | --- | --- | --- | --- |
Cơchếđạtđượchiệuquảnàylànhờkhảnăngnhậndiệnthôngminhcácvùng
"Hotspot" (vùng đa phủ sóng). Thay vì duy trì kết nối 5G công suất cao liên tục,
mô hình chủ động chuyển hướng sang các giao diện Wi-Fi hoặc BLE ngay khi ngữ
cảnh tác vụ cho phép (ví dụ: tác vụ Monitoring hoặc Alert) để giảm thiểu tiêu thụ
| năng | lượng | mà vẫn | đảm | bảo độ | trễ trong | ngưỡng | quy | định. |
| ---- | ----- | ------ | --- | ------ | --------- | ------ | --- | ----- |
Nghiên cứu đã xây dựng thành công một hệ thống ra quyết định thông minh
cho thiết bị IoT đa kết nối. Bằng cách kết hợp giữa lý thuyết MCDM và mô hình
học máy Random Forest, hệ thống đã chứng minh được khả năng tối ưu hóa đồng
| thời | giữa | thời lượng | pin và | chất | lượng | trải nghiệm | dịch | vụ. |
| ---- | ---- | ---------- | ------ | ---- | ----- | ----------- | ---- | --- |
| 2    | Hạn  | chế hiện   | tại    |      |       |             |      |     |
Mặc dù đạt được kết quả khả quan, hệ thống hiện tại vẫn tồn tại hạn chế về
tính"tốiưuhóaíchkỷ"(SelfishOptimization). Domỗithiếtbịchỉthựchiệntốiưu
dựa trên trạng thái cá nhân, hiện tượng tắc nghẽn cục bộ có thể xảy ra khi số lượng
thiết bị trong một khu vực tăng lên đáng kể, gây mất cân bằng tải hệ thống.
| 3   | Hướng | phát | triển | tương | lai | (Scalability) |     |     |
| --- | ----- | ---- | ----- | ----- | --- | ------------- | --- | --- |
Để giải quyết các thách thức về khả năng mở rộng, nghiên cứu định hướng
| hai | lộ trình | phát | triển chính: |     |     |     |     |     |
| --- | -------- | ---- | ------------ | --- | --- | --- | --- | --- |
17

| • Tiếp | cận hướng | mạng | (Network-Centric): |     |     |     |     |     |     |
| ------ | --------- | ---- | ------------------ | --- | --- | --- | --- | --- | --- |
– Cơ chế: Dịch chuyển "bộ não" quyết định từ thiết bị lên các
|     | SDN | Controller | đặt | tại trạm | MEC | (Edge | Cloud). |     |     |
| --- | --- | ---------- | --- | -------- | --- | ----- | ------- | --- | --- |
– Lợi ích: Thay thế tối ưu hóa ích kỷ bằng điều phối tập trung
|        | để thực   | hiện                                       | cân bằng | tải       | (Load | Balancing) |            | động giữa  | 5G và     |
| ------ | --------- | ------------------------------------------ | -------- | --------- | ----- | ---------- | ---------- | ---------- | --------- |
|        | Wi-Fi,    | đảm bảo                                    | ổn       | định QoS  | cho   | hàng       | ngàn       | thiết bị   | cùng lúc. |
| • Tiếp | cận hướng | AI (AI-Centric):                           |          |           |       |            |            |            |           |
|        | – Cơ chế: | Áp                                         | dụng Học | máy       | liên  | minh       | (Federated | Learning), |           |
|        | trong     | đó các                                     | thiết bị | huấn      | luyện | mô hình    | cục        | bộ và      | chỉ gửi   |
|        | thông     | số (Weights)                               |          | về server | trung | tâm        | để         | tổng hợp   | thành     |
|        | Global    | Model.                                     |          |           |       |            |            |            |           |
|        | – Lợiích: | Chophépcácthiếtbịhọchỏikinhnghiệmtừvùngphủ |          |           |       |            |            |            |           |
sóngcủanhaumàkhôngcầnthuthậpdữliệuthô,giúpbảomật
|     | quyền | riêng tư | tuyệt | đối và | tiết kiệm | băng | thông | truyền | tải lên |
| --- | ----- | -------- | ----- | ------ | --------- | ---- | ----- | ------ | ------- |
Cloud.
18

|     |     | TÀI LIỆU | THAM | KHẢO |
| --- | --- | -------- | ---- | ---- |
[1] T. S. Rappaport, “Wireless Communications: Principles and Practice”, 2nd
ed., 2002.
[2] C. E. Shannon, “A Mathematical Theory of Communication”, Bell System
| Tech. J., | 1948. |     |     |     |
| --------- | ----- | --- | --- | --- |
[3] K. Piamrat, et al., “QoE-aware Vertical Handover in Wireless Heterogeneous
| Networks”, | IEEE | Trans. Mob. | Comput., | 2011. |
| ---------- | ---- | ----------- | -------- | ----- |
[4] L. Breiman, “Random Forests”, Machine Learning, vol. 45, no. 1, 2001.
[5] 3GPP, “Study on channel model for frequencies from 0.5 to 100 GHz”, TR
| 38.901, | 2024. |     |     |     |
| ------- | ----- | --- | --- | --- |
[6] B. McMahan, et al., “Communication-Efficient Learning of Deep Networks
| from Decentralized |     | Data”, AISTATS, |     | 2017. |
| ------------------ | --- | --------------- | --- | ----- |
19