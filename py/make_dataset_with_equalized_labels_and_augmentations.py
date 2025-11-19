import os
import shutil
import random
from glob import glob
import cv2
import albumentations as A

# --- AYARLAR ---
source_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\Ev1\Dataset"  # Ana klasör
output_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\Ev1\DatasetSplitted"

train_split = 1500
val_split = 250
test_split = 0

# Alt sınıflar
classes = [
    "ev_kapakli_tbkli","ev_kapakli_tbksiz","ev_kapaksiz_tbkli","ev_kapaksiz_tbksiz",
    "ev_sarikapakli_tbkli","ev_sarikapakli_tbksiz",
    "mogaz_sebilkapakli_tbkli","mogaz_sebilkapakli_tbksiz",
    "mogaz_kapaksiz_tbkli","mogaz_kapaksiz_tbksiz",
    "mogaz_sarikapak_tbkli","mogaz_sarikapak_tbksiz",
    "aygaz_kapakli_tbkli","aygaz_kapakli_tbksiz",
    "aygaz_sarikapakli_tbkli","aygaz_sarikapakli_tbksiz",
    "aygaz_kapaksiz_tbkli","aygaz_kapaksiz_tbksiz",
    "maxi_kapakli_tbkli","maxi_kapakli_tbksiz",
    "maxi_kapaksiz_tbkli","maxi_kapaksiz_tbksiz",
    "maxi_sarikapakli_tbkli","maxi_sarikapakli_tbksiz"
]

# --- Albumentations transform ---
transform = A.Compose([
    A.RandomBrightnessContrast(brightness_limit=0.15, contrast_limit=0.15, p=0.5),
    A.GaussNoise(var=(2.0, 8.0), p=0.1),
    A.GaussianBlur(blur_limit=(3, 5), p=0.2),
])

# --- FONKSİYONLAR ---
def make_dirs(path, classes):
    for split in ["train", "val", "test"]:
        for cls in classes:
            os.makedirs(os.path.join(path, split, cls, "images"), exist_ok=True)
            os.makedirs(os.path.join(path, split, cls, "labels"), exist_ok=True)

def ensure_jpg_and_copy_image(src_img, dst_img_path):
    """
    Eğer src_img .png ise okuyup JPG olarak dst_img_path'e kaydeder.
    Eğer zaten JPG ise doğrudan kopyalar.
    dst_img_path full path (with .jpg)
    """
    _, ext = os.path.splitext(src_img)
    ext = ext.lower()
    if ext in [".png", ".jpeg", ".tif", ".tiff", ".bmp"]:
        img = cv2.imread(src_img)
        if img is None:
            print(f"   ⚠️  Görsel okunamadı: {src_img}")
            return False
        # cv2.imwrite ile JPG olarak kaydet
        cv2.imwrite(dst_img_path, img)
        return True
    else:
        # zaten .jpg veya başka; kopyala (ama hedefin .jpg uzantılı olduğundan emin ol)
        try:
            shutil.copy(src_img, dst_img_path)
            return True
        except Exception as e:
            print(f"   ⚠️  Kopyalama hatası: {src_img} -> {dst_img_path} | {e}")
            return False

def copy_image_and_label(src_img, src_label, dst_img_dir, dst_label_dir, new_name):
    """
    src_img: orijinal image path (herhangi uzantı)
    src_label: orijinal label path (.txt)
    dst_img_dir: hedef images klasörü
    dst_label_dir: hedef labels klasörü
    new_name: dosya adı (uzantısız)
    """
    os.makedirs(dst_img_dir, exist_ok=True)
    os.makedirs(dst_label_dir, exist_ok=True)

    dst_img_path = os.path.join(dst_img_dir, new_name + ".jpg")  # her zaman .jpg olarak kaydediyoruz
    ok = ensure_jpg_and_copy_image(src_img, dst_img_path)
    if not ok:
        print(f"   ⚠️  Görsel atlandı: {src_img}")
        return False

    if os.path.exists(src_label):
        try:
            shutil.copy(src_label, os.path.join(dst_label_dir, new_name + ".txt"))
        except Exception as e:
            print(f"   ⚠️  Label kopyalama hatası: {src_label} -> {e}")
            return False
    else:
        print(f"   ⚠️  Etiket bulunamadı: {src_label} (görsel kopyalandı ama etiketsiz)")
        # etiket yoksa yine de devam et (isteğe göre burada False dönebilirsin)
    return True

