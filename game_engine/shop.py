import pygame
from .ui import *

# CẤU HÌNH VẬT PHẨM
SHOP_ITEMS_DATA = {
    "BuaThan": {"price": 50, "name": "Búa Thần", "desc": "Đập Niêu - X2 Điểm"},
    "GiayGio": {"price": 30, "name": "Giày Gió", "desc": "Chạy Nhanh"},
    "BuaMay": {"price": 20, "name": "Bùa May", "desc": "Vé Số - Tăng hên"},
    "DenDom": {"price": 40, "name": "Đèn Đóm", "desc": "Ghép Hình - Gợi ý"},
    "NamCham": {"price": 40, "name": "Nam Châm", "desc": "Hứng Quả - Hút xa"}
}


def draw_shop(screen, player, mode="MAIN_MENU"):
    draw_background(screen)

    # 1. Vẽ Bảng Gỗ
    panel_w, panel_h = 700, 520
    panel_x = (SCREEN_WIDTH - panel_w) // 2
    panel_y = (SCREEN_HEIGHT - panel_h) // 2 + 10

    bg_wood = get_image("bg_table.png", panel_w, panel_h)
    if bg_wood:
        screen.blit(bg_wood, (panel_x, panel_y))
        pygame.draw.rect(screen, (60, 40, 20), (panel_x, panel_y, panel_w, panel_h), 5)
    else:
        draw_panel(screen, panel_x, panel_y, panel_w, panel_h, color=(101, 67, 33, 240))

    # 2. Tiêu đề (ĐÃ SỬA: Font nhỏ hơn để vừa ô)
    title_text = "TRẠM DỪNG CHÂN" if mode == "INTER_LEVEL" else "CỬA HÀNG"
    title_bg_rect = pygame.Rect(panel_x + 150, panel_y - 25, 400, 60)  # Tăng chiều cao ô lên 60
    pygame.draw.rect(screen, RED_LUCKY, title_bg_rect, border_radius=15)
    pygame.draw.rect(screen, GOLD, title_bg_rect, 3, border_radius=15)
    # Giảm cỡ chữ xuống 32 (cũ là 40)
    draw_text_outline(screen, title_text, 32, title_bg_rect.centerx, title_bg_rect.centery, GOLD, BLACK)

    # 3. Thông tin Tiền & Túi
    draw_text_outline(screen, f"Tiền: {player.money} xu", 24, panel_x + 100, panel_y + 50, WHITE, BLACK)
    items_count = sum(player.inventory.values())
    draw_text_outline(screen, f"Túi: {items_count} món", 22, panel_x + panel_w - 100, panel_y + 50, PAPER, BLACK)

    # 4. Danh Sách Vật Phẩm
    mouse_pos = pygame.mouse.get_pos()
    start_y = panel_y + 85
    item_height = 65
    gap = 8

    for i, (key, val) in enumerate(SHOP_ITEMS_DATA.items()):
        item_y = start_y + i * (item_height + gap)
        item_rect = pygame.Rect(panel_x + 30, item_y, panel_w - 60, item_height)
        val['rect'] = item_rect

        is_hover = item_rect.collidepoint(mouse_pos)
        can_buy = player.money >= val['price']

        if is_hover:
            bg_col = (255, 245, 230)
            border_col = GOLD
        else:
            bg_col = (240, 230, 210)
            border_col = (100, 70, 40)

        pygame.draw.rect(screen, bg_col, item_rect, border_radius=10)
        pygame.draw.rect(screen, border_col, item_rect, 2, border_radius=10)

        # Icon
        icon_name = ""
        if key == "BuaThan":
            icon_name = "bua_than.png"
        elif key == "GiayGio":
            icon_name = "giay_gio.png"
        elif key == "BuaMay":
            icon_name = "bua_may.png"
        elif key == "DenDom":
            icon_name = "den_dom.png"
        elif key == "NamCham":
            icon_name = "nam_cham.png"

        img = get_image(icon_name, 50, 50)
        if img:
            screen.blit(img, (item_rect.x + 15, item_rect.centery - 25))
        else:
            pygame.draw.circle(screen, GRAY, (item_rect.x + 40, item_rect.centery), 25)

        # Tên & Mô tả
        draw_text_outline(screen, val['name'], 22, item_rect.x + 80, item_rect.y + 10, (139, 69, 19), WHITE,
                          align="left")
        draw_text_outline(screen, val['desc'], 16, item_rect.x + 80, item_rect.y + 36, (80, 80, 80), WHITE,
                          align="left")

        # Nút Mua
        buy_btn_rect = pygame.Rect(item_rect.right - 130, item_rect.y + 10, 120, 45)
        btn_col = GREEN_DARK if can_buy else (100, 100, 100)
        pygame.draw.rect(screen, btn_col, buy_btn_rect, border_radius=8)

        price_col = GOLD if can_buy else (200, 200, 200)
        draw_text_outline(screen, f"{val['price']} xu", 20, buy_btn_rect.centerx, buy_btn_rect.y + 15, price_col, BLACK)

        current_qty = player.inventory.get(key, 0)
        qty_txt = f"Có: {current_qty}" if current_qty > 0 else ""
        if qty_txt:
            draw_text_outline(screen, qty_txt, 12, buy_btn_rect.centerx, buy_btn_rect.bottom - 2, WHITE, BLACK)

    # 5. Các nút chức năng
    btn_y_bottom = panel_y + panel_h - 60

    btn_loto = pygame.Rect(panel_x + 40, btn_y_bottom, 180, 45)
    is_loto_hover = btn_loto.collidepoint(mouse_pos)
    draw_button(screen, btn_loto, "XÉ VÉ SỐ", is_loto_hover, False, bg_color=RED_LUCKY)

    btn_play = pygame.Rect(panel_x + panel_w - 220, btn_y_bottom, 180, 45)
    play_lbl = "VÀO CHƠI" if mode == "MAIN_MENU" else "TIẾP TỤC"
    is_play_hover = btn_play.collidepoint(mouse_pos)
    draw_button(screen, btn_play, play_lbl, is_play_hover, False, bg_color=GREEN_DARK)

    # Nút Thoát (ĐÃ SỬA: To hơn để chứa vừa chữ)
    # Tăng width lên 120 (cũ là 80), height lên 50 (cũ là 40)
    btn_back = pygame.Rect(20, 20, 120, 50)
    is_back_hover = btn_back.collidepoint(mouse_pos)
    draw_button(screen, btn_back, "THOÁT", is_back_hover, False, bg_color=WOOD_DARK)

    return {"PLAY": btn_play, "LOTO": btn_loto, "BACK": btn_back}


def handle_shop_click(pos, player, buttons):
    for key, val in SHOP_ITEMS_DATA.items():
        if 'rect' in val and val['rect'].collidepoint(pos):
            if player.money >= val['price']:
                player.money -= val['price']
                player.add_item(key)
                play_sound("correct.wav")
            else:
                play_sound("wrong.wav")
            return "STAY"

    if buttons["PLAY"].collidepoint(pos):
        play_sound("hit.wav")
        return "PLAY"
    if buttons["LOTO"].collidepoint(pos):
        play_sound("hit.wav")
        return "LOTO"
    if buttons["BACK"].collidepoint(pos):
        play_sound("hit.wav")
        return "BACK"

    return "STAY"