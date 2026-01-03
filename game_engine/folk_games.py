import pygame
import random
import time
import math
from .ui import *
from .effects import EffectManager


# --- [CẬP NHẬT] HÀM VẼ NÚT VẬT PHẨM MỚI ---
def draw_item_toggle(screen, img_name, x, y, is_active, label="", count=0):
    rect = pygame.Rect(x, y, 70, 70)

    # Màu nền: Xanh nếu đang Dùng, Xám nếu Hết/Chưa dùng
    if is_active:
        bg_color = (50, 200, 50)
        border_col = GOLD
    else:
        bg_color = (100, 100, 100) if count > 0 else (60, 60, 60)
        border_col = WHITE if count > 0 else GRAY

    pygame.draw.rect(screen, bg_color, rect, border_radius=10)
    pygame.draw.rect(screen, border_col, rect, 2, border_radius=10)

    # Vẽ icon vật phẩm
    img = get_image(img_name, 45, 45)
    if img:
        # Nếu hết hàng thì vẽ mờ đi
        if count == 0 and not is_active:
            img.set_alpha(100)
        else:
            img.set_alpha(255)
        screen.blit(img, (rect.centerx - 22, rect.centery - 25))

    # --- [LOGIC HIỂN THỊ CHỮ MỚI] ---
    if is_active:
        # Đang dùng -> Hiện "ĐÃ DÙNG"
        draw_text_outline(screen, "ĐÃ DÙNG", 14, rect.centerx, rect.bottom - 12, WHITE, BLACK)
    else:
        # Chưa dùng -> Hiện số lượng "xN" hoặc "HẾT"
        if count > 0:
            draw_text_outline(screen, f"x{count}", 22, rect.right - 10, rect.bottom - 15, GOLD, BLACK)
        else:
            draw_text_outline(screen, "HẾT", 14, rect.centerx, rect.bottom - 12, GRAY, BLACK)

    # Tên vật phẩm (nhỏ ở trên cùng)
    if label:
        draw_text_outline(screen, label, 11, rect.centerx, rect.top + 8, WHITE, BLACK)

    return rect


