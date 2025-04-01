import glob
import os
import shutil
import unicodedata

# Türkçe karakterleri normalleştiren bir fonksiyon
def normalize_path(path):
    return unicodedata.normalize('NFKD', path).encode('ascii', 'ignore').decode('utf-8')

# Etiket dosyalarının yollarını al
label_paths = glob.glob(r"C:\Users\524ha\Desktop\AYGAZ_DATAS\datasets\*txt")

# Tüm etiket dosyalarını işle
for label in label_paths:
    label = normalize_path(label)  # Türkçe karakterleri normalize et
    rows = []

    try:
        # Etiket dosyasını oku
        with open(label, "r", encoding="utf-8") as file:
            data = file.read()
            rows = data.split("\n")

        # Her bir satırı işle
        for row in rows:
            if row.strip():  # Boş satırları atla
                elements = row.split(" ")
                category = int(elements[0])  # Kategori bilgisi al
                base_name = os.path.splitext(label)[0]  # Dosya adı (uzantısız)

                # Hedef yol ve klasör belirleme
                if category == 0:
                    destination_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\EV2_DATA\Aygaz_tbkli"
                elif category == 1:
                    destination_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\EV2_DATA\Aygaz_tbksiz"
                elif category == 2:
                    destination_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\EV2_DATA\Mogaz_tbkli"
                elif category == 3:
                    destination_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\EV2_DATA\Mogaz_tbksiz"
                elif category == 4:
                    destination_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\EV2_DATA\Kapaksiz_tbkli"
                elif category == 5:
                    destination_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\EV2_DATA\Kapaksiz_tbksiz"
                elif category == 6:
                    destination_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\EV2_DATA\SariKapak_tbkli"
                elif category == 7:
                    destination_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\EV2_DATA\SariKapak_tbksiz"
                elif category == 8:
                    destination_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\EV2_DATA\MaksiYesil_tbkli"
                elif category == 9:
                    destination_dir = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\EV2_DATA\MaksiYesil_tbksiz"

                # Hedef klasörü oluştur
                os.makedirs(destination_dir, exist_ok=True)

                # Dosyaları taşı
                image_path = base_name + ".jpg"
                destination_label = os.path.join(destination_dir, os.path.basename(label))
                destination_image = os.path.join(destination_dir, os.path.basename(image_path))

                if os.path.exists(image_path):  # Resim dosyası mevcutsa taşı
                    shutil.move(image_path, destination_image)
                else:
                    print(f"Resim dosyası bulunamadı: {image_path}")

                shutil.move(label, destination_label)

    except Exception as e:
        print(f"Hata oluştu: {label} -> {e}")
