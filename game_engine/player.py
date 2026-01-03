import pygame
import math
import os
import sys


# --- HÀM HỖ TRỢ ĐƯỜNG DẪN (CHO EXE) ---
def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối, hoạt động cho cả Code chạy thường và File Exe"""
    try:
        # PyInstaller tạo ra thư mục tạm này
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Player:
    def __init__(self):
        self.money = 200  # [NÂNG CẤP] Tăng tiền khởi điểm để dễ test mua đồ

        # [NÂNG CẤP] Inventory chuyển thành Dictionary để lưu số lượng
        # Ví dụ: {"BuaThan": 3, "GiayGio": 1}
        self.inventory = {}

        self.gender = "BOY"  # Mặc định là Nam

        # --- CẤU HÌNH VỊ TRÍ CHUẨN ---
        self.x = 400
        self.y = 420

        # --- CẤU HÌNH KÍCH THƯỚC ---
        self.height = 100
        self.width = 70

        self.sprites = []
        self.current_frame = 0
        self.animation_speed = 0.2

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # --- DI CHUYỂN ---
        self.speed = 5
        self.target_x = self.x
        self.target_y = self.y
        self.is_moving = False
        self.facing_right = True
        self.walk_tick = 0

        # --- GIỚI HẠN VÙNG ĐI ---
        self.MIN_Y = 400
        self.MAX_Y = 490

        # Tự động tải ảnh
        self.set_gender("BOY")

    def set_gender(self, gender):
        self.gender = gender
        self.sprites = []

        # Dùng đường dẫn tương đối để hàm resource_path xử lý
        if gender == "BOY":
            path = os.path.join("assets", "img", "player", "boy")
        else:
            path = os.path.join("assets", "img", "player", "girl")

        self.load_animations(path)

    def load_animations(self, relative_path):
        # Chuyển đổi sang đường dẫn thật
        full_path = resource_path(relative_path)

        if not os.path.exists(full_path):
            # print(f"⚠️ Cảnh báo: Không tìm thấy thư mục ảnh tại {full_path}")
            return

        try:
            # Lấy danh sách file png và sắp xếp
            files = sorted([f for f in os.listdir(full_path) if f.startswith('walk_') and f.endswith('.png')])
            if not files: return

            # Load ảnh đầu tiên để lấy kích thước gốc
            first_img = pygame.image.load(os.path.join(full_path, files[0]))
            orig_w, orig_h = first_img.get_size()

            # Tính tỷ lệ resize (Giữ chiều cao 100px)
            scale = self.height / orig_h
            new_w = int(orig_w * scale)
            self.width = new_w  # Cập nhật chiều rộng hitbox

            # Load tất cả ảnh
            for f in files:
                img = pygame.image.load(os.path.join(full_path, f))
                img = pygame.transform.scale(img, (self.width, self.height))
                self.sprites.append(img)

            print(f"-> Đã tải {len(self.sprites)} ảnh cho {self.gender}")

        except Exception as e:
            print(f"Lỗi tải ảnh nhân vật: {e}")

    # --- [NÂNG CẤP] HỆ THỐNG QUẢN LÝ KHO HÀNG ---

    def add_item(self, item_key):
        """Mua thêm vật phẩm: Cộng dồn số lượng"""
        if item_key in self.inventory:
            self.inventory[item_key] += 1
        else:
            self.inventory[item_key] = 1

    def has_item(self, item_key):
        """Kiểm tra xem có vật phẩm này trong kho không (số lượng > 0)"""
        return item_key in self.inventory and self.inventory[item_key] > 0

    def use_item(self, item_key):
        """
        Sử dụng 1 vật phẩm:
        - Trừ số lượng đi 1.
        - Nếu hết (về 0) thì xóa khỏi danh sách hoặc để 0 tùy logic.
        - Trả về True nếu dùng thành công, False nếu không có.
        """
        if self.has_item(item_key):
            self.inventory[item_key] -= 1
            # Nếu muốn xóa hẳn key khi về 0 để tiết kiệm bộ nhớ:
            if self.inventory[item_key] == 0:
                del self.inventory[item_key]
            return True
        return False

    # ----------------------------------------------------

    def set_target(self, mouse_pos, camera_x=0):
        screen_x, screen_y = mouse_pos
        self.target_x = screen_x + camera_x

        # Điều chỉnh Y để chân chạm đất (trừ chiều cao)
        self.target_y = screen_y - self.height + 15

        # Kẹp Y trong vùng cho phép
        if self.target_y < self.MIN_Y: self.target_y = self.MIN_Y
        if self.target_y > self.MAX_Y: self.target_y = self.MAX_Y

        # Căn giữa X
        self.target_x -= self.width // 2

        self.is_moving = True

        if self.target_x > self.x:
            self.facing_right = True
        elif self.target_x < self.x:
            self.facing_right = False

    def update_position(self, screen_height, screen_width=800):
        # Update animation
        if self.is_moving:
            self.walk_tick += 0.2
            if self.sprites:
                self.current_frame += self.animation_speed
                if self.current_frame >= len(self.sprites):
                    self.current_frame = 0
        else:
            self.current_frame = 0
            self.walk_tick = 0

        if not self.is_moving:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < self.speed:
            self.x = self.target_x
            self.y = self.target_y
            self.is_moving = False
        else:
            ratio = self.speed / distance
            self.x += dx * ratio
            self.y += dy * ratio

        # Ràng buộc tọa độ
        if self.y < self.MIN_Y: self.y = self.MIN_Y
        if self.y > self.MAX_Y: self.y = self.MAX_Y
        if self.x < -20: self.x = -20

        self.rect.topleft = (self.x, self.y)
        self.rect.size = (self.width, self.height)

    # --- HÀM VẼ (GIỮ NGUYÊN) ---
    def draw(self, screen):
        """Hàm vẽ chính: Tự vẽ bản thân lên màn hình"""

        # Cách 1: Vẽ bằng Ảnh (Sprite) nếu load thành công
        if self.sprites and len(self.sprites) > 0:
            try:
                img = self.sprites[int(self.current_frame) % len(self.sprites)]
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)

                # Bóng đổ
                pygame.draw.ellipse(screen, (0, 0, 0, 80), (self.x + 5, self.y + self.height - 10, self.width - 10, 15))
                # Nhân vật
                screen.blit(img, (self.x, self.y))

                # Tên (Dùng font hệ thống cho an toàn)
                font = pygame.font.SysFont("arial", 14, bold=True)
                text = font.render("Tôi", True, (255, 255, 255))
                text_x = self.x + (self.width - text.get_width()) // 2
                screen.blit(text, (text_x, self.y - 20))
                return
            except:
                pass  # Nếu lỗi vẽ ảnh -> Chuyển sang Cách 2

        # Cách 2: Vẽ bằng Hình khối (Fallback - Đảm bảo không tàng hình)
        # Bóng
        pygame.draw.ellipse(screen, (0, 0, 0, 50), (self.x + 10, self.y + 80, 50, 15))

        color = (50, 100, 200) if self.gender == "BOY" else (255, 105, 180)

        # Thân (Nhún nhảy khi đi)
        bounce = math.sin(self.walk_tick * 2) * 5 if self.is_moving else 0
        draw_y = self.y + bounce + 20

        pygame.draw.rect(screen, color, (self.x + 15, draw_y, 40, 50), border_radius=10)
        # Đầu
        pygame.draw.circle(screen, (255, 224, 189), (int(self.x + 35), int(draw_y - 5)), 20)

        # Tên
        font = pygame.font.SysFont("arial", 14, bold=True)
        text = font.render("Tôi", True, (255, 255, 255))
        screen.blit(text, (self.x + 20, draw_y - 40))