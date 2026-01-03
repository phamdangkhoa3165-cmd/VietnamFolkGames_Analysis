import pygame
import os
import csv
import datetime
import time
import random

from game_engine.ui import *
from game_engine.player import Player
from game_engine.shop import SHOP_ITEMS_DATA, draw_shop, handle_shop_click
from game_engine.folk_games import play_dap_nieu, play_nhay_bao, play_hung_qua, play_xe_giay, play_ghep_hinh
from game_engine.effects import EffectManager
from game_engine.main_analysis import analyze_data
from game_engine.profile_manager import ProfileManager

if not os.path.exists('data'): os.makedirs('data')
LOG_FILE = 'data/raw_logs.csv'


# --- HÀM LƯU LOG ---
def save_log(player_name, game_type, level, result_data, items_snapshot, lives_left):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'player_name', 'game_type', 'level', 'score', 'metric1', 'metric2', 'result',
                             'items_list', 'lives_left'])

        items_str = "; ".join([f"{k} x{v}" for k, v in items_snapshot.items()]) if items_snapshot else "None"

        writer.writerow([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            player_name,
            game_type, level, result_data['score'],
            round(result_data['metric1'], 2), result_data['metric2'],
            "Win" if result_data['win'] else "Lose", items_str, lives_left
        ])


# --- HÀM LẤY ẢNH AVATAR (CẮT LẤY PHẦN ĐẦU) ---
def get_avatar_img(gender):
    # 1. Xác định đường dẫn
    path = f"player/boy/walk_1.png" if gender == "BOY" else f"player/girl/walk_1.png"

    # 2. Lấy ảnh gốc (Kích thước gốc)
    # Lưu ý: get_image mặc định trả về None nếu sai tên, nên ta không truyền size vào đây để lấy ảnh gốc
    full_img = get_image(path)

    if not full_img:
        # Fallback thử tên file khác
        path_alt = f"player/boy/walk_01.png" if gender == "BOY" else f"player/girl/walk_01.png"
        full_img = get_image(path_alt)

    if full_img:
        # 3. Xử lý CẮT ẢNH (CROP)
        w, h = full_img.get_size()

        # Lấy phần hình vuông ở trên cùng (phần đầu)
        # Kích thước cắt = chiều rộng của ảnh (để thành hình vuông)
        crop_size = min(w, h)

        # Tạo vùng cắt (x, y, w, h) -> Lấy từ góc (0,0)
        crop_rect = pygame.Rect(0, 0, crop_size, crop_size)

        # Cắt lấy phần đầu (subsurface)
        face_surf = full_img.subsurface(crop_rect).copy()

        # 4. Resize phần đầu về kích thước icon (50x50 hoặc 80x80 tùy chỗ dùng)
        # Hàm này trả về ảnh gốc đã cắt, việc resize sẽ do hàm vẽ quyết định
        return face_surf

    return None


