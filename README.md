# IoT Network Selection Simulator
Mô phỏng một thiết bị IoT chọn mạng (Wi-Fi, 5G, BLE) theo thời gian thực để giảm năng lượng nhưng vẫn giữ QoS.

## What’s inside
- Simulation engine tính QoS từ mô hình kênh vô tuyến và khoảng cách.
- MCDM baseline + Random Forest để chọn mạng tức thời.
- FastAPI REST API + web UI minh họa.

## Tech stack
- Backend: Python 3.11, FastAPI, Pydantic, Uvicorn.
- AI/ML: Scikit-learn (Random Forest), Pandas/NumPy, joblib.
- Frontend: HTML + Chart.js (UI demo nhẹ).

## Project layout (rút gọn)
- `app/` backend FastAPI, core logic, simulation, ML.
- `scripts/` tiện ích thu thập dữ liệu và train.
- `tests/` pytest.
- `docs/` tài liệu chi tiết.

## Muốn đào sâu?
- Kiến trúc & code: `docs/CODE_GUIDE.md`.
- Công thức & mô hình vật lý: `docs/congthuc.md`.
- Báo cáo & kết quả ML: `docs/RESEARCH_REPORT.md`.
- API usage: `docs/POSTMAN_GUIDE.md` + collection JSON.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

**Author:** Tuan Tu Tran 
**Email:** [trantuantu2004@gmail.com]  
**GitHub:** [@ngaiTu29s1](https://github.com/ngaiTu29s1)

---

## 🙏 Acknowledgments

Công trình này sử dụng các tài liệu tham khảo:
- **T. S. Rappaport** - *Wireless Communications: Principles and Practice* (Path Loss Model)
- **C. E. Shannon** - *A Mathematical Theory of Communication* (Shannon-Hartley)
- **K. Piamrat et al.** - *QoE-aware Vertical Handover* (Energy Model)

---

⭐ **Nếu dự án này hữu ích cho nghiên cứu của bạn, hãy star repo để ủng hộ!** ⭐