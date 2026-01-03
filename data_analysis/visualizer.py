import matplotlib.pyplot as plt
import pandas as pd

def draw_charts(df):
    if df is None or df.empty:
        print("Không có dữ liệu.")
        return

    plt.style.use('ggplot')
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('BÁO CÁO PHÂN TÍCH GAME SINH TỒN', fontsize=16, color='navy')

    # 1. Điểm theo Level
    axs[0, 0].scatter(df['level'], df['score'], color='blue', alpha=0.6)
    axs[0, 0].set_title('Tương quan: Level & Điểm')
    axs[0, 0].set_ylabel('Điểm')

    # 2. Game gây mất mạng nhiều nhất
    lose_df = df[df['result'] == 'Lose']
    if not lose_df.empty:
        deadly = lose_df['game_type'].value_counts()
        axs[0, 1].bar(deadly.index, deadly.values, color='red')
        axs[0, 1].set_title('Số lần Mất Mạng theo Game')
    else:
        axs[0, 1].text(0.5, 0.5, "Chưa ai thua cả!", ha='center')

    # 3. Hiệu quả vật phẩm
    df['Status'] = df['items_list'].apply(lambda x: 'Có Item' if x != 'None' else 'Không Item')
    df.boxplot(column='score', by='Status', ax=axs[1, 0])
    axs[1, 0].set_title('So sánh điểm số (Có/Không Item)')

    # 4. Xu hướng Level (20 lượt gần nhất)
    recent = df.tail(20)
    axs[1, 1].plot(range(len(recent)), recent['level'], marker='o', color='green')
    axs[1, 1].set_title('Level đạt được gần đây')

    plt.tight_layout()
    plt.show()