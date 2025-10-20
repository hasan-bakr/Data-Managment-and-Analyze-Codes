import glob
import os
import shutil
import unicodedata

# Türkçe karakterleri normalleştiren bir fonksiyon
def normalize_path(path):
    return unicodedata.normalize('NFKD', path).encode('ascii', 'ignore').decode('utf-8')

# Etiket dosyalarının yollarını al
label_paths = glob.glob(r"C:\Users\524ha\Desktop\sanayi\ayrilmis_data_sanayi_tup\sari_TBKLI\*.txt")
label_paths.remove(r"C:\Users\524ha\Desktop\sanayi\ayrilmis_data_sanayi_tup\sari_TBKLI\classes.txt")
for label in label_paths:
    new_rows = []
    with open(label, "r", encoding="utf-8") as file:
        data = file.read()
        rows = data.splitlines()

    for row in rows:
        row = row.strip()  # Remove leading/trailing whitespace
        if not row:
            continue

        elements = row.split(" ")
        if not elements[0]:
            continue

        print(f"Processing row: {repr(row)}")  # Debug: Print the row with hidden characters
        try:
            category = int(elements[0])
        except ValueError:
            print(f"Skipping row with invalid category: {row}")
            continue
        

        elements[0] = "6"
        

        new_rows.append(" ".join(elements))
    file.close()
    # Dosyayı güncelle ve yaz
    with open(label, "w", encoding="utf-8") as file:
        file.write("\n".join(new_rows))
    
    print(f"Updated content in: {label}")  # Debug: Confirm file is updated