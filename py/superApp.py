import os
import cv2
import random
import shutil
from colorama import Fore, Style, init
from collections import defaultdict
import argparse
import albumentations as A
import matplotlib.pyplot as plt

# Renkli terminal çıktısı için
init(autoreset=True)


def organize_dataset_by_folder(root_path):
    """
    Alt klasörlerdeki tüm dosyaları kendi klasörlerine taşı.
    Her klasörde labels ve images klasörleri oluşturur.
    """
    for dirpath, dirnames, filenames in os.walk(root_path):
        if not filenames:
            continue

        labels_dir = os.path.join(dirpath, "labels")
        images_dir = os.path.join(dirpath, "images")
        os.makedirs(labels_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)

        for file_name in filenames:
            file_path = os.path.join(dirpath, file_name)
            if os.path.isfile(file_path):
                if file_name.endswith(".txt"):
                    shutil.move(file_path, os.path.join(labels_dir, file_name))
                    print(f"{file_path} -> {labels_dir}")
                elif file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    shutil.move(file_path, os.path.join(images_dir, file_name))
                    print(f"{file_path} -> {images_dir}")


def analyze_dataset(root_dir, delete_missing=False):
    """
    Dataset’i analiz eder. Eksik image veya label varsa listeler.
    Her klasör için stats döndürür: {class_path: {images, labels, missing_images, missing_labels}}
    """
    print(Fore.CYAN + "📂 YOLO Dataset Super Analyzer Başlatıldı...")
    class_stats = dict()
    deleted_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "images" in dirpath.lower():
            parent_dir = os.path.dirname(dirpath)
            class_name = parent_dir  # full path olarak sakla
            labels_dir = os.path.join(parent_dir, "labels")
            os.makedirs(labels_dir, exist_ok=True)

            stats = class_stats.setdefault(class_name, {"images": 0, "labels": 0, "missing_labels": [], "missing_images": []})

            for f in filenames:
                if f.lower().endswith((".jpg", ".jpeg", ".png")):
                    stats["images"] += 1
                    label_path = os.path.join(labels_dir, os.path.splitext(f)[0] + ".txt")
                    if not os.path.exists(label_path):
                        stats["missing_labels"].append(os.path.join(dirpath, f))
                        if delete_missing:
                            os.remove(os.path.join(dirpath, f))
                            deleted_files.append(os.path.join(dirpath, f))
        elif "labels" in dirpath.lower():
            parent_dir = os.path.dirname(dirpath)
            class_name = parent_dir
            images_dir = os.path.join(parent_dir, "images")
            os.makedirs(images_dir, exist_ok=True)

            stats = class_stats.setdefault(class_name, {"images": 0, "labels": 0, "missing_labels": [], "missing_images": []})

            for f in filenames:
                if f.lower().endswith(".txt"):
                    stats["labels"] += 1
                    img_found = False
                    for ext in [".jpg", ".jpeg", ".png"]:
                        img_path = os.path.join(images_dir, os.path.splitext(f)[0] + ext)
                        if os.path.exists(img_path):
                            img_found = True
                            break
                    if not img_found:
                        stats["missing_images"].append(os.path.join(dirpath, f))
                        if delete_missing:
                            os.remove(os.path.join(dirpath, f))
                            deleted_files.append(os.path.join(dirpath, f))

    return class_stats, deleted_files


