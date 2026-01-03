import json
import os

DATA_DIR = 'data'
PROFILE_FILE = os.path.join(DATA_DIR, 'profiles.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


class ProfileManager:
    def __init__(self):
        self.profiles = self.load_profiles()

    def load_profiles(self):
        if not os.path.exists(PROFILE_FILE):
            return []
        try:
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # [MỚI] Kiểm tra xem dữ liệu cũ (chỉ là list string) có tồn tại không để convert
                new_data = []
                for p in data:
                    if isinstance(p, str):  # Dữ liệu cũ
                        new_data.append({"name": p, "gender": "BOY"})  # Mặc định là Nam
                    else:
                        new_data.append(p)
                return new_data
        except:
            return []

    def save_profiles(self):
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=4)

    # [MỚI] Thêm tham số gender
    def add_profile(self, name, gender="BOY"):
        name = name.strip()
        if not name: return False
        # Kiểm tra trùng tên
        for p in self.profiles:
            if p["name"] == name: return False

        self.profiles.append({"name": name, "gender": gender})
        self.save_profiles()
        return True

    def delete_profile(self, name):
        for i, p in enumerate(self.profiles):
            if p["name"] == name:
                del self.profiles[i]
                self.save_profiles()
                return True
        return False

    def rename_profile(self, old_name, new_name):
        new_name = new_name.strip()
        # Kiểm tra trùng tên mới
        for p in self.profiles:
            if p["name"] == new_name: return False

        for p in self.profiles:
            if p["name"] == old_name:
                p["name"] = new_name
                self.save_profiles()
                return True
        return False

    def get_gender(self, name):
        for p in self.profiles:
            if p["name"] == name: return p.get("gender", "BOY")
        return "BOY"