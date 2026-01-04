# 🇻🇳 VIETNAM FOLK GAMES - GAME DÂN GIAN VIỆT NAM

> **Bài tập lớn môn Lập trình Python** > Đề tài: Xây dựng bộ trò chơi dân gian tích hợp phân tích dữ liệu người chơi.

## 📖 Giới thiệu (Introduction)

Dự án **Vietnam Folk Games** được xây dựng nhằm mục đích bảo tồn và tái hiện các trò chơi dân gian quen thuộc của Việt Nam trên nền tảng máy tính. Điểm đặc biệt của dự án là việc tích hợp module **Data Analysis**, giúp thu thập và phân tích hành vi, thành tích của người chơi để đưa ra các biểu đồ thống kê trực quan.

## 🎮 Danh sách trò chơi (Features)

Hệ thống bao gồm 4 mini-game mang đậm bản sắc văn hóa:
1.  **Đập Niêu Đất:** Thử tài phản xạ và canh thời gian chính xác.
2.  **Nhảy Bao Bố:** Trò chơi vận động đòi hỏi sự khéo léo.
3.  **Hứng Trái Cây:** Hứng lộc đầu năm, rèn luyện sự nhanh mắt.
4.  **Ghép Tranh Làng Quê:** Trò chơi trí tuệ, ghép các mảnh vỡ thành bức tranh hoàn chỉnh.

**Tính năng nâng cao:**
* 🛒 **Cửa hàng (Shop):** Mua vật phẩm hỗ trợ bằng tiền ảo trong game.
* 👤 **Hồ sơ (Profile):** Tạo nhiều người chơi, tùy chọn Avatar (Nam/Nữ).
* 📊 **Thống kê (Dashboard):** Hệ thống tự động vẽ biểu đồ phân tích tỷ lệ thắng/thua và xu hướng sử dụng vật phẩm.

## 🛠 Công nghệ sử dụng (Tech Stack)

* **Ngôn ngữ:** Python 3.x
* **Game Engine:** Pygame (Xử lý đồ họa, âm thanh, va chạm).
* **Data Processing:** Pandas (Xử lý file log CSV, làm sạch dữ liệu).
* **Visualization:** Matplotlib & Seaborn (Vẽ biểu đồ phân tích).

## ⚙️ Cài đặt và Chạy game (Installation)

Nếu bạn muốn chạy source code trên máy tính cá nhân:

1. **Clone dự án về máy:**
   ```bash
   git clone [https://github.com/phamdangkhoa3165-cmd/VietnamFolkGames_Analysis.git](https://github.com/phamdangkhoa3165-cmd/VietnamFolkGames_Analysis.git)
   cd VietnamFolkGames_Analysis

2. Cài đặt các thư viện cần thiết:
Bash
pip install -r requirements.txt

3. Chạy game:
Bash
python main_game.py

📂 Cấu trúc thư mục (Folder Structure)
assets/: Chứa hình ảnh, âm thanh, font chữ.
data/: Chứa dữ liệu người chơi (raw_logs.csv, profiles.json).
game_engine/: Mã nguồn xử lý logic game và phân tích dữ liệu.
main_game.py: File khởi chạy chính.

👨‍💻 Tác giả (Author)

Nhóm 17
1. Trần Hải Đạt	24110197
2. Trần Nguyễn Minh Hiếu	24110212
3. Phạm Đăng Khoa	24110256
4. Nguyễn Trung Kiên	24110263
5. Nguyễn Quốc Việt	24110380

Trường: Đại học Sư phạm Kỹ thuật TP.HCM (UTE)

Khoa: Công nghệ Thông tin

Cảm ơn thầy cô và các bạn đã quan tâm đến dự án!

