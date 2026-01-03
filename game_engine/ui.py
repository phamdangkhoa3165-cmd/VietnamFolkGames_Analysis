import pygame
import os
import sys
import math
import time

# --- [1] KHỞI TẠO ÂM THANH AN TOÀN ---
SOUND_SYSTEM_OK = False
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    SOUND_SYSTEM_OK = True
    print("✅ UI: Hệ thống âm thanh sẵn sàng.")
except Exception as e:
    print(f"⚠️ UI: Lỗi âm thanh ({e}). Chạy chế độ im lặng.")
    SOUND_SYSTEM_OK = False

# --- CẤU HÌNH ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Vietnam Folk Games"

# --- BẢNG MÀU ---
WOOD_DARK = (60, 40, 20)
WOOD_LIGHT = (101, 67, 33)
PAPER = (245, 230, 210)
GOLD = (255, 215, 0)
RED_LUCKY = (178, 34, 34)
GREEN_DARK = (34, 139, 34)
BLACK_OVERLAY = (0, 0, 0, 180)
BTN_GREEN = (118, 192, 68)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
GRAY = (200, 200, 200)
PINK = (255, 105, 180)
BROWN_BG = (210, 180, 140)
CYAN = (0, 255, 255)


# --- HÀM TÀI NGUYÊN ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


_font_cache = {}


def get_font(size):
    global _font_cache
    if size not in _font_cache:
        try:
            font_path = resource_path(os.path.join("assets", "font_game.ttf"))
            if os.path.exists(font_path):
                _font_cache[size] = pygame.font.Font(font_path, size)
            else:
                _font_cache[size] = pygame.font.SysFont("arial", size, bold=True)
        except:
            _font_cache[size] = pygame.font.SysFont("arial", size)
    return _font_cache[size]


_image_cache = {}


def get_image(name, width=None, height=None):
    global _image_cache
    cache_key = f"{name}_{width}_{height}"
    if cache_key not in _image_cache:
        try:
            path = resource_path(os.path.join("assets", "img", name))
            img = pygame.image.load(path)
            if width and height: img = pygame.transform.scale(img, (width, height))
            _image_cache[cache_key] = img
        except:
            _image_cache[cache_key] = None
    return _image_cache[cache_key]


# --- HÀM VẼ CHỮ CÓ VIỀN ---
def draw_text_outline(screen, text, font_size, x, y, color=WHITE, outline_color=BLACK, align="center"):
    font = get_font(font_size)
    offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2), (-1, 0), (1, 0), (0, -1), (0, 1)]
    for ox, oy in offsets:
        surf = font.render(text, True, outline_color)
        rect = surf.get_rect()
        if align == "center":
            rect.center = (x + ox, y + oy)
        elif align == "left":
            rect.topleft = (x + ox, y + oy)
        elif align == "right":
            rect.topright = (x + ox, y + oy)
        screen.blit(surf, rect)

    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if align == "center":
        rect.center = (x, y)
    elif align == "left":
        rect.topleft = (x, y)
    elif align == "right":
        rect.topright = (x, y)
    screen.blit(surf, rect)


