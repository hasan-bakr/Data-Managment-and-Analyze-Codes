#!/usr/bin/env python3
"""
YOLO label txt dosyalarında hedef sınıf (vars: 4) satırlarını en üste taşır.
- Stable partition (sınıf içi sırayı korur)
- Boş satırları atlar
- İsteğe bağlı .bak yedeği
"""
from pathlib import Path
import argparse
import shutil
from typing import Tuple, Iterable, List

DEFAULT_PATH = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\yarımca_kamyon\Annotation\unlabeled\Umut_ustten_1509\etiket\labels"

def reorder_lines(lines: Iterable[str], target_class: int) -> str:
    tops, rest = [], []
    for orig in lines:
        s = orig.strip()
        if not s:
            continue
        parts = s.split()
        try:
            cls_id = int(parts[0])
        except ValueError:
            rest.append(s)
            continue
        (tops if cls_id == target_class else rest).append(s)
    new_lines = tops + rest
    return "\n".join(new_lines) + ("\n" if new_lines else "")

def process_file(fp: Path, target_class: int, backup: bool) -> Tuple[bool, str]:
    if not fp.is_file() or fp.suffix.lower() != ".txt":
        return False, "skip"
    text = fp.read_text(encoding="utf-8", errors="ignore")
    original_lines = text.splitlines()
    new_text = reorder_lines(original_lines, target_class)
    if backup:
        shutil.copy2(fp, fp.with_suffix(fp.suffix + ".bak"))
    fp.write_text(new_text, encoding="utf-8")
    # Doğru sayım: ilk token tam eşleşmeli
    moved = 0
    for ln in original_lines:
        s = ln.strip()
        if not s:
            continue
        parts = s.split()
        try:
            if int(parts[0]) == target_class:
                moved += 1
        except ValueError:
            pass
    return True, f"{moved} satır üste taşındı"

def iter_targets(path: Path, recursive: bool):
    if path.is_file():
        yield path
    elif path.is_dir():
        pattern = "**/*.txt" if recursive else "*.txt"
        yield from path.glob(pattern)

def main(argv: List[str] = None):
    ap = argparse.ArgumentParser(description="YOLO txt'lerde belirli sınıfı en üste taşı.")
    ap.add_argument("path", nargs="*", help="İşlenecek dosya(lar) veya klasör(ler)")
    ap.add_argument("-r", "--recursive", action="store_true", help="Alt dizinlere in")
    ap.add_argument("--no-backup", action="store_true", help="Yedek (.bak) oluşturma")
    ap.add_argument("--class-id", type=int, default=4, help="Üste taşınacak sınıf id'si (vars: 4)")
    # Jupyter/IPython'ın ek argümanlarını yok say
    args, _ = ap.parse_known_args(argv)

    paths = args.path if args.path else [DEFAULT_PATH]

    total_files = 0
    for p in paths:
        base = Path(p)
        if not base.exists():
            print(f"[WARN] Yol bulunamadı: {base}")
            continue
        for f in iter_targets(base, args.recursive):
            ok, msg = process_file(f, args.class_id, backup=not args.no_backup)
            if ok:
                print(f"[OK] {f}: {msg}")
                total_files += 1

    if total_files == 0:
        print("İşlenecek .txt bulunamadı.")

if __name__ == "__main__":
    main()