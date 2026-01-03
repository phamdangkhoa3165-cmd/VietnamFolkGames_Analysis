import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Cấu hình giao diện biểu đồ
plt.style.use('ggplot')
sns.set_palette("husl")


# Xác định đường dẫn file dữ liệu (hoạt động cả khi chạy exe)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Dùng đường dẫn tương đối để trỏ ra thư mục chứa file Exe
DATA_FILE = 'data/raw_logs.csv'


def analyze_data():
    print(f"--- ĐANG ĐỌC DỮ LIỆU TỪ: {DATA_FILE} ---")

    # 1. Kiểm tra file dữ liệu
    if not os.path.exists(DATA_FILE):
        print("❌ Chưa có dữ liệu! Hãy chơi game vài ván để sinh file logs.")
        return

    # 2. Đọc dữ liệu bằng Pandas
    try:
        df = pd.read_csv(DATA_FILE)
        if df.empty:
            print("⚠️ File dữ liệu trống.")
            return
        print("✅ Đã đọc dữ liệu thành công!")
        print(f"Tổng số ván đã chơi: {len(df)}")
    except Exception as e:
        print(f"❌ Lỗi đọc file CSV: {e}")
        return

    # 3. Làm sạch và Chuẩn hóa dữ liệu
    # Chuyển timestamp sang dạng thời gian chuẩn
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except:
        pass

    # Tạo cột 'win_flag': 1 nếu Win, 0 nếu Lose
    df['win_flag'] = df['result'].apply(lambda x: 1 if x == 'Win' else 0)

    # --- VẼ BIỂU ĐỒ ---
    try:
        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('BÁO CÁO PHÂN TÍCH NGƯỜI CHƠI', fontsize=16, color='darkred')

        # BIỂU ĐỒ 1: TỶ LỆ THẮNG (Cột)
        if 'game_type' in df.columns:
            win_rates = df.groupby('game_type')['win_flag'].mean() * 100
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            axs[0, 0].bar(win_rates.index, win_rates.values, color=colors[:len(win_rates)])
            axs[0, 0].set_title('Tỷ lệ thắng (%) theo Game')
            axs[0, 0].set_ylabel('% Thắng')
            axs[0, 0].set_ylim(0, 100)

        # BIỂU ĐỒ 2: ĐIỂM SỐ THEO THỜI GIAN (Đường)
        if 'score' in df.columns:
            df_sorted = df.sort_values('timestamp')
            axs[0, 1].plot(df_sorted['timestamp'], df_sorted['score'], marker='o', linestyle='-', color='blue')
            axs[0, 1].set_title('Biến động điểm số')
            axs[0, 1].tick_params(axis='x', rotation=45)

        # BIỂU ĐỒ 3: THẮNG THUA THEO LEVEL (Cột đếm)
        if 'level' in df.columns:
            sns.countplot(data=df, x='level', hue='result', ax=axs[1, 0], palette="Set2")
            axs[1, 0].set_title('Kết quả theo Level')

        # BIỂU ĐỒ 4: VẬT PHẨM (Tròn)
        def has_items(item_str):
            return "Không dùng" if pd.isna(item_str) or item_str == "None" or item_str == "" else "Có dùng"

        df['use_item_status'] = df['items_list'].apply(has_items)
        item_counts = df['use_item_status'].value_counts()

        axs[1, 1].pie(item_counts, labels=item_counts.index, autopct='%1.1f%%', startangle=90,
                      colors=['#ffcc99', '#99ff99'])
        axs[1, 1].set_title('Tỷ lệ dùng vật phẩm')

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"❌ Lỗi khi vẽ biểu đồ: {e}")


if __name__ == "__main__":
    analyze_data()