def augment_and_save(src_img, src_label, dst_img_dir, dst_label_dir, aug_index):
    """
    Augment edilmiş resmi JPG kaydeder ve label'ı kopyalar.
    """
    img = cv2.imread(src_img)
    if img is None:
        print(f"   ⚠️  Augment için okunamadı: {src_img}")
        return False
    augmented = transform(image=img)['image']
    base_name = os.path.splitext(os.path.basename(src_img))[0]
    new_name = f"{base_name}_aug{aug_index}"
    dst_img_path = os.path.join(dst_img_dir, new_name + ".jpg")
    cv2.imwrite(dst_img_path, augmented)
    if os.path.exists(src_label):
        shutil.copy(src_label, os.path.join(dst_label_dir, new_name + ".txt"))
    else:
        print(f"   ⚠️  Augmented için label yok: {src_label}")
    return True

# --- İŞLEM ---
# 1. Dinamik olarak alt klasörleri bul (images/labels yapısını kontrol ederek)
all_classes = []
for root, dirs, files in os.walk(source_dir):
    for d in dirs:
        dir_path = os.path.join(root, d)
        images_folder = os.path.join(dir_path, "images")
        labels_folder = os.path.join(dir_path, "labels")
        if os.path.isdir(images_folder):
            # jpg, JPG, png, jpeg, etc.
            jpgs = glob(os.path.join(images_folder, "*.jpg")) + glob(os.path.join(images_folder, "*.JPG")) \
                   + glob(os.path.join(images_folder, "*.png")) + glob(os.path.join(images_folder, "*.PNG")) \
                   + glob(os.path.join(images_folder, "*.jpeg")) + glob(os.path.join(images_folder, "*.JPEG"))
            if jpgs:
                rel = os.path.relpath(dir_path, source_dir)
                if rel not in all_classes:
                    all_classes.append(rel)

if not all_classes:
    print("⚠️  Hiç sınıf bulunamadı. source_dir ve alt yapıyı kontrol et.")
else:
    print(f"🔎 Toplam sınıf bulundu: {len(all_classes)}")

make_dirs(output_dir, all_classes)