# --- VẼ BACKGROUND ---
def draw_background(screen, camera_x=0):
    bg = get_image("bg_lang_que.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
    if bg:
        rel_x = camera_x % SCREEN_WIDTH
        screen.blit(bg, (-rel_x, 0))
        if rel_x < SCREEN_WIDTH:
            screen.blit(bg, (SCREEN_WIDTH - rel_x, 0))
    else:
        screen.fill(PAPER)


# --- CÁC HÀM UI CƠ BẢN ---
def draw_panel(screen, x, y, w, h, color=BLACK_OVERLAY):
    s = pygame.Surface((w, h))
    alpha = color[3] if len(color) > 3 else 200
    s.set_alpha(alpha)
    s.fill(color[:3])
    screen.blit(s, (x, y))
    pygame.draw.rect(screen, GOLD, (x, y, w, h), 2)


def draw_text_fit(screen, text, font_size, color, rect, align="center"):
    font = get_font(font_size)
    surf = font.render(text, True, color)
    r = surf.get_rect()
    if align == "center":
        r.center = rect.center
    elif align == "left":
        r.midleft = (rect.x + 5, rect.centery)
    elif align == "right":
        r.midright = (rect.x + rect.w - 5, rect.centery)
    screen.blit(surf, r)


def draw_button(screen, rect, text, is_hover=False, is_sel=False, bg_color=None, sub_text=""):
    base = bg_color if bg_color else WOOD_LIGHT
    col = (min(base[0] + 30, 255), min(base[1] + 30, 255), min(base[2] + 30, 255)) if is_hover else base
    if is_sel: col = (100, 100, 100)

    pygame.draw.rect(screen, (0, 0, 0), (rect.x + 3, rect.y + 3, rect.w, rect.h), border_radius=8)
    pygame.draw.rect(screen, col, rect, border_radius=8)
    pygame.draw.rect(screen, GOLD, rect, 2, border_radius=8)

    draw_text_outline(screen, text, 28, rect.centerx, rect.centery - (10 if sub_text else 0), WHITE, BLACK)
    if sub_text:
        draw_text_outline(screen, sub_text, 18, rect.centerx, rect.centery + 15, GOLD, BLACK)


def draw_timer_bar(screen, x, y, w, h, time_left, total_time):
    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h), border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), (x, y, w, h), 2, border_radius=10)
    if total_time > 0:
        ratio = max(0, time_left / total_time)
        fill_w = int((w - 4) * ratio)
        col = BTN_GREEN if ratio > 0.5 else (GOLD if ratio > 0.2 else RED)
        if fill_w > 0:
            pygame.draw.rect(screen, col, (x + 2, y + 2, fill_w, h - 4), border_radius=8)

    draw_text_outline(screen, f"THỜI GIAN: {int(time_left)}s", 22, x + w / 2, y + h + 15, WHITE, BLACK)


# --- VẼ MŨI TÊN & TƯƠNG TÁC ---
def draw_bouncing_arrow(screen, x, y, color=GOLD):
    bounce = math.sin(time.time() * 8) * 10
    current_y = y + bounce - 80
    pygame.draw.polygon(screen, color, [(x - 20, current_y - 20), (x + 20, current_y - 20), (x, current_y + 10)])
    pygame.draw.polygon(screen, WHITE, [(x - 20, current_y - 20), (x + 20, current_y - 20), (x, current_y + 10)], 2)


