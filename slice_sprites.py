import pygame
import os

# --- CẤU HÌNH ---
INPUT_IMAGE = "assets/img/nu.png"  # Ảnh gốc nữ
OUTPUT_FOLDER = "assets/img/player/girl"  # Thư mục chứa ảnh sau khi cắt
NUM_FRAMES = 6  # Số bước đi (thường là 6)


# ---------------

def slice_sprite_sheet():
    pygame.init()

    if not os.path.exists(INPUT_IMAGE):
        print(f"LỖI: Không tìm thấy file '{INPUT_IMAGE}'")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    try:
        sheet = pygame.image.load(INPUT_IMAGE)
        sheet_w, sheet_h = sheet.get_size()
        frame_width = sheet_w // NUM_FRAMES
        frame_height = sheet_h

        print(f"Đang cắt ảnh nữ: {sheet_w}x{sheet_h} -> {NUM_FRAMES} hình.")

        for i in range(NUM_FRAMES):
            rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            frame_surf = sheet.subsurface(rect)

            # Lưu tên file giống hệt bên Boy (walk_0, walk_1...)
            out_name = f"{OUTPUT_FOLDER}/walk_{i}.png"
            pygame.image.save(frame_surf, out_name)
            print(f"-> Đã lưu: {out_name}")

        print("\n--- XONG! ĐÃ CÓ ẢNH NỮ ---")

    except Exception as e:
        print(f"Lỗi: {e}")


if __name__ == "__main__":
    slice_sprite_sheet()