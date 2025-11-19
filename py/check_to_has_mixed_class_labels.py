import os

labels_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\Mini\Oncekiler\labels"

# Farklı sınıfları içeren dosyaları saklamak için liste
multi_class_files = []

for label_file in os.listdir(labels_dir):
    if not label_file.endswith(".txt"):
        continue

    label_path = os.path.join(labels_dir, label_file)
    with open(label_path, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # Satırlardan sınıf ID'lerini al
    class_ids = set(line.split()[0] for line in lines)

    # Birden fazla sınıf varsa listeye ekle
    if len(class_ids) > 1:
        multi_class_files.append(label_file)

# Sonuçları yazdır
print("📄 Birden fazla sınıf içeren dosyalar:")
for f in multi_class_files:
    print(f)