# --- MÀN HÌNH QUẢN LÝ PROFILE (ĐÃ SỬA LỖI ẢNH TRÀN) ---
def draw_profile_screen(screen, profile_mgr, input_text, active_idx, mode="SELECT"):
    draw_background(screen)

    panel_w, panel_h = 700, 520
    panel_x = (SCREEN_WIDTH - panel_w) // 2
    panel_y = (SCREEN_HEIGHT - panel_h) // 2 + 10

    bg_wood = get_image("bg_table.png", panel_w, panel_h)
    if bg_wood:
        screen.blit(bg_wood, (panel_x, panel_y))
        pygame.draw.rect(screen, (60, 40, 20), (panel_x, panel_y, panel_w, panel_h), 5)
    else:
        draw_panel(screen, panel_x, panel_y, panel_w, panel_h, color=(101, 67, 33, 240))

    title = "CHỌN NGƯỜI CHƠI" if mode == "SELECT" else ("TẠO MỚI" if mode == "CREATE" else "ĐỔI TÊN")
    title_rect = pygame.Rect(panel_x + 100, panel_y - 25, 500, 60)
    pygame.draw.rect(screen, RED_LUCKY, title_rect, border_radius=15)
    pygame.draw.rect(screen, GOLD, title_rect, 3, border_radius=15)
    draw_text_outline(screen, title, 36, title_rect.centerx, title_rect.centery, GOLD, BLACK)

    mouse_pos = pygame.mouse.get_pos()
    buttons = {}

    if mode == "SELECT":
        start_y = panel_y + 60
        if not profile_mgr.profiles:
            draw_text_outline(screen, "(Chưa có tài khoản nào)", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE,
                              BLACK)

        for i, p_data in enumerate(profile_mgr.profiles):
            name = p_data["name"] if isinstance(p_data, dict) else p_data
            gender = p_data.get("gender", "BOY") if isinstance(p_data, dict) else "BOY"

            if i > 4: break
            row_y = start_y + i * 65
            rect = pygame.Rect(panel_x + 50, row_y, 400, 55)
            is_hover = rect.collidepoint(mouse_pos)
            col = (255, 245, 230) if is_hover else (240, 230, 210)

            pygame.draw.rect(screen, col, rect, border_radius=10)
            pygame.draw.rect(screen, (100, 70, 40), rect, 2, border_radius=10)

            # --- [FIX] XỬ LÝ AVATAR (THU NHỎ ĐỂ KHÔNG TRÀN) ---
            avatar = get_avatar_img(gender)
            if avatar:
                # 1. Thu nhỏ ảnh về 40x40 (Nhỏ hơn vòng tròn 50px để không bị lòi góc)
                avatar_small = pygame.transform.scale(avatar, (40, 40))

                # 2. Vẽ vòng tròn nền (Tâm tại rect.x + 35)
                pygame.draw.circle(screen, (220, 220, 220), (rect.x + 35, rect.centery), 25)
                pygame.draw.circle(screen, BLACK, (rect.x + 35, rect.centery), 25, 2)

                # 3. Vẽ ảnh vào chính giữa
                # Tâm X = rect.x + 35. Ảnh rộng 40 -> X vẽ = (rect.x + 35) - 20 = rect.x + 15
                # Tâm Y = rect.centery. Ảnh cao 40 -> Y vẽ = rect.centery - 20
                screen.blit(avatar_small, (rect.x + 15, rect.centery - 20))
            else:
                pygame.draw.circle(screen, (150, 150, 150), (rect.x + 35, rect.centery), 25)

            # Tên người chơi
            draw_text_outline(screen, name, 26, rect.x + 80, rect.centery - 15, (139, 69, 19), WHITE, align="left")

            del_rect = pygame.Rect(rect.right + 10, row_y, 55, 55)
            draw_button(screen, del_rect, "X", del_rect.collidepoint(mouse_pos), bg_color=RED)

            edit_rect = pygame.Rect(del_rect.right + 10, row_y, 80, 55)
            draw_button(screen, edit_rect, "Sửa", edit_rect.collidepoint(mouse_pos), bg_color=(70, 130, 180))

            buttons[f"SELECT_{name}"] = rect
            buttons[f"DELETE_{name}"] = del_rect
            buttons[f"RENAME_{name}"] = edit_rect

        btn_new = pygame.Rect(panel_x + 200, panel_y + panel_h - 70, 300, 55)
        draw_button(screen, btn_new, "+ THÊM MỚI", btn_new.collidepoint(mouse_pos), bg_color=GREEN_DARK)
        buttons["NEW"] = btn_new

    elif mode == "CREATE" or mode == "RENAME":
        draw_text_outline(screen, "Nhập tên của bạn:", 24, SCREEN_WIDTH // 2, panel_y + 80, WHITE, BLACK)

        input_rect = pygame.Rect(panel_x + 100, panel_y + 110, 500, 60)
        draw_input_box(screen, input_rect, input_text, True)

        if mode == "CREATE":
            draw_text_outline(screen, "Giới tính:", 24, panel_x + 100, panel_y + 190, WHITE, BLACK, align="left")

            btn_boy = pygame.Rect(panel_x + 220, panel_y + 180, 100, 100)
            col_boy = BLUE if active_idx == "BOY" else (100, 100, 100)
            pygame.draw.rect(screen, col_boy, btn_boy, border_radius=10)
            pygame.draw.rect(screen, GOLD if active_idx == "BOY" else BLACK, btn_boy, 3, border_radius=10)

            boy_img = get_avatar_img("BOY")
            if boy_img:
                # Thu nhỏ ảnh cho nút chọn
                screen.blit(pygame.transform.scale(boy_img, (80, 80)), (btn_boy.x + 10, btn_boy.y + 10))
            draw_text_outline(screen, "NAM", 16, btn_boy.centerx, btn_boy.bottom + 15, WHITE, BLACK)

            btn_girl = pygame.Rect(panel_x + 380, panel_y + 180, 100, 100)
            col_girl = PINK if active_idx == "GIRL" else (100, 100, 100)
            pygame.draw.rect(screen, col_girl, btn_girl, border_radius=10)
            pygame.draw.rect(screen, GOLD if active_idx == "GIRL" else BLACK, btn_girl, 3, border_radius=10)

            girl_img = get_avatar_img("GIRL")
            if girl_img:
                # Thu nhỏ ảnh cho nút chọn
                screen.blit(pygame.transform.scale(girl_img, (80, 80)), (btn_girl.x + 10, btn_girl.y + 10))
            draw_text_outline(screen, "NỮ", 16, btn_girl.centerx, btn_girl.bottom + 15, WHITE, BLACK)

            buttons["SEL_BOY"] = btn_boy
            buttons["SEL_GIRL"] = btn_girl

        btn_y = panel_y + 350
        btn_ok = pygame.Rect(panel_x + 100, btn_y, 200, 60)
        btn_cancel = pygame.Rect(panel_x + 400, btn_y, 200, 60)

        draw_button(screen, btn_ok, "LƯU", btn_ok.collidepoint(mouse_pos), bg_color=GREEN_DARK)
        draw_button(screen, btn_cancel, "HỦY", btn_cancel.collidepoint(mouse_pos), bg_color=WOOD_DARK)

        buttons["OK"] = btn_ok
        buttons["CANCEL"] = btn_cancel

    return buttons


# --- MAIN MENU ---
def draw_main_menu(screen):
    draw_background(screen)
    draw_panel(screen, 150, 40, 500, 520, color=(0, 0, 0, 200))
    draw_text_outline(screen, "TRÒ CHƠI DÂN GIAN", 55, 400, 90, GOLD, BLACK)

    mp = pygame.mouse.get_pos()
    btn_start = pygame.Rect(250, 160, 300, 60)
    draw_button(screen, btn_start, "BẮT ĐẦU", btn_start.collidepoint(mp))

    btn_setting = pygame.Rect(250, 230, 300, 60)
    draw_button(screen, btn_setting, "CÀI ĐẶT", btn_setting.collidepoint(mp))

    btn_stats = pygame.Rect(250, 300, 300, 60)
    draw_button(screen, btn_stats, "THỐNG KÊ", btn_stats.collidepoint(mp), bg_color=(70, 130, 180))

    btn_profile = pygame.Rect(250, 370, 300, 60)
    draw_button(screen, btn_profile, "ĐỔI TÀI KHOẢN", btn_profile.collidepoint(mp), bg_color=(200, 100, 50))

    btn_quit = pygame.Rect(250, 440, 300, 60)
    draw_button(screen, btn_quit, "THOÁT GAME", btn_quit.collidepoint(mp), bg_color=WOOD_DARK)

    return {"START": btn_start, "SETTINGS": btn_setting, "STATS": btn_stats, "PROFILE": btn_profile, "QUIT": btn_quit}


def draw_settings(screen, sound_on):
    draw_background(screen)
    draw_panel(screen, 200, 100, 400, 400)
    draw_text_outline(screen, "CÀI ĐẶT", 50, 400, 160, GOLD, BLACK)
    mp = pygame.mouse.get_pos()
    btn_sound = pygame.Rect(250, 220, 300, 60)
    col = GREEN_DARK if sound_on else RED
    draw_button(screen, btn_sound, f"ÂM THANH: {'BẬT' if sound_on else 'TẮT'}", btn_sound.collidepoint(mp),
                bg_color=col)
    btn_reset = pygame.Rect(250, 300, 300, 60)
    draw_button(screen, btn_reset, "XÓA DỮ LIỆU CŨ", btn_reset.collidepoint(mp), bg_color=(200, 100, 50))
    btn_ok = pygame.Rect(300, 400, 200, 60)
    draw_button(screen, btn_ok, "XONG", btn_ok.collidepoint(mp))
    return {"SOUND": btn_sound, "RESET": btn_reset, "OK": btn_ok}


def reset_data():
    try:
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        processed = os.path.join(os.path.dirname(LOG_FILE), 'processed_data.csv')
        if os.path.exists(processed): os.remove(processed)
        img = os.path.join(os.path.dirname(LOG_FILE), 'analysis_report.png')
        if os.path.exists(img): os.remove(img)
    except:
        pass


# --- GAMEPLAY & SURVIVAL (GIỮ NGUYÊN) ---
def run_inter_level_shop(screen, player):
    in_shop = True
    while in_shop:
        buttons = draw_shop(screen, player, mode="INTER_LEVEL")
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_GAME"
            if event.type == pygame.MOUSEBUTTONDOWN:
                action = handle_shop_click(event.pos, player, buttons)
                if action == "PLAY":
                    return "NEXT_LEVEL"
                elif action == "LOTO":
                    play_xe_giay(screen, player)
                elif action == "BACK":
                    return "QUIT_RUN"
    return "NEXT_LEVEL"


def run_survival_mode(screen, player, current_player_name):
    lives = 3
    current_level = 1
    games_list = ["DapNieu", "NhayBaoBo", "HungQua", "GhepHinh"]

    in_lobby = True
    while in_lobby:
        btn_start = draw_survival_lobby(screen, current_level)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_GAME"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_start.collidepoint(event.pos):
                    play_sound("hit.wav");
                    in_lobby = False

    while lives > 0:
        game_index = (current_level - 1) % len(games_list)
        game_name_raw = games_list[game_index]
        game_name_vn = {
            "DapNieu": "Đập Niêu Đất", "NhayBaoBo": "Nhảy Bao Bố",
            "HungQua": "Hứng Trái Cây", "GhepHinh": "Ghép Tranh Làng Quê"
        }.get(game_name_raw, game_name_raw)

        for i in range(3, 0, -1):
            draw_background(screen);
            draw_countdown(screen, i, game_name_vn)
            pygame.display.flip();
            play_sound("tick.wav");
            time.sleep(1)

        items_snapshot = player.inventory.copy()
        result = None
        if game_name_raw == "DapNieu":
            result = play_dap_nieu(screen, player, current_level)
        elif game_name_raw == "NhayBaoBo":
            result = play_nhay_bao(screen, player, current_level)
        elif game_name_raw == "HungQua":
            result = play_hung_qua(screen, player, current_level)
        elif game_name_raw == "GhepHinh":
            result = play_ghep_hinh(screen, player, current_level)

        if result is None: return "MAP"

        save_log(current_player_name, game_name_raw, current_level, result, items_snapshot, lives)

        if result['win']:
            player.money += result['score'];
            current_level += 1
            action = run_inter_level_shop(screen, player)
            if action == "QUIT_GAME": return "QUIT_GAME"
            if action == "QUIT_RUN": break
        else:
            lives -= 1
            draw_panel(screen, 200, 250, 400, 100)
            draw_text_outline(screen, "MẤT 1 MẠNG!", 50, 400, 300, RED, WHITE)
            pygame.display.flip();
            play_sound("wrong.wav");
            time.sleep(1.5)

    if lives <= 0:
        draw_background(screen);
        draw_panel(screen, 100, 150, 600, 300)
        draw_text_outline(screen, "KẾT THÚC HỘI LÀNG", 60, 400, 230, RED, BLACK)
        draw_text_outline(screen, f"Đạt cấp độ: {current_level}", 30, 400, 300, WHITE, BLACK)
        pygame.display.flip();
        time.sleep(3)
    return "MAP"


# --- MAIN LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    player = Player()
    profile_mgr = ProfileManager()

    running = True
    current_state = "PROFILE_SELECT"
    current_player_name = "Guest"
    input_text = "";
    rename_target = ""
    # Biến lưu giới tính đang chọn khi tạo mới
    selected_gender_create = "BOY"

    sound_on = True
    clock = pygame.time.Clock()
    popup_state = None;
    zone_village = pygame.Rect(80, 520, 120, 40);
    zone_loto = pygame.Rect(600, 520, 120, 40)
    map_fx = EffectManager();
    click_effect = None

    while running:
        dt = clock.tick(60)
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT: running = False

        if current_state == "PROFILE_SELECT":
            buttons = draw_profile_screen(screen, profile_mgr, "", -1, "SELECT")
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if buttons.get("NEW") and buttons["NEW"].collidepoint(event.pos):
                        play_sound("hit.wav")
                        current_state = "PROFILE_CREATE"
                        input_text = ""
                        selected_gender_create = "BOY"  # Mặc định chọn Nam
                    else:
                        for p_data in profile_mgr.profiles:
                            name = p_data["name"]
                            if buttons.get(f"SELECT_{name}") and buttons[f"SELECT_{name}"].collidepoint(event.pos):
                                play_sound("hit.wav")
                                current_player_name = name
                                # [QUAN TRỌNG] Load giới tính của người chơi này
                                gender = profile_mgr.get_gender(name)
                                player.set_gender(gender)
                                player.x, player.y = 400, 480;
                                player.target_x, player.target_y = 400, 480
                                current_state = "MAIN_MENU"
                            elif buttons.get(f"DELETE_{name}") and buttons[f"DELETE_{name}"].collidepoint(event.pos):
                                play_sound("wrong.wav");
                                profile_mgr.delete_profile(name)
                            elif buttons.get(f"RENAME_{name}") and buttons[f"RENAME_{name}"].collidepoint(event.pos):
                                play_sound("hit.wav");
                                current_state = "PROFILE_RENAME";
                                input_text = name;
                                rename_target = name

        elif current_state in ["PROFILE_CREATE", "PROFILE_RENAME"]:
            mode = "CREATE" if current_state == "PROFILE_CREATE" else "RENAME"
            buttons = draw_profile_screen(screen, profile_mgr, input_text, selected_gender_create, mode)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif len(input_text) < 12:
                        input_text += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mode == "CREATE":
                        # Xử lý nút chọn giới tính
                        if buttons.get("SEL_BOY") and buttons["SEL_BOY"].collidepoint(event.pos):
                            selected_gender_create = "BOY";
                            play_sound("hit.wav")
                        elif buttons.get("SEL_GIRL") and buttons["SEL_GIRL"].collidepoint(event.pos):
                            selected_gender_create = "GIRL";
                            play_sound("hit.wav")

                    if buttons["OK"].collidepoint(event.pos):
                        play_sound("correct.wav")
                        if mode == "CREATE":
                            # Lưu kèm giới tính
                            profile_mgr.add_profile(input_text, selected_gender_create)
                        else:
                            profile_mgr.rename_profile(rename_target, input_text)
                        current_state = "PROFILE_SELECT"
                    elif buttons["CANCEL"].collidepoint(event.pos):
                        play_sound("hit.wav");
                        current_state = "PROFILE_SELECT"

        elif current_state == "MAIN_MENU":
            buttons = draw_main_menu(screen)
            draw_text_outline(screen, f"Chào: {current_player_name}", 24, 150, 30, WHITE, BLACK)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if buttons["START"].collidepoint(event.pos):
                        play_sound("hit.wav");
                        # Bỏ qua màn hình CHARACTER_SELECT cũ vì đã chọn lúc tạo profile
                        current_state = "MAP"
                    elif buttons["SETTINGS"].collidepoint(event.pos):
                        play_sound("hit.wav");
                        current_state = "SETTINGS"
                    elif buttons["STATS"].collidepoint(event.pos):
                        play_sound("hit.wav")
                        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
                            analyze_data()
                        else:
                            draw_panel(screen, 200, 250, 400, 100)
                            draw_text_outline(screen, "CHƯA CÓ DỮ LIỆU!", 40, 400, 300, RED, WHITE)
                            pygame.display.flip();
                            time.sleep(1)
                    elif buttons["PROFILE"].collidepoint(event.pos):
                        play_sound("hit.wav");
                        current_state = "PROFILE_SELECT"
                    elif buttons["QUIT"].collidepoint(event.pos):
                        running = False

        # --- BỎ QUA STATE CHARACTER_SELECT (VÌ ĐÃ CHỌN LÚC TẠO PROFILE) ---

        elif current_state == "SETTINGS":
            buttons = draw_settings(screen, sound_on)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if buttons["OK"].collidepoint(event.pos):
                        play_sound("hit.wav"); current_state = "MAIN_MENU"
                    elif buttons["SOUND"].collidepoint(event.pos):
                        sound_on = not sound_on; set_sound_enabled(sound_on)
                    elif buttons["RESET"].collidepoint(event.pos):
                        play_sound("hit.wav");
                        reset_data()
                        draw_panel(screen, 200, 250, 400, 100)
                        draw_text_outline(screen, "ĐÃ XÓA DỮ LIỆU!", 40, 400, 300, RED, WHITE)
                        pygame.display.flip();
                        time.sleep(1)

        elif current_state == "MAP":
            draw_background(screen, 0);
            map_fx.update();
            map_fx.draw(screen)
            if popup_state is None: player.update_position(SCREEN_HEIGHT, SCREEN_WIDTH)

            near_v = player.rect.colliderect(zone_village)
            near_l = player.rect.colliderect(zone_loto)
            draw_interaction_zone(screen, zone_village, "ĐÌNH LÀNG", near_v, 0)
            draw_interaction_zone(screen, zone_loto, "SẠP VÉ SỐ", near_l, 0)

            if click_effect:
                rad = 30 - click_effect['timer'];
                pygame.draw.circle(screen, WHITE, (click_effect['x'], click_effect['y']), rad, 2)
                click_effect['timer'] -= 2;
                if click_effect['timer'] <= 0: click_effect = None

            player.draw(screen)
            hud = draw_hud(screen, player, current_player_name)

            popup_ui = None
            if popup_state == "INVENTORY":
                popup_ui = draw_inventory_grid(screen, player)
            elif popup_state == "SHOP":
                popup_ui = draw_shop_popup(screen, player, SHOP_ITEMS_DATA)

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if popup_state:
                            popup_state = None
                        else:
                            current_state = "MAIN_MENU"
                    if not popup_state and event.key == pygame.K_SPACE:
                        if near_v:
                            play_sound("hit.wav"); player.is_moving = False; current_state = "GAME_SURVIVAL"
                        elif near_l:
                            play_sound("hit.wav"); player.is_moving = False; current_state = "GAME_LOTO"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if popup_state:
                        if popup_ui["CLOSE"].collidepoint(event.pos):
                            play_sound("hit.wav"); popup_state = None
                        elif popup_state == "SHOP":
                            for btn in popup_ui["BUY_BTNS"]:
                                if btn["rect"].collidepoint(event.pos):
                                    if player.money >= btn["price"]:
                                        player.money -= btn["price"]; player.add_item(btn["key"]); play_sound(
                                            "correct.wav")
                                    else:
                                        play_sound("wrong.wav")
                    elif not popup_state:
                        if hud["SHOP_BTN"].collidepoint(event.pos):
                            play_sound("hit.wav"); popup_state = "SHOP"; player.is_moving = False
                        elif hud["BAG_BTN"].collidepoint(event.pos):
                            play_sound("hit.wav"); popup_state = "INVENTORY"; player.is_moving = False
                        else:
                            player.set_target(event.pos, 0); click_effect = {'x': event.pos[0], 'y': event.pos[1],
                                                                             'timer': 20}

        elif current_state == "GAME_SURVIVAL":
            if run_survival_mode(screen, player, current_player_name) == "QUIT_GAME":
                running = False
            else:
                current_state = "MAP"; player.is_moving = False; player.x, player.y = 150, 520; player.target_x, player.target_y = 150, 520

        elif current_state == "GAME_LOTO":
            play_xe_giay(screen, player)
            current_state = "MAP";
            player.is_moving = False;
            player.x, player.y = 550, 520;
            player.target_x, player.target_y = 550, 520

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()