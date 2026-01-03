import wave
import math
import struct
import os
import random

# --- CẤU HÌNH ---
SAMPLE_RATE = 44100
VOLUME = 16000 # Âm lượng vừa phải
FOLDER = "assets/sounds"

if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)
    print(f"✅ Đã tạo thư mục: {FOLDER}")

def save_wav(name, samples):
    path = os.path.join(FOLDER, name)
    with wave.open(path, 'w') as f:
        f.setnchannels(1) # Mono
        f.setsampwidth(2) # 16-bit
        f.setframerate(SAMPLE_RATE)
        for s in samples:
            f.writeframes(struct.pack('<h', int(s)))
    print(f"-> Đã tạo: {name}")

# --- CÁC HÀM TẠO SÓNG ÂM ---
def make_beep(freq, duration):
    n = int(SAMPLE_RATE * duration)
    return [math.sin(2 * math.pi * freq * t / SAMPLE_RATE) * VOLUME for t in range(n)]

def make_jump():
    # Tiếng nhảy (Boing) - Tần số tăng dần
    n = int(SAMPLE_RATE * 0.2)
    return [math.sin(2 * math.pi * (200 + t/n*400) * t / SAMPLE_RATE) * VOLUME for t in range(n)]

def make_noise(duration):
    n = int(SAMPLE_RATE * duration)
    return [random.uniform(-VOLUME, VOLUME) for _ in range(n)]

def make_win():
    # Nhạc thắng (Do-Mi-Sol-Do)
    res = []
    for note in [523, 659, 784, 1046]:
        res.extend(make_beep(note, 0.1))
    return res

def make_correct():
    # Tiếng chọn đúng (Ting ting)
    return make_beep(1200, 0.1) + make_beep(1800, 0.15)

# --- CHẠY TẠO FILE ---
if __name__ == "__main__":
    print("⏳ Đang tạo âm thanh...")
    save_wav("hit.wav", make_beep(880, 0.05))       # Tiếng click
    save_wav("correct.wav", make_correct())         # Tiếng đúng/mua đồ
    save_wav("wrong.wav", make_beep(150, 0.3))      # Tiếng sai/thua (trầm)
    save_wav("jump.wav", make_jump())               # Tiếng nhảy
    save_wav("win.wav", make_win())                 # Tiếng thắng
    save_wav("tick.wav", make_noise(0.05))          # Tiếng đếm ngược
    print("🎉 HOÀN TẤT! Đã có đủ âm thanh trong assets/sounds/")