def run_pause_menu_loop(screen):
    paused = True
    while paused:
        buttons = draw_pause_menu(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "EXIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["RESUME"].collidepoint(event.pos):
                    play_sound("hit.wav")
                    return "RESUME"
                elif buttons["EXIT"].collidepoint(event.pos):
                    play_sound("hit.wav")
                    pygame.mouse.set_visible(True)
                    return "EXIT"
    return "RESUME"


# --- GAME 1: ĐẬP NIÊU ---
def play_dap_nieu(screen, player, level=1):
    clock = pygame.time.Clock()
    is_active = False

    target = pygame.Rect(random.randint(50, 700), random.randint(450, 530), 60, 60)
    score = 0;
    clicks = 0;
    duration = 15
    spawn_interval = max(0.5, 2.0 - (level * 0.2))
    start_time = time.time();
    last_spawn = time.time();
    time_offset = 0
    fx_manager = EffectManager()
    running = True

    bg_img = get_image("bg_dap_nieu.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
    nieu_img = get_image("nieu.png", 60, 60)

    # [FIX] Tải ảnh búa và xử lý fallback
    bua_std = get_image("bua.png", 50, 50)
    bua_god = get_image("bua_than.png", 50, 50)
    # Nếu không có ảnh búa thần thì dùng búa thường thay thế
    if not bua_god: bua_god = bua_std

    while running:
        dt = clock.tick(60)
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill((200, 150, 100))

        elapsed = time.time() - start_time - time_offset
        time_left = max(0, duration - elapsed)
        if time_left <= 0: running = False

        if time.time() - last_spawn - time_offset > spawn_interval:
            target.topleft = (random.randint(50, 700), random.randint(450, 530))
            last_spawn = time.time() - time_offset

        # Nút Búa
        qty = player.inventory.get("BuaThan", 0)
        item_btn = draw_item_toggle(screen, "bua_than.png", SCREEN_WIDTH - 90, 80, is_active, "Búa", qty)

        btn_pause = draw_pause_button_icon(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_pause.collidepoint(event.pos):
                    st = time.time()
                    if run_pause_menu_loop(screen) == "EXIT": return None
                    time_offset += time.time() - st

                elif item_btn.collidepoint(event.pos):
                    if not is_active and player.has_item("BuaThan"):
                        player.use_item("BuaThan")
                        is_active = True
                        play_sound("correct.wav")
                    elif is_active:
                        pass
                    else:
                        play_sound("wrong.wav")

                else:
                    clicks += 1
                    if target.collidepoint(event.pos):
                        play_sound("hit.wav")
                        fx_manager.create_explosion(event.pos[0], event.pos[1], (200, 100, 50))
                        points = 20 if is_active else 10
                        color = RED if is_active else GOLD
                        fx_manager.create_text(event.pos[0], event.pos[1], f"+{points}", color)
                        score += points
                        target.topleft = (random.randint(50, 700), random.randint(450, 530))
                        last_spawn = time.time() - time_offset

        pygame.draw.ellipse(screen, (0, 0, 0, 80), (target.x + 5, target.bottom - 10, 50, 15))
        if nieu_img:
            screen.blit(nieu_img, target)
        else:
            pygame.draw.rect(screen, RED, target)

        fx_manager.update();
        fx_manager.draw(screen)

        mx, my = pygame.mouse.get_pos()
        pygame.mouse.set_visible(False)
        if item_btn.collidepoint((mx, my)) or btn_pause.collidepoint((mx, my)):
            pygame.mouse.set_visible(True)
        else:
            # Chọn ảnh búa để vẽ
            cur_bua = bua_god if is_active else bua_std

            if cur_bua:
                screen.blit(cur_bua, (mx - 25, my - 25))
            else:
                # Chỉ hiện chấm đen nếu CẢ 2 ảnh búa đều không có
                pygame.draw.circle(screen, BLACK, (mx, my), 10)

        draw_timer_bar(screen, 50, 10, 700, 30, time_left, duration)
        draw_text_outline(screen, f"Điểm: {score}", 30, 100, 70, GOLD, BLACK)
        if is_active: draw_text_outline(screen, "X2 ĐIỂM!", 20, 150, 100, RED, WHITE)

        pygame.display.flip()

    pygame.mouse.set_visible(True)
    return {"score": score, "metric1": 0, "metric2": clicks, "win": score >= (20 + level * 10)}


# --- GAME 2: NHẢY BAO BỐ (CHỈNH SỬA ĐỘ NHÚN THẬT HƠN) ---
def play_nhay_bao(screen, player, level=1):
    clock = pygame.time.Clock()
    bg_img = get_image("bg_bao_bo.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)

    is_active = False

    finish_line_x = 700;
    GOAL = 1000;
    player_dist = 0;
    presses = 0

    # Bot thông minh
    bot_speed = 0.35 + (level * 0.08)
    racers = [
        {"type": "BOT", "name": f"Máy {i}", "y": 360 + i * 35, "scale": 45 + i * 10, "dist": 0, "speed": bot_speed,
         "dash": 0, "aggression": i + 1}
        for i in range(4)
    ]
    player_y = 430;
    player_scale = 65

    start_time = time.time();
    fx_manager = EffectManager();
    running = True;
    result = "Lose"

    while running:
        clock.tick(60)
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(GREEN)

        # Vẽ đường đua
        pygame.draw.line(screen, (200, 50, 50), (finish_line_x, 350), (finish_line_x, 600), 5)
        for i in range(0, 800, 150):
            draw_x = (i - (player_dist % 150))
            if draw_x < 0: draw_x += 800
            pygame.draw.circle(screen, (34, 139, 34), (draw_x, 380), 4)
            pygame.draw.circle(screen, (34, 139, 34), (draw_x + 30, 550), 5)

        # Nút Vật Phẩm
        qty = player.inventory.get("GiayGio", 0)
        item_btn = draw_item_toggle(screen, "giay_gio.png", SCREEN_WIDTH - 90, 80, is_active, "Giày", qty)

        btn_pause = draw_pause_button_icon(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_pause.collidepoint(event.pos):
                    if run_pause_menu_loop(screen) == "EXIT": return None
                elif item_btn.collidepoint(event.pos):
                    if not is_active and player.has_item("GiayGio"):
                        player.use_item("GiayGio")
                        is_active = True
                        play_sound("correct.wav")
                    elif is_active:
                        pass
                    else:
                        play_sound("wrong.wav")

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE]:
                    presses += 1
                    step = 45 if is_active else 28
                    player_dist += step

                    # Hiệu ứng bụi đất
                    px = int((player_dist / GOAL) * 600) + 50
                    col = CYAN if is_active else (160, 82, 45)
                    fx_manager.create_explosion(px, player_y + 30, col, count=5)
                    play_sound("jump.wav")

        # AI LOGIC
        for r in racers:
            current_move = r["speed"] * random.uniform(0.9, 1.4)
            if r["dist"] < player_dist - 50: current_move *= 1.15

            dist_left = GOAL - r["dist"]
            if dist_left < 250 and random.randint(0, 20) < r["aggression"]: r["dash"] = 30
            if r["dash"] <= 0 and random.randint(0, 100) < (1 + r["aggression"]): r["dash"] = 40

            if r["dash"] > 0:
                current_move *= 1.8
                r["dash"] -= 1
                if r["dash"] % 8 == 0:
                    bx = int((r["dist"] / GOAL) * 600) + 50
                    fx_manager.create_explosion(bx, r["y"] + 20, (200, 200, 200), count=3)

            r["dist"] += current_move
            if r["dist"] >= GOAL: result = "Lose"; running = False

        if player_dist >= GOAL: result = "Win"; running = False

        # Vẽ nhân vật
        draw_list = list(racers)
        draw_list.append({"type": "PLAYER", "name": "BẠN", "y": player_y, "scale": player_scale, "dist": player_dist})
        draw_list.sort(key=lambda x: x["y"])

        current_rank = 1
        for r in racers:
            if r["dist"] > player_dist: current_rank += 1

        for c in draw_list:
            cx = int((c["dist"] / GOAL) * 600) + 50
            cy = c["y"]

            bounce = 0
            if c["type"] == "PLAYER":
                # [ĐÃ SỬA] Độ nhún chậm lại và cao hơn
                # time.time() * 12: Tốc độ nhún chậm (cũ là 25)
                # * 35: Độ cao nhún cao hơn (cũ là 20)
                if presses > 0:
                    bounce = abs(math.sin(time.time() * 12)) * 35
            else:
                # Bot cũng nhún chậm lại cho thật
                jump_freq = 8 if c["dash"] == 0 else 18  # Cũ là 15/25
                bounce = abs(math.sin(time.time() * jump_freq + c["y"])) * 20

            cy -= bounce

            img = get_image("bao_bo.png", c["scale"], c["scale"])
            if img:
                screen.blit(img, (cx, cy))
            else:
                pygame.draw.circle(screen, BLUE if c["type"] == "PLAYER" else GRAY, (cx + 20, int(cy) + 20), 20)

            if c["type"] == "PLAYER":
                draw_text_outline(screen, "BẠN", 14, cx + 30, cy - 25, GOLD, BLACK)
                pygame.draw.polygon(screen, RED, [(cx + 30, cy - 35), (cx + 25, cy - 45), (cx + 40, cy - 45)])

        fx_manager.update();
        fx_manager.draw(screen)

        # UI
        rank_color = GREEN if current_rank == 1 else (RED if current_rank > 3 else GOLD)
        draw_text_outline(screen, f"HẠNG: {current_rank}/5", 35, 120, 50, rank_color, BLACK)

        pygame.draw.rect(screen, WHITE, (200, 80, 400, 15), border_radius=8)
        pygame.draw.rect(screen, GREEN, (200, 80, 400 * min(1, player_dist / GOAL), 15), border_radius=8)
        pygame.draw.line(screen, RED, (600, 75), (600, 100), 3)

        pygame.display.flip()

    score = 100 if result == "Win" else 10
    time_taken = time.time() - start_time
    spd = player_dist / time_taken if time_taken > 0 else 0
    return {"score": score, "metric1": spd, "metric2": presses, "win": result == "Win"}


# --- GAME 3: HỨNG QUẢ (ĐÃ SỬA: BỎ GIÀY, CHỈ GIỮ NAM CHÂM) ---
def play_hung_qua(screen, player, level=1):
    clock = pygame.time.Clock()
    bg_img = get_image("bg_hung_trai_cay.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)

    # Chỉ giữ lại Nam Châm
    active_magnet = False

    basket_img = get_image("gio_hung.png", 80, 80)
    scale_img = get_image("cai_can.png", 120, 120)

    ITEM_TYPES = {
        "apple": {"s": 1, "img": "tao.png", "c": RED},
        "banana": {"s": 2, "img": "chuoi.png", "c": GOLD},
        "melon": {"s": 5, "img": "dua_hau.png", "c": GREEN},
        "bomb": {"s": -5, "img": "bom.png", "c": BLACK}
    }

    target_score = 15 + (level - 1) * 5;
    current_score = 0;
    duration = 40
    player_rect = pygame.Rect(360, 470, 80, 80)
    falling = [];
    timer = 0;
    start = time.time();
    offset = 0
    fx = EffectManager();
    running = True

    scale_pos_x, scale_pos_y = 120, 480

    while running:
        dt = clock.tick(60)
        screen.blit(bg_img, (0, 0)) if bg_img else screen.fill(BLUE)

        elapsed = time.time() - start - offset
        if duration - elapsed <= 0: running = False

        # Tốc độ cố định (không phụ thuộc giày nữa), tăng nhẹ theo level
        spd = 10 + (level * 0.5)
        radius = 80 if active_magnet else 50

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player_rect.x -= spd
        if keys[pygame.K_RIGHT]: player_rect.x += spd
        player_rect.clamp_ip(screen.get_rect())

        # [CẬP NHẬT] Chỉ vẽ nút Nam Châm (Đưa lên vị trí y=80)
        qty_mag = player.inventory.get("NamCham", 0)
        btn_mag = draw_item_toggle(screen, "nam_cham.png", SCREEN_WIDTH - 90, 80, active_magnet, "N.Châm", qty_mag)

        btn_pause = draw_pause_button_icon(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_pause.collidepoint(event.pos):
                    st = time.time()
                    if run_pause_menu_loop(screen) == "EXIT": return None
                    offset += time.time() - st

                # Chỉ check nút Nam Châm
                elif btn_mag.collidepoint(event.pos):
                    if not active_magnet and player.has_item("NamCham"):
                        player.use_item("NamCham")
                        active_magnet = True
                        play_sound("correct.wav")
                    elif active_magnet:
                        pass
                    else:
                        play_sound("wrong.wav")

        timer += 1
        if timer > 30:
            timer = 0
            t = random.choices(list(ITEM_TYPES.keys()), weights=[45, 30, 10, 15])[0]
            falling.append({"r": pygame.Rect(random.randint(50, 750), -50, 50, 50), "t": t, "s": random.randint(3, 6)})

        for it in falling[:]:
            it["r"].y += it["s"]

            if active_magnet and it["t"] != "bomb":
                dx = player_rect.centerx - it["r"].centerx
                dy = player_rect.centery - it["r"].centery
                if math.hypot(dx, dy) < 200:
                    it["r"].x += int(dx * 0.15);
                    it["r"].y += int(dy * 0.15)

            if math.hypot(player_rect.centerx - it["r"].centerx, player_rect.centery - it["r"].centery) < radius:
                data = ITEM_TYPES[it["t"]]
                current_score = max(0, current_score + data["s"])
                falling.remove(it)
                play_sound("hit.wav" if data["s"] > 0 else "wrong.wav")
                fx.create_text(player_rect.centerx, player_rect.top, f"{data['s']}", data["c"])
            elif it["r"].y > 600:
                falling.remove(it)

        if basket_img:
            screen.blit(basket_img, player_rect)
        else:
            pygame.draw.rect(screen, BLUE, player_rect)

        if active_magnet: pygame.draw.circle(screen, CYAN, player_rect.center, 90, 2)

        for it in falling:
            img = get_image(ITEM_TYPES[it["t"]]["img"], 50, 50)
            screen.blit(img, it["r"]) if img else pygame.draw.rect(screen, ITEM_TYPES[it["t"]]["c"], it["r"])

        if scale_img:
            scale_rect = scale_img.get_rect(center=(scale_pos_x, scale_pos_y))
            screen.blit(scale_img, scale_rect)
        else:
            pygame.draw.circle(screen, WHITE, (scale_pos_x, scale_pos_y), 50, 3)

        draw_text_outline(screen, f"{current_score}/{target_score}", 35, scale_pos_x, scale_pos_y + 70, GOLD, BLACK)
        draw_timer_bar(screen, 50, 10, 700, 30, duration - elapsed, duration)

        fx.update();
        fx.draw(screen)
        pygame.display.flip()

    return {"score": current_score * 10, "metric1": current_score, "metric2": 0, "win": current_score >= target_score}


# --- GAME 4: GHÉP HÌNH (ĐÃ SỬA: HIỆN TRANH SÁNG + THÔNG BÁO RÕ RÀNG) ---
def play_ghep_hinh(screen, player, level=1):
    clock = pygame.time.Clock()
    bg_table = get_image("bg_table.png", SCREEN_WIDTH, SCREEN_HEIGHT)

    img_name = f"puzzle_lv{min(level, 5)}.png"
    orig = get_image(img_name, 450, 450)
    if not orig: orig = pygame.Surface((450, 450)); orig.fill(WHITE)

    rows = cols = 3 + (level - 1) if level < 4 else 6
    pw, ph = 450 // cols, 450 // rows
    sx, sy = 175, 100

    pieces = []
    fixed = []
    for i in range(rows * cols):
        r, c = divmod(i, cols)
        rect = pygame.Rect(c * pw, r * ph, pw, ph)
        sub = orig.subsurface(rect).copy()
        pygame.draw.rect(sub, (200, 200, 200), (0, 0, pw, ph), 1)
        fixed.append((sx + c * pw, sy + r * ph))
        pieces.append({"s": sub, "ok": i, "cur": 0, "r": pygame.Rect(0, 0, pw, ph), "lock": False})

    idx = list(range(rows * cols));
    random.shuffle(idx)
    for i, p in enumerate(pieces):
        p["cur"] = idx[i];
        p["r"].topleft = fixed[idx[i]]
        if p["cur"] == p["ok"]: p["lock"] = True

    dim = pygame.Surface((pw, ph), pygame.SRCALPHA);
    dim.fill((0, 0, 0, 100))
    drag = None;
    ox = oy = 0;
    start = time.time();
    off = 0;
    fx = EffectManager()

    while True:
        clock.tick(60)
        screen.blit(bg_table, (0, 0)) if bg_table else screen.fill(BROWN_BG)
        elapsed = time.time() - start - off
        if 60 + level * 20 - elapsed <= 0: return {"score": 0, "metric1": 0, "metric2": 0, "win": False}

        # Vẽ khung nền tranh
        pygame.draw.rect(screen, (101, 67, 33), (sx - 10, sy - 10, 470, 470), border_radius=10)

        # Nút Đèn
        qty = player.inventory.get("DenDom", 0)
        btn_lamp = draw_item_toggle(screen, "den_dom.png", SCREEN_WIDTH - 90, 80, False, "Gợi Ý", qty)
        btn_pause = draw_pause_button_icon(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_pause.collidepoint(event.pos):
                    t = time.time();
                    if run_pause_menu_loop(screen) == "EXIT": return None
                    off += time.time() - t
                    drag = None

                elif btn_lamp.collidepoint(event.pos):
                    if player.has_item("DenDom"):
                        found_move = False
                        for p in pieces:
                            if not p["lock"]:
                                target = p["ok"]
                                occupier = next((x for x in pieces if x["cur"] == target), None)
                                if occupier:
                                    occupier["cur"] = p["cur"]
                                    occupier["r"].topleft = fixed[occupier["cur"]]
                                p["cur"] = target
                                p["r"].topleft = fixed[target]
                                p["lock"] = True
                                fx.create_explosion(p["r"].centerx, p["r"].centery, GOLD)
                                found_move = True
                                break

                        if found_move:
                            player.use_item("DenDom")
                            play_sound("correct.wav")
                        else:
                            pass
                    else:
                        play_sound("wrong.wav")

                for p in pieces:
                    if not p["lock"] and p["r"].collidepoint(event.pos):
                        drag = p;
                        ox = event.pos[0] - p["r"].x;
                        oy = event.pos[1] - p["r"].y
                        pieces.remove(p);
                        pieces.append(p)
                        break

            if event.type == pygame.MOUSEBUTTONUP and drag:
                mx, my = event.pos;
                found = -1
                for i, pos in enumerate(fixed):
                    if pygame.Rect(pos[0], pos[1], pw, ph).collidepoint(mx, my): found = i; break

                if found != -1:
                    target = next((x for x in pieces if x["cur"] == found and x != drag), None)
                    if target and target["lock"]:
                        drag["r"].topleft = fixed[drag["cur"]]
                    else:
                        old = drag["cur"];
                        drag["cur"] = found;
                        drag["r"].topleft = fixed[found]
                        if target: target["cur"] = old; target["r"].topleft = fixed[old]
                        if drag["cur"] == drag["ok"]: drag["lock"] = True; play_sound("correct.wav")
                        if target and target["cur"] == target["ok"]: target["lock"] = True
                else:
                    drag["r"].topleft = fixed[drag["cur"]]
                drag = None

            if event.type == pygame.MOUSEMOTION and drag:
                drag["r"].x = event.pos[0] - ox;
                drag["r"].y = event.pos[1] - oy

        # Vẽ các mảnh ghép
        to_draw = sorted(pieces, key=lambda x: (x == drag, not x["lock"]))
        for p in to_draw:
            screen.blit(p["s"], p["r"])
            # Chỉ vẽ lớp tối nếu CHƯA hoàn thành game
            if p["lock"]: screen.blit(dim, p["r"])

        # [SỬA LỖI] KIỂM TRA CHIẾN THẮNG
        if all(p["lock"] for p in pieces):
            # 1. Vẽ lại màn hình một lần cuối với trạng thái ĐẸP NHẤT (không bị tối)
            screen.blit(bg_table, (0, 0)) if bg_table else screen.fill(BROWN_BG)
            pygame.draw.rect(screen, (101, 67, 33), (sx - 10, sy - 10, 470, 470), border_radius=10)
            # Vẽ lại toàn bộ mảnh ghép sáng trưng (không phủ dim)
            for p in pieces:
                screen.blit(p["s"], p["r"])

            # 2. Hiện thông báo Chiến Thắng to rõ
            msg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50, 400, 100)
            pygame.draw.rect(screen, RED_LUCKY, msg_rect, border_radius=20)
            pygame.draw.rect(screen, GOLD, msg_rect, 5, border_radius=20)
            draw_text_outline(screen, "HOÀN THÀNH!", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, GOLD, BLACK)

            pygame.display.flip()
            play_sound("win.wav")
            time.sleep(2)  # Dừng 2s để người chơi kịp nhìn

            return {"score": 100 + int(60 + level * 20 - elapsed), "metric1": elapsed, "metric2": 0, "win": True}

        fx.update();
        fx.draw(screen)
        draw_timer_bar(screen, 50, 10, 700, 30, 60 + level * 20 - elapsed, 60 + level * 20)
        pygame.display.flip()

    return {"score": 0, "metric1": 0, "metric2": 0, "win": False}


# --- GAME 5: XÉ VÉ SỐ ---
def play_xe_giay(screen, player):
    clock = pygame.time.Clock()
    is_active = False

    bg_table = get_image("bg_table.png", SCREEN_WIDTH, SCREEN_HEIGHT)

    def init(charm):
        pool = [0] * 5 + [5] * 8 + [10] * 5 + [20] * 4 + [50] * 2 + [200] * 1 if charm else \
            [0] * 12 + [5] * 4 + [10] * 4 + [20] * 3 + [50] * 1 + [200] * 1
        random.shuffle(pool)
        ts = []
        sx = (800 - (5 * 55 + 4 * 8)) // 2
        sy = 130
        for r in range(5):
            for c in range(5):
                ts.append(
                    {"r": pygame.Rect(sx + c * 63, sy + r * 63, 55, 55), "open": False, "v": pool.pop(), "sel": False})
        return ts

    tickets = init(False)
    fx = EffectManager()
    session_won = 0;
    price = 20

    while True:
        clock.tick(60)
        screen.blit(bg_table, (0, 0)) if bg_table else screen.fill((100, 50, 0))
        draw_panel(screen, 100, 10, 600, 580)

        qty = player.inventory.get("BuaMay", 0)
        btn_charm = draw_item_toggle(screen, "bua_may.png", SCREEN_WIDTH - 90, 80, is_active, "Bùa", qty)

        btn_pause = draw_pause_button_icon(screen)

        draw_text_outline(screen, "XÉ VÉ SỐ", 50, 400, 50, GOLD, BLACK)
        draw_text_outline(screen, f"GIÁ: {price} - CÓ: {player.money}", 24, 400, 90, WHITE, BLACK)
        if is_active: draw_text_outline(screen, "BÙA MAY ĐÃ KÍCH HOẠT!", 20, 400, 115, RED, WHITE)

        sel_cnt = sum(1 for t in tickets if t["sel"])
        cost = sel_cnt * price

        btn_open = pygame.Rect(200, 480, 400, 60)
        pygame.draw.rect(screen, (200, 100, 0) if sel_cnt > 0 else (80, 80, 80), btn_open, border_radius=15)
        draw_text_outline(screen, f"MỞ {sel_cnt} VÉ (-{cost})" if sel_cnt > 0 else "CHỌN VÉ", 26, 400, 510, WHITE,
                          BLACK)
        draw_text_outline(screen, f"THẮNG: {session_won}", 28, 400, 560, GOLD, BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_pause.collidepoint(event.pos): return "SHOP"

                if btn_charm.collidepoint(event.pos):
                    # Chỉ dùng bùa nếu bàn mới tinh
                    all_closed = all(not t["open"] for t in tickets)
                    if not is_active and player.has_item("BuaMay") and all_closed:
                        player.use_item("BuaMay")
                        is_active = True
                        tickets = init(True)  # Reset bàn với tỷ lệ xịn
                        play_sound("correct.wav")
                    elif is_active:
                        pass
                    else:
                        play_sound("wrong.wav")

                for t in tickets:
                    if not t["open"] and t["r"].collidepoint(event.pos):
                        play_sound("hit.wav");
                        t["sel"] = not t["sel"]

                if btn_open.collidepoint(event.pos) and sel_cnt > 0:
                    if player.money >= cost:
                        player.money -= cost
                        for t in tickets:
                            if t["sel"]:
                                t["open"] = True;
                                t["sel"] = False
                                fx.create_explosion(t["r"].centerx, t["r"].centery, GOLD)
                                if t["v"] > 0:
                                    player.money += t["v"];
                                    session_won += t["v"]
                                    fx.create_text(t["r"].x, t["r"].y, f"+{t['v']}", GOLD)
                                else:
                                    fx.create_text(t["r"].x, t["r"].y, "0", GRAY)

                        if all(t["open"] for t in tickets):
                            pygame.display.flip();
                            time.sleep(0.5)
                            tickets = init(is_active)
                    else:
                        play_sound("wrong.wav")

        for t in tickets:
            col = (200, 50, 50) if t["sel"] else ((40, 30, 30) if t["open"] else (160, 20, 20))
            pygame.draw.rect(screen, col, t["r"], border_radius=8)
            pygame.draw.rect(screen, (200, 150, 50), t["r"], 2, border_radius=8)
            if t["open"]:
                draw_text_outline(screen, str(t["v"]), 24, t["r"].centerx, t["r"].centery, GOLD if t["v"] > 0 else GRAY,
                                  BLACK)
            elif t["sel"]:
                draw_text_outline(screen, "V", 30, t["r"].centerx, t["r"].centery, GREEN, BLACK)

        fx.update();
        fx.draw(screen)
        pygame.display.flip()
