import os
from collections import defaultdict

def load_class_names(classes_path):
    """
    Opsiyonel 'classes.txt' dosyasından sınıf isimlerini yükler.
    Dosya formatı: her satırda bir sınıf ismi (person, car, vb.)
    """
    class_names = []
    if classes_path and os.path.exists(classes_path):
        try:
            with open(classes_path, 'r', encoding='utf-8') as f:
                class_names = [line.strip() for line in f if line.strip()]
            print(f"Sınıf isimleri '{classes_path}' dosyasından başarıyla yüklendi.")
        except Exception as e:
            print(f"Uyarı: '{classes_path}' dosyası okunamadı. Sadece ID'ler gösterilecek. Hata: {e}")
    else:
        print("Sınıf isim dosyası ('classes.txt') sağlanmadı veya bulunamadı.")
        print("Analizde sadece sınıf ID'leri (0, 1, 2...) gösterilecek.")
    return class_names

def analyze_yolo_labels(labels_dir, classes_path=None):
    """
    Bir YOLO etiket klasörünü tarar ve her sınıftaki etiket sayısını sayar.
    """
    
    # Sınıf isimlerini yüklemeyi dene
    class_names = load_class_names(classes_path)
    
    # Sayımları saklamak için defaultdict kullanmak işleri kolaylaştırır
    class_counts = defaultdict(int)
    total_labels = 0
    processed_files = 0

    print(f"\n'{labels_dir}' klasörü taranıyor...")

    if not os.path.isdir(labels_dir):
        print(f"Hata: '{labels_dir}' klasörü bulunamadı. Lütfen yolu kontrol edin.")
        return

    # Klasördeki tüm dosyaları dolaş
    for filename in os.listdir(labels_dir):
        # Sadece .txt uzantılı etiket dosyalarını işle
        if filename.endswith(".txt"):
            file_path = os.path.join(labels_dir, filename)
            processed_files += 1
            
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:  # Boş satırları atla
                            parts = line.split()
                            if parts:
                                try:
                                    # YOLO formatı: <class_id> <x_center> ...
                                    class_id = int(parts[0])
                                    class_counts[class_id] += 1
                                    total_labels += 1
                                except ValueError:
                                    print(f"Uyarı: {filename} dosyasında geçersiz satır (ID sayı değil): {line}")
            except Exception as e:
                print(f"Hata: {filename} dosyası okunurken bir sorun oluştu. {e}")

    print(f"Tarama tamamlandı. {processed_files} adet etiket (.txt) dosyası işlendi.")
    print("\n--- ETİKET ANALİZ RAPORU ---")

    if total_labels == 0:
        print("Hiç etiket bulunamadı.")
        return

    # Sonuçları sınıf ID'sine göre sıralayarak yazdır
    sorted_class_ids = sorted(class_counts.keys())
    
    # Düzgün hizalama için en uzun başlık uzunluğunu bul
    max_header_len = len("SINIF (ID)")
    for class_id in sorted_class_ids:
        display_name = f"Sınıf {class_id}"
        if class_names and class_id < len(class_names):
            display_name = f"{class_names[class_id]} ({class_id})"
        max_header_len = max(max_header_len, len(display_name))

    # Başlıkları yazdır
    print(f"{'SINIF (ID)':<{max_header_len}} | {'SAYI':>10} | {'YÜZDE (%)':>10}")
    print(f"{'-' * max_header_len:<{max_header_len}} | {'-' * 10:>10} | {'-' * 10:>10}")

    # Her sınıf için sayım ve yüzdeleri yazdır
    for class_id in sorted_class_ids:
        count = class_counts[class_id]
        percentage = (count / total_labels) * 100
        
        # Sınıf ismini (varsa) veya sadece ID'yi al
        display_name = f"Sınıf {class_id}"
        if class_names and class_id < len(class_names):
            display_name = f"{class_names[class_id]} ({class_id})"
            
        print(f"{display_name:<{max_header_len}} | {count:>10} | {percentage:>10.2f}%")

    # Toplamı yazdır
    print(f"{'-' * max_header_len:<{max_header_len}} | {'-' * 10:>10} | {'-' * 10:>10}")
    print(f"{'TOPLAM':<{max_header_len}} | {total_labels:>10} | {100.0:>10.2f}%")

# --- BURADAN AYARLAYIN ---

# 1. Etiketlerinizin bulunduğu klasörün yolu
# Örnek: 'dataset/train/labels' veya 'C:/kullanicilar/proje/labels'
LABELS_KLASORU = r'C:\Users\524ha\Desktop\Resources\data_managment\notebooks\2010\unlabeled_1\labels'  # <<< LÜTFEN BURAYI KENDİ 'labels' KLASÖR YOLUNUZLA DEĞİŞTİRİN

# 2. (OPSİYONEL) Sınıf isimlerinin bulunduğu .txt dosyasının yolu
# Eğer böyle bir dosyanız yoksa veya sadece ID'leri görmek istiyorsanız 'None' yapın.
# Genellikle 'labels' klasörünün bir üst dizininde 'classes.txt' olarak bulunur.
# Örnek: 'dataset/classes.txt'
CLASSES_DOSYASI = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\dataset\train\labels\classes.txt"  # <<< (Opsiyonel) BURAYI DEĞİŞTİRİN veya None yapın

# --- KODU ÇALIŞTIR ---
if __name__ == "__main__":
    analyze_yolo_labels(LABELS_KLASORU, CLASSES_DOSYASI)