def draw_interaction_zone(screen, rect, text, is_near, camera_x=0):
    draw_x = rect.x - camera_x
    if -200 < draw_x < SCREEN_WIDTH + 200:
        s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        col = (255, 215, 0, 150) if is_near else (200, 200, 200, 80)
        pygame.draw.ellipse(s, col, (0, 0, rect.w, rect.h))
        pygame.draw.ellipse(s, WHITE, (0, 0, rect.w, rect.h), 2)
        screen.blit(s, (draw_x, rect.y))

        draw_bouncing_arrow(screen, draw_x + rect.w // 2, rect.y + rect.h // 2, RED_LUCKY if "VÉ SỐ" in text else GOLD)

        name_y = rect.y - 140
        bg_rect = pygame.Rect(draw_x + rect.w // 2 - 100, name_y - 10, 200, 40)
        draw_panel(screen, bg_rect.x, bg_rect.y, bg_rect.w, bg_rect.h)
        draw_text_outline(screen, text, 24, bg_rect.centerx, bg_rect.centery, GOLD, BLACK)

        if is_near:
            draw_text_outline(screen, "Bấm SPACE", 20, draw_x + rect.w // 2, rect.bottom + 20, WHITE, BLACK)


# --- VẼ NHÂN VẬT ---
def draw_character_on_map(screen, player, camera_x=0):
    screen_x = player.x - camera_x
    drawn_by_sprite = False

    if hasattr(player, 'sprites') and player.sprites and len(player.sprites) > 0:
        try:
            idx = int(player.current_frame) % len(player.sprites)
            img = player.sprites[idx]
            if not player.facing_right: img = pygame.transform.flip(img, True, False)
            pygame.draw.ellipse(screen, (0, 0, 0, 80),
                                (screen_x + 5, player.y + player.height - 12, player.width - 10, 15))
            screen.blit(img, (screen_x, player.y))
            drawn_by_sprite = True
        except:
            pass

    if not drawn_by_sprite:
        pygame.draw.rect(screen, BLUE if player.gender == "BOY" else PINK,
                         (screen_x, player.y, player.width, player.height))

    draw_text_outline(screen, "Tôi", 18, screen_x + player.width // 2, player.y - 15, WHITE, BLACK)


# --- CHỌN NHÂN VẬT ---
def draw_character_select(screen):
    draw_background(screen)
    draw_panel(screen, 100, 80, 600, 440, color=(0, 0, 0, 200))
    draw_text_outline(screen, "CHỌN NHÂN VẬT", 50, 400, 140, GOLD, BLACK)

    mouse_pos = pygame.mouse.get_pos()

    btn_boy = pygame.Rect(180, 200, 200, 200)
    is_boy_hover = btn_boy.collidepoint(mouse_pos)
    col_boy = BLUE if is_boy_hover else (30, 30, 100)
    pygame.draw.rect(screen, col_boy, btn_boy, border_radius=15)
    pygame.draw.rect(screen, GOLD, btn_boy, 3, border_radius=15)
    draw_text_outline(screen, "NAM", 40, btn_boy.centerx, btn_boy.centery, WHITE, BLACK)

    btn_girl = pygame.Rect(420, 200, 200, 200)
    is_girl_hover = btn_girl.collidepoint(mouse_pos)
    col_girl = PINK if is_girl_hover else (100, 30, 60)
    pygame.draw.rect(screen, col_girl, btn_girl, border_radius=15)
    pygame.draw.rect(screen, GOLD, btn_girl, 3, border_radius=15)
    draw_text_outline(screen, "NỮ", 40, btn_girl.centerx, btn_girl.centery, WHITE, BLACK)

    return {"BOY": btn_boy, "GIRL": btn_girl}


# --- CÁC HÀM KHÁC ---
def draw_pause_button_icon(screen):
    cx, cy = SCREEN_WIDTH - 40, 40
    pygame.draw.circle(screen, BTN_GREEN, (cx, cy), 25)
    pygame.draw.circle(screen, WHITE, (cx, cy), 25, 2)
    pygame.draw.rect(screen, WHITE, (cx - 8, cy - 10, 6, 20))
    pygame.draw.rect(screen, WHITE, (cx + 2, cy - 10, 6, 20))
    return pygame.Rect(cx - 25, cy - 25, 50, 50)


def draw_pause_menu(screen):
    draw_panel(screen, 200, 150, 400, 300)
    draw_text_outline(screen, "TẠM DỪNG", 50, 400, 200, GOLD, BLACK)
    mp = pygame.mouse.get_pos()
    btn_resume = pygame.Rect(250, 280, 300, 60)
    btn_exit = pygame.Rect(250, 360, 300, 60)
    draw_button(screen, btn_resume, "TIẾP TỤC", btn_resume.collidepoint(mp), False, BTN_GREEN)
    draw_button(screen, btn_exit, "THOÁT", btn_exit.collidepoint(mp), False, RED)
    return {"RESUME": btn_resume, "EXIT": btn_exit}


def draw_icon_button(screen, rect, icon_name):
    pygame.draw.rect(screen, WHITE, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
    symb = "$" if icon_name == "SHOP" else "B"
    draw_text_outline(screen, symb, 30, rect.centerx, rect.centery, BLACK, WHITE)
    draw_text_outline(screen, icon_name, 14, rect.centerx, rect.bottom + 10, WHITE, BLACK)


# --- [CẬP NHẬT] HUD VỚI NỀN MÀU BẢO VỆ ---
def draw_hud(screen, player, player_name="Người chơi"):
    # 1. Vẽ khung nền trắng mờ (Background HUD)
    pygame.draw.rect(screen, (255, 255, 255, 200), (10, 10, 220, 70), border_radius=35)

    # 2. Vẽ NỀN TRÒN MÀU (Vẽ trước để làm nền an toàn)
    # Nếu là Nam -> Màu Xanh, Nữ -> Màu Hồng
    base_color = BLUE if player.gender == "BOY" else PINK
    pygame.draw.circle(screen, base_color, (45, 45), 28)

    # 3. Xử lý và Vẽ Avatar đè lên
    gender_path = "player/boy/walk_1.png" if player.gender == "BOY" else "player/girl/walk_1.png"

    # Lấy ảnh gốc
    full_img = get_image(gender_path)
    if not full_img:
        alt_path = "player/boy/walk_01.png" if player.gender == "BOY" else "player/girl/walk_01.png"
        full_img = get_image(alt_path)

    if full_img:
        try:
            # --- LOGIC CẮT ẢNH ---
            w, h = full_img.get_size()
            crop_size = min(w, h)

            # Cắt phần đầu (Lấy hình vuông từ góc trên trái)
            face_surf = full_img.subsurface(pygame.Rect(0, 0, crop_size, crop_size)).copy()

            # Resize về 46x46 (Nhỏ hơn vòng tròn màu 56px một chút để tạo viền màu)
            avatar = pygame.transform.scale(face_surf, (46, 46))

            # Vẽ vào tâm vòng tròn (45, 45)
            # Tọa độ vẽ = Tâm - (Kích thước / 2)
            # x = 45 - 23 = 22
            # y = 45 - 23 = 22
            screen.blit(avatar, (22, 22))
        except Exception as e:
            print(f"Lỗi vẽ avatar: {e}")
            # Nếu lỗi thì thôi, vẫn còn hình tròn màu đã vẽ ở bước 2

    # 4. Vẽ Viền Vàng Sang Chảnh (Vẽ sau cùng để đè lên mép ảnh cho đẹp)
    pygame.draw.circle(screen, GOLD, (45, 45), 30, 3)

    # 5. Hiển thị Tên & Tiền
    draw_text_outline(screen, player_name, 20, 85, 25, BLACK, WHITE, align="left")
    draw_text_outline(screen, f"Tiền: {player.money}", 22, 85, 55, RED, WHITE, align="left")

    # 6. Nút chức năng
    btn_w = 60
    rect_shop = pygame.Rect(SCREEN_WIDTH - 80, 100, btn_w, btn_w)
    rect_bag = pygame.Rect(SCREEN_WIDTH - 80, 180, btn_w, btn_w)
    draw_icon_button(screen, rect_shop, "SHOP")
    draw_icon_button(screen, rect_bag, "BAG")

    return {"SHOP_BTN": rect_shop, "BAG_BTN": rect_bag}


def draw_popup_panel(screen, title, w, h):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(150)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    panel_x = (SCREEN_WIDTH - w) // 2
    panel_y = (SCREEN_HEIGHT - h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, w, h)
    pygame.draw.rect(screen, BROWN_BG, panel_rect, border_radius=15)
    pygame.draw.rect(screen, WOOD_DARK, panel_rect, 4, border_radius=15)

    banner_rect = pygame.Rect(panel_x + w // 2 - 120, panel_y - 30, 240, 60)
    pygame.draw.rect(screen, RED_LUCKY, banner_rect, border_radius=10)
    pygame.draw.rect(screen, GOLD, banner_rect, 2, border_radius=10)
    draw_text_outline(screen, title, 35, banner_rect.centerx, banner_rect.centery, GOLD, BLACK)

    close_btn = pygame.Rect(panel_x + w - 40, panel_y - 15, 35, 35)
    pygame.draw.rect(screen, RED, close_btn, border_radius=5)
    draw_text_outline(screen, "X", 25, close_btn.centerx, close_btn.centery, WHITE, BLACK)
    return panel_rect, close_btn


# ... (Phần đầu file giữ nguyên) ...

# --- [MỚI] HÀM HỖ TRỢ LẤY TÊN ẢNH ITEM ---
def get_item_icon_name(key):
    if key == "BuaThan":
        return "bua_than.png"
    elif key == "GiayGio":
        return "giay_gio.png"
    elif key == "BuaMay":
        return "bua_may.png"
    elif key == "DenDom":
        return "den_dom.png"
    elif key == "NamCham":
        return "nam_cham.png"
    return ""


# --- [CẬP NHẬT] HIỂN THỊ TÚI ĐỒ (CÓ ẢNH) ---
def draw_inventory_grid(screen, player):
    panel_w, panel_h = 600, 420
    panel_rect, close_btn = draw_popup_panel(screen, "TÚI ĐỒ", panel_w, panel_h)

    items_list = [(k, v) for k, v in player.inventory.items() if v > 0]

    slot_size = 80
    gap = 20
    cols = 5
    rows = 3

    grid_width = cols * slot_size + (cols - 1) * gap
    start_x = panel_rect.x + (panel_w - grid_width) // 2
    start_y = panel_rect.y + 90

    for row in range(rows):
        for col in range(cols):
            idx = row * 5 + col
            x = start_x + col * (slot_size + gap)
            y = start_y + row * (slot_size + gap)
            rect = pygame.Rect(x, y, slot_size, slot_size)

            pygame.draw.rect(screen, (245, 235, 215), rect, border_radius=10)
            pygame.draw.rect(screen, (101, 67, 33), rect, 2, border_radius=10)

            if idx < len(items_list):
                key, count = items_list[idx]

                # [SỬA] Hiển thị ảnh vật phẩm
                icon_name = get_item_icon_name(key)
                img = get_image(icon_name, 55, 55)

                if img:
                    screen.blit(img, (rect.centerx - 27, rect.centery - 35))
                else:
                    # Fallback nếu thiếu ảnh
                    pygame.draw.circle(screen, GRAY, rect.center, 28)
                    draw_text_outline(screen, key[:3], 14, rect.centerx, rect.centery, BLACK, WHITE)

                # Tên vật phẩm ở dưới
                vn_name = {"BuaThan": "Búa", "GiayGio": "Giày", "BuaMay": "Bùa", "DenDom": "Đèn",
                           "NamCham": "N.Châm"}.get(key, "???")
                draw_text_outline(screen, vn_name, 16, rect.centerx, rect.bottom - 15, BLACK, WHITE)

                # Số lượng
                qty_surf = get_font(18).render(f"x{count}", True, (200, 0, 0))
                screen.blit(qty_surf, (rect.right - qty_surf.get_width() - 5, rect.top + 2))

    return {"CLOSE": close_btn, "SLOTS": []}


# --- [CẬP NHẬT] POPUP SHOP (ĐÃ ĐẨY CHỮ LÊN CAO CHO CÂN ĐỐI) ---
def draw_shop_popup(screen, player, shop_items):
    panel_rect, close_btn = draw_popup_panel(screen, "CỬA HÀNG", 600, 400)
    start_x = panel_rect.x + 30
    start_y = panel_rect.y + 60
    buttons = []

    for i, (key, val) in enumerate(shop_items.items()):
        if i > 4: break

        item_rect = pygame.Rect(start_x, start_y + i * 65, 540, 55)
        pygame.draw.rect(screen, WHITE, item_rect, border_radius=10)

        # Vẽ ảnh vật phẩm
        icon_name = get_item_icon_name(key)
        img = get_image(icon_name, 45, 45)

        if img:
            screen.blit(img, (item_rect.x + 15, item_rect.centery - 22))
        else:
            pygame.draw.circle(screen, GREEN_DARK, (item_rect.x + 35, item_rect.centery), 22)

        # [FIX] Đẩy chữ lên cao hơn khoảng 7 pixel
        # Tên vật phẩm: item_rect.y + 12 -> item_rect.y + 5
        draw_text_outline(screen, val['desc'], 20, item_rect.x + 70, item_rect.y + 5, BLACK, WHITE, align="left")

        # Giá tiền: item_rect.y + 35 -> item_rect.y + 28
        draw_text_outline(screen, f"Giá: {val['price']} xu", 16, item_rect.x + 70, item_rect.y + 28, RED, WHITE,
                          align="left")

        # Nút Mua
        can_buy = player.money >= val['price']
        current_qty = player.inventory.get(key, 0)

        btn_rect = pygame.Rect(item_rect.right - 110, item_rect.y + 5, 100, 45)
        bg_col = GREEN_DARK if can_buy else GRAY

        pygame.draw.rect(screen, bg_col, btn_rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, btn_rect, 1, border_radius=5)

        draw_text_outline(screen, "MUA", 18, btn_rect.centerx, btn_rect.y + 15, WHITE, BLACK)
        if current_qty > 0:
            draw_text_outline(screen, f"Có: {current_qty}", 12, btn_rect.centerx, btn_rect.bottom - 5, GOLD, BLACK)

        buttons.append({"key": key, "rect": btn_rect, "price": val['price']})

    return {"CLOSE": close_btn, "BUY_BTNS": buttons}

def draw_survival_lobby(screen, level):
    draw_background(screen)
    draw_panel(screen, 100, 100, 600, 400)
    draw_text_outline(screen, f"HỘI LÀNG - CẤP ĐỘ {level}", 50, 400, 160, GOLD, BLACK)
    draw_text_outline(screen, "Hoàn thành thử thách để nhận quà!", 26, 400, 220, WHITE, BLACK)

    mp = pygame.mouse.get_pos()
    btn = pygame.Rect(275, 350, 250, 70)
    draw_button(screen, btn, "BẮT ĐẦU", btn.collidepoint(mp), False, BTN_GREEN)
    return btn


def draw_countdown(screen, count, game_name):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(150)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    draw_text_outline(screen, f"Trò chơi: {game_name}", 40, 400, 200, GOLD, BLACK)
    draw_text_outline(screen, str(count), 150, 400, 350, RED, WHITE)


# --- ÂM THANH AN TOÀN ---
_sound_cache = {}
SOUND_ENABLED = True


def set_sound_enabled(enabled):
    global SOUND_ENABLED
    SOUND_ENABLED = enabled
    if not SOUND_ENABLED and SOUND_SYSTEM_OK:
        pygame.mixer.stop()


def play_sound(name):
    global _sound_cache, SOUND_ENABLED
    if not SOUND_ENABLED or not SOUND_SYSTEM_OK: return

    if name not in _sound_cache:
        try:
            path = resource_path(os.path.join("assets", "sounds", name))
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                sound.set_volume(0.5)
                _sound_cache[name] = sound
            else:
                _sound_cache[name] = None
        except:
            _sound_cache[name] = None

    if _sound_cache.get(name):
        try:
            _sound_cache[name].play()
        except:
            pass


# --- HÀM VẼ INPUT BOX (ĐÃ CĂN CHỈNH LẠI CHỮ) ---
def draw_input_box(screen, rect, text, is_active):
    # Vẽ nền ô nhập
    color = GOLD if is_active else GRAY
    pygame.draw.rect(screen, WHITE, rect, border_radius=10)
    pygame.draw.rect(screen, color, rect, 3, border_radius=10)  # Viền dày hơn chút

    # [FIX] Đẩy chữ lên cao (rect.centery - 15) để không bị chạm đáy
    draw_text_outline(screen, text, 30, rect.x + 15, rect.centery - 15, BLACK, WHITE, align="left")

    # Vẽ con trỏ nhấp nháy (Cursor)
    if is_active and time.time() % 1 > 0.5:
        # Tính độ dài text để đặt con trỏ đúng chỗ
        font = get_font(30)
        txt_surf = font.render(text, True, BLACK)
        cursor_x = rect.x + 15 + txt_surf.get_width() + 2
        pygame.draw.line(screen, RED, (cursor_x, rect.y + 10), (cursor_x, rect.bottom - 10), 2)

    # Vẽ hướng dẫn nếu trống
    if not text and not is_active:
        draw_text_outline(screen, "Nhập tên...", 20, rect.x + 15, rect.centery - 10, (150, 150, 150), WHITE,
                          align="left")