# 2. Her alt klasör için işlemleri uygula
for cls_rel_path in all_classes:
    cls_full_path = os.path.join(source_dir, cls_rel_path)
    images_folder = os.path.join(cls_full_path, "images")
    labels_folder = os.path.join(cls_full_path, "labels")

    # tüm görüntüleri al (jpg, png, jpeg, büyük/küçük)
    raw_images = []
    raw_images += glob(os.path.join(images_folder, "*.jpg"))
    raw_images += glob(os.path.join(images_folder, "*.JPG"))
    raw_images += glob(os.path.join(images_folder, "*.png"))
    raw_images += glob(os.path.join(images_folder, "*.PNG"))
    raw_images += glob(os.path.join(images_folder, "*.jpeg"))
    raw_images += glob(os.path.join(images_folder, "*.JPEG"))

    # normalize et ve sırayı koruyarak duplicateları kaldır
    # Windows'ta path'ler case-insensitive olabilir, bu yüzden lower() ile normalize edip dict.fromkeys ile dedupe yapıyoruz
    seen = {}
    images = []
    for p in raw_images:
        key = os.path.normpath(p).lower()   # normalize & lower ile güvenli karşılaştırma
        if key not in seen:
            seen[key] = True
            images.append(p)

    images = sorted(images)  # istersen alfabetik sıraya sok (opsiyonel)

    # debug: ilk birkaç dosyayı göster
    print(f"\n📁 İşlenen Sınıf: {cls_rel_path}")
    print(f"   Toplam Görseller (images/ içinde): {len(images)}")
    for p in images[:6]:
        lblp = os.path.join(labels_folder, os.path.basename(p).rsplit(".", 1)[0] + ".txt")
        print(f"     - {os.path.basename(p)}  label: {'OK' if os.path.exists(lblp) else 'MISSING'}")

    # oluşturulan label path'leri (labels klasöründen)
    labels = [os.path.join(labels_folder, os.path.basename(img).rsplit(".", 1)[0] + ".txt") for img in images]

    combined = list(zip(images, labels))
    random.shuffle(combined)
    images, labels = zip(*combined) if combined else ([], [])

    # Val ve Test
    val_images = images[:val_split]
    val_labels = labels[:val_split]

    test_images = images[val_split:val_split+test_split]
    test_labels = labels[val_split:val_split+test_split]

    train_images = images[val_split+test_split:]
    train_labels = labels[val_split+test_split:]

    print(f"   Val: {len(val_images)}  Test: {len(test_images)}  Orijinal Train: {len(train_images)}")

    # Kopyala (val/test/train) - eksik label'larda uyar, atla
    for img, lbl in zip(val_images, val_labels):
        ok = copy_image_and_label(img, lbl,
                             os.path.join(output_dir, "val", cls_rel_path, "images"),
                             os.path.join(output_dir, "val", cls_rel_path, "labels"),
                             os.path.splitext(os.path.basename(img))[0])
        if not ok:
            print(f"   ⚠️  Val kopyalama atlandı: {img}")

    for img, lbl in zip(test_images, test_labels):
        ok = copy_image_and_label(img, lbl,
                             os.path.join(output_dir, "test", cls_rel_path, "images"),
                             os.path.join(output_dir, "test", cls_rel_path, "labels"),
                             os.path.splitext(os.path.basename(img))[0])
        if not ok:
            print(f"   ⚠️  Test kopyalama atlandı: {img}")

    for img, lbl in zip(train_images, train_labels):
        ok = copy_image_and_label(img, lbl,
                             os.path.join(output_dir, "train", cls_rel_path, "images"),
                             os.path.join(output_dir, "train", cls_rel_path, "labels"),
                             os.path.splitext(os.path.basename(img))[0])
        if not ok:
            print(f"   ⚠️  Train kopyalama atlandı: {img}")

    # --- Eksikse augmentasyon ---
    train_count = len(os.listdir(os.path.join(output_dir, "train", cls_rel_path, "images")))
    aug_index = 0

    # güvenlik: eğer orijinal train_images hiç yoksa augmentasyon yapmayı atla
    if len(train_images) == 0:
        print(f"   ⚠️  Uyarı: {cls_rel_path} için hiç orijinal train görüntüsü yok — augmentasyon atlandı.")
    else:
        # Augment için döngü (mevcut train görsellerinin üzerinden döner)
        # güvenlik: tek döngüde en fazla X augment olsun (ör: sınıf başına 5000), böylece takılmaz
        max_aug_iterations = 5000
        while train_count < train_split and aug_index < max_aug_iterations:
            for img, lbl in zip(train_images, train_labels):
                success = augment_and_save(img, lbl,
                                 os.path.join(output_dir, "train", cls_rel_path, "images"),
                                 os.path.join(output_dir, "train", cls_rel_path, "labels"),
                                 aug_index)
                if success:
                    aug_index += 1
                    train_count += 1
                if train_count >= train_split or aug_index >= max_aug_iterations:
                    break

    if aug_index > 0:
        print(f"   🔄 Augmentasyon ile {aug_index} görsel eklendi (hedef: {train_split})")
    else:
        print(f"   ✅ Augmentasyon uygulanmadı (yeterli orijinal varsa)")

print("\n✅ Dataset başarıyla organize edildi ve augmentasyon uygulandı!")
