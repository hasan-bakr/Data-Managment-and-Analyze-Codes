import os
import shutil

# Ana klasör
base_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\Mini\Mini_1"

# 🔧 Kaynak klasörleri belirt
images_dir = os.path.join(base_dir, "images")
labels_dir = os.path.join(base_dir, "labels")

# 🔧 Çıktı klasörü
output_dir = os.path.join(base_dir, "sorted_by_class")
os.makedirs(output_dir, exist_ok=True)

# 🔁 Tüm label dosyalarını dolaş
for label_file in os.listdir(labels_dir):
    if not label_file.endswith(".txt"):
        continue

    label_path = os.path.join(labels_dir, label_file)
    image_name = os.path.splitext(label_file)[0] + ".jpg"
    image_path = os.path.join(images_dir, image_name)

    if not os.path.exists(image_path):
        print(f"⚠️ Görsel bulunamadı, atlanıyor: {image_name}")
        continue

    # 🧠 Etiket dosyasındaki sınıf ID'lerini al
    with open(label_path, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    if not lines:
        continue

    class_ids = set(line.split()[0] for line in lines)

    # 🗂️ Her sınıf için ilgili klasörleri oluşturup dosyaları kopyala
    for class_id in class_ids:
        class_image_dir = os.path.join(output_dir, f"class_{class_id}", "images")
        class_label_dir = os.path.join(output_dir, f"class_{class_id}", "labels")
        os.makedirs(class_image_dir, exist_ok=True)
        os.makedirs(class_label_dir, exist_ok=True)

        shutil.copy2(image_path, os.path.join(class_image_dir, image_name))
        shutil.copy2(label_path, os.path.join(class_label_dir, label_file))

print("✅ Sınıflara göre ayırma işlemi tamamlandı!")
