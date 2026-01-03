import pygame
import random
import math


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.lifetime = 20
        self.size = random.randint(4, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.size -= 0.2

    def draw(self, screen):
        if self.lifetime > 0 and self.size > 0:
            pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), int(self.size), int(self.size)))


class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 60
        try:
            self.font = pygame.font.SysFont("arial", 28, bold=True)
        except:
            self.font = pygame.font.Font(None, 28)

    def update(self):
        self.y -= 1
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            txt_surf_shadow = self.font.render(self.text, True, (0, 0, 0))
            screen.blit(txt_surf_shadow, (self.x + 2, self.y + 2))
            txt_surf = self.font.render(self.text, True, self.color)
            screen.blit(txt_surf, (self.x, self.y))


# --- HIỆU ỨNG NƯỚC CHẢY (ĐÃ CHỈNH VỊ TRÍ) ---
class WaterRipple:
    def __init__(self, screen_width):
        # Random vị trí trong vùng sông
        # ĐÃ SỬA: Hạ thấp tọa độ Y xuống (350 - 480) để khớp với mặt nước hơn
        self.x = random.randint(0, screen_width)
        self.y = random.randint(350, 480)

        # Kích thước vệt sóng
        self.w = random.randint(20, 50)
        self.h = random.randint(2, 4)

        # Tốc độ trôi
        self.speed = random.uniform(-0.5, 0.5)

        # Độ trong suốt (Alpha)
        self.alpha = 0
        self.fade_in = True
        self.max_alpha = random.randint(50, 150)
        self.alive = True

    def update(self):
        self.x += self.speed

        # Hiệu ứng mờ dần
        if self.fade_in:
            self.alpha += 2
            if self.alpha >= self.max_alpha:
                self.fade_in = False
        else:
            self.alpha -= 2
            if self.alpha <= 0:
                self.alive = False

    def draw(self, screen):
        if self.alive:
            s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            color = (255, 255, 255, self.alpha)
            pygame.draw.ellipse(s, color, (0, 0, self.w, self.h))
            screen.blit(s, (self.x, self.y))


class EffectManager:
    def __init__(self):
        self.particles = []
        self.texts = []
        self.ripples = []

    def create_explosion(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def create_text(self, x, y, content, color=(255, 255, 0)):
        self.texts.append(FloatingText(x, y, content, color))

    def update(self):
        # Update particles & texts
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for p in self.particles: p.update()

        self.texts = [t for t in self.texts if t.lifetime > 0]
        for t in self.texts: t.update()

        # --- UPDATE NƯỚC ---
        # Sinh thêm sóng
        if len(self.ripples) < 30:
            if random.randint(0, 10) < 2:
                self.ripples.append(WaterRipple(800))

        # Update vị trí sóng
        self.ripples = [r for r in self.ripples if r.alive]
        for r in self.ripples: r.update()

    def draw(self, screen):
        # Vẽ sóng nước TRƯỚC
        for r in self.ripples: r.draw(screen)

        for p in self.particles: p.draw(screen)
        for t in self.texts: t.draw(screen)