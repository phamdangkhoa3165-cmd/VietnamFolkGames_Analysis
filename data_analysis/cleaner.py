import pandas as pd

def process_data(input_path, output_path):
    print("Đang xử lý dữ liệu...")
    try:
        df = pd.read_csv(input_path)
        df = df.fillna(0)
        # One-hot encoding cho vật phẩm
        df['has_item'] = df['items_list'].apply(lambda x: 0 if x == 'None' or pd.isna(x) else 1)
        df.to_csv(output_path, index=False)
        return df
    except Exception as e:
        print(f"Lỗi: {e}")
        return None