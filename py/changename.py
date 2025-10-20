#!/usr/bin/env python
"""
rename_yolo_pairs.py
Görüntü–etiket çiftlerini (YOLO) birlikte ve güvenli biçimde yeniden adlandırır.
"""

from pathlib import Path
import argparse
import shutil
import sys

VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

def collect_pairs(images_dir: Path, labels_dir: Path):
    """İki klasörü tarar, her görüntü-etiket çifti için (img_path, label_path) döndürür."""
    for img_path in sorted(p for p in images_dir.iterdir() if p.suffix.lower() in VALID_EXTS):
        label_path = labels_dir / (img_path.stem + ".txt")
        if label_path.exists():
            yield img_path, label_path
        else:
            print(f"[Uyarı] Etiket yok → {img_path.relative_to(images_dir)}", file=sys.stderr)

def rename_yolo_pairs(images_dir, labels_dir,
                      prefix="", suffix="",
                      zfill=4, start_idx=1, dry_run=False):
    images_dir = Path(images_dir)
    labels_dir = Path(labels_dir)

    if not images_dir.is_dir() or not labels_dir.is_dir():
        raise NotADirectoryError("images_dir ve/veya labels_dir bulunamadı!")

    pairs = list(collect_pairs(images_dir, labels_dir))
    if not pairs:
        raise RuntimeError("Eşleşen görüntü-etiket çifti bulunamadı.")

    for idx, (img_path, label_path) in enumerate(pairs, start=start_idx):
        num = str(idx).zfill(zfill)
        new_base = f"{prefix}{num}{suffix}"
        img_new = img_path.with_name(new_base + img_path.suffix)
        label_new = label_path.with_name(new_base + ".txt")

        # Çakışma kontrolü
        if img_new.exists() or label_new.exists():
            raise FileExistsError(f"Dosya zaten var: {img_new} | {label_new}")

        print(f"{img_path.name}  →  {img_new.name}")
        print(f"{label_path.name} →  {label_new.name}")

        if not dry_run:
            shutil.move(img_path, img_new)
            shutil.move(label_path, label_new)

    print("✅  Tamamlandı." + (" (dry-run)" if dry_run else ""))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="YOLO görüntü-etiket çiftlerini birlikte yeniden adlandır."
    )
    parser.add_argument("--images_dir", required=True, help="images/ klasörü")
    parser.add_argument("--labels_dir", required=True, help="labels/ klasörü")
    parser.add_argument("--prefix", default="", help="Dosya adına önek")
    parser.add_argument("--suffix", default="", help="Dosya adına sonek")
    parser.add_argument("--zfill", type=int, default=4,
                        help="Numaradaki hane sayısı (vars: 4 → 0001)")
    parser.add_argument("--start_idx", type=int, default=1,
                        help="Numaralandırmaya kaçtan başlanacak?")
    parser.add_argument("--dry_run", action="store_true",
                        help="Önce deneme: sadece ne olacağını yaz, dosya taşıma!")
    args = parser.parse_args()

    rename_yolo_pairs(**vars(args))
