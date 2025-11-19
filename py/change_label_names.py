import os

# === Ayarlar ===
labels_folder = r"LABEL_PATH"  # labels klasörünün yolu
new_class_index = 19  # Tüm label dosyalarındaki class index bu olacak

# === İşlem ===
for filename in os.listdir(labels_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(labels_folder, filename)
        
        with open(file_path, "r") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 5:  # YOLO formatı: class_id x_center y_center width height
                parts[0] = str(new_class_index)
                new_lines.append(" ".join(parts))
            else:
                # Boş veya yanlış satırlar varsa onları atlıyoruz
                continue

        with open(file_path, "w") as f:
            f.write("\n".join(new_lines))
        
        print(f"✅ {filename} güncellendi.")

print("\n🎉 Tüm .txt dosyalarındaki class index başarıyla değiştirildi!")