def augment_images(class_stats, augment_count=2):
    """
    Her klasörde augmentasyon uygular.
    """
    print(Fore.MAGENTA + "🧪 Augmentasyon işlemi başlatılıyor...\n")
    transform = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.3),
        A.Rotate(limit=10, p=0.3),
    ])

    for class_path, stats in class_stats.items():
        img_dir = os.path.join(class_path, "images")
        label_dir = os.path.join(class_path, "labels")

        if not os.path.exists(img_dir) or not os.path.exists(label_dir):
            continue

        img_files = [f for f in os.listdir(img_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not img_files:
            continue

        for img_file in random.sample(img_files, min(len(img_files), augment_count)):
            img_path = os.path.join(img_dir, img_file)
            image = cv2.imread(img_path)
            if image is None:
                continue

            aug = transform(image=image)
            aug_img = aug["image"]
            new_name = os.path.splitext(img_file)[0] + "_aug.jpg"
            cv2.imwrite(os.path.join(img_dir, new_name), aug_img)

            # Label kopyala
            src_label = os.path.join(label_dir, os.path.splitext(img_file)[0] + ".txt")
            dst_label = os.path.join(label_dir, os.path.splitext(new_name)[0] + ".txt")
            if os.path.exists(src_label):
                shutil.copy(src_label, dst_label)

        print(Fore.CYAN + f"✨ {os.path.basename(class_path)} sınıfına augmentasyon uygulandı ({augment_count} adet).")

    print(Fore.GREEN + "\n🎉 Augmentasyon işlemi tamamlandı!\n")


def print_stats(class_stats, deleted_files=None):
    """
    Analiz sonuçlarını terminale yazdırır.
    """
    print(Fore.GREEN + "📊 Analiz Sonuçları:\n")
    for cls, stats in class_stats.items():
        print(Fore.CYAN + f"📁 Klasör: {cls}")
        print(Fore.WHITE + f"  🖼️  Görseller: {stats['images']}")
        print(Fore.WHITE + f"  🏷️  Etiketler: {stats['labels']}")
        if stats["missing_labels"]:
            print(Fore.RED + f"  ⚠️  Eşleşmeyen Görseller ({len(stats['missing_labels'])} adet):")
            for m in stats["missing_labels"]:
                print(Fore.RED + f"     └─ {os.path.basename(m)}")
        if stats["missing_images"]:
            print(Fore.RED + f"  ⚠️  Etiketi Var Ama Görseli Yok ({len(stats['missing_images'])} adet):")
            for m in stats["missing_images"]:
                print(Fore.RED + f"     └─ {os.path.basename(m)}")
        print()

    if deleted_files:
        print(Fore.RED + "🗑️ Silinen dosyalar:")
        for f in deleted_files:
            print(Fore.RED + f"   └─ {f}")
        print(Fore.LIGHTBLACK_EX + f"Toplam {len(deleted_files)} dosya silindi.\n")



def save_graphs(root_dir):
    import matplotlib.pyplot as plt

    folder_counts = {}

    # Dizinleri gez
    for dirpath, dirnames, filenames in os.walk(root_dir):
        img_files = [f for f in filenames if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if img_files:
            folder_name = os.path.relpath(dirpath, root_dir)
            folder_counts[folder_name] = len(img_files)

    if not folder_counts:
        print("⚠️ Hiç image bulunamadı, grafik oluşturulamadı.")
        return

    # Grafik oluştur
    plt.figure(figsize=(12, 6))
    bars = plt.bar(folder_counts.keys(), folder_counts.values(), color="skyblue")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Image Sayısı")
    plt.xlabel("Klasörler")
    plt.title("Her Klasördeki Image Sayısı")

    # Her bar üzerine sayı ekle
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, str(yval), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig("images_count_graph.png")
    plt.close()
    print("✅ Grafik kaydedildi: images_count_graph.png")


def delete_classes_txt(root_dir):
    """
    Tüm alt klasörlerdeki classes.txt dosyalarını siler.
    """
    deleted = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.lower() == "classes.txt":
                path = os.path.join(dirpath, f)
                os.remove(path)
                deleted.append(path)
                print(Fore.RED + f"🗑️  classes.txt silindi: {path}")
    print(Fore.LIGHTBLACK_EX + f"Toplam {len(deleted)} classes.txt dosyası silindi.\n")
    return deleted

def detailed_analysis(root_dir):
    """
    Her klasördeki label dosyalarını açar ve 
    her bir bounding box index'i için kaç adet olduğunu sayar.
    Ayrıca her class ID için 1 örnek label dosyasının ismini gösterir.
    """
    print(Fore.MAGENTA + "🔎 Detaylı Analiz Başlatıldı...\n")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "labels" in dirpath.lower():
            class_name = os.path.basename(os.path.dirname(dirpath))
            index_counts = defaultdict(int)
            sample_files = {}  # class ID -> örnek label dosyası
            total_labels = 0

            for f in filenames:
                if f.lower().endswith(".txt"):
                    total_labels += 1
                    path = os.path.join(dirpath, f)
                    with open(path, "r") as file:
                        for line in file:
                            parts = line.strip().split()
                            if len(parts) > 0:
                                index = parts[0]  # YOLO class ID
                                index_counts[index] += 1
                                # Eğer örnek dosya yoksa kaydet
                                if index not in sample_files:
                                    sample_files[index] = f

            print(Fore.CYAN + f"📁 Klasör: {class_name} ({dirpath})")
            print(Fore.WHITE + f"  Toplam label dosyası: {total_labels}")
            for idx, count in index_counts.items():
                print(Fore.YELLOW + f"  Class ID {idx}: {count} bounding box")
                print(Fore.GREEN + f"    Örnek label dosyası: {sample_files[idx]}")
            print()
    print(Fore.GREEN + "✅ Detaylı analiz tamamlandı!\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLO Dataset Super Analyzer 🚀")
    parser.add_argument("--path", type=str, default=".", help="Analiz edilecek ana klasör yolu")
    parser.add_argument("--augment", action="store_true", help="Augmentasyon işlemi uygula")
    parser.add_argument("--count", type=int, default=2, help="Her klasörde augment edilecek görüntü sayısı")
    parser.add_argument("--delete-missing", action="store_true", help="Eşi olmayan (image veya label) dosyaları sil")
    parser.add_argument("--organize-subfolders", action="store_true", help="Alt klasörleri organize et")
    parser.add_argument("--delete-classestxt", action="store_true", help="classes.txt dosyalarını sil")
    parser.add_argument("--detailed", action="store_true", help="Her label içindeki class ID bazlı detaylı analiz yap")
    parser.add_argument("--save-graph", action="store_true", help="Her klasör için image/label sayısını grafikte kaydet")

    args = parser.parse_args()

    if args.organize_subfolders:
        print(Fore.YELLOW + "📂 Alt klasörler organize ediliyor...")
        organize_dataset_by_folder(args.path)

    stats, deleted = analyze_dataset(args.path, delete_missing=args.delete_missing)
    print_stats(stats, deleted_files=deleted)
    
    if args.save_graph:
        save_graphs(args.path)
    
    if args.augment:
        augment_images(stats, augment_count=args.count)

    if args.delete_classestxt:
        delete_classes_txt(args.path)

    if args.detailed:
        detailed_analysis(args.path)

