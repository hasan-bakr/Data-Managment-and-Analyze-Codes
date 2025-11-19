import os, shutil, cv2, uuid
from glob import glob

base_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\Ev1\DatasetSplitted"
merged_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\Ev1\DatasetMerged"
splits = ["train", "val", "test"]

def make_dirs(path):
    for split in splits:
        os.makedirs(os.path.join(path, split, "images"), exist_ok=True)
        os.makedirs(os.path.join(path, split, "labels"), exist_ok=True)

def convert_to_jpg_and_copy(src_img, dst_img_path):
    ext = os.path.splitext(src_img)[1].lower()
    if ext in [".png", ".jpeg", ".tif", ".tiff", ".bmp"]:
        img = cv2.imread(src_img)
        if img is None:
            return False
        cv2.imwrite(dst_img_path, img)
    else:
        shutil.copy(src_img, dst_img_path)
    return True

def merge_split(split):
    print(f"\n🔄 {split.upper()} verileri birleştiriliyor...")
    split_src = os.path.join(base_dir, split)
    split_dst_img = os.path.join(merged_dir, split, "images")
    split_dst_lbl = os.path.join(merged_dir, split, "labels")

    # sadece en alt "images" klasörlerini bul
    all_image_files = glob(os.path.join(split_src, "**", "images", "*.*"), recursive=True)
    seen = set()
    count, missing_label = 0, 0

    for src_img in all_image_files:
        ext = os.path.splitext(src_img)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]:
            continue

        if src_img in seen:
            continue
        seen.add(src_img)

        # label path
        labels_dir = os.path.join(os.path.dirname(os.path.dirname(src_img)), "labels")
        base = os.path.splitext(os.path.basename(src_img))[0]
        src_lbl = os.path.join(labels_dir, base + ".txt")

        # benzersiz isim oluştur
        rel_prefix = os.path.relpath(os.path.dirname(os.path.dirname(src_img)), split_src).replace(os.sep, "_")
        unique_id = uuid.uuid4().hex[:6]
        new_basename = f"{rel_prefix}_{base}_{unique_id}"

        dst_img_path = os.path.join(split_dst_img, new_basename + ".jpg")
        dst_lbl_path = os.path.join(split_dst_lbl, new_basename + ".txt")

        ok = convert_to_jpg_and_copy(src_img, dst_img_path)
        if not ok:
            continue

        if os.path.exists(src_lbl):
            shutil.copy(src_lbl, dst_lbl_path)
        else:
            missing_label += 1

        count += 1

    print(f"✅ {split}: {count} görsel işlendi ({missing_label} label eksik)")
    print(f"   🔢 Sonuç: {len(os.listdir(split_dst_img))} images, {len(os.listdir(split_dst_lbl))} labels")

make_dirs(merged_dir)
for s in splits:
    merge_split(s)
print("\n🎯 Birleştirme tamamlandı!")
