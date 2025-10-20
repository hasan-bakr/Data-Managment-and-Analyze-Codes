import os
import shutil
import random
import math
def split_yolo_data(source_dir, dest_dir, train_ratio=0.9, valid_ratio=0.1, test_ratio=0.00):
    assert round(train_ratio + valid_ratio + test_ratio) == 1, "Oranların toplamı 1 olmalıdır."
    
    image_dir = os.path.join(source_dir, "images")
    label_dir = os.path.join(source_dir, "labels")
    
    assert os.path.exists(image_dir) and os.path.exists(label_dir), "Gerekli dizinler mevcut değil."
    
    images = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    random.shuffle(images)
    
    train_split = int(len(images) * train_ratio)
    valid_split = int(len(images) * (train_ratio + valid_ratio))
    
    sets = {
        "train": images[:train_split],
        "valid": images[train_split:valid_split],
        "test": images[valid_split:]
    }
    
    for subset, files in sets.items():
        img_dest = os.path.join(dest_dir, subset, "images")
        lbl_dest = os.path.join(dest_dir, subset, "labels")
        os.makedirs(img_dest, exist_ok=True)
        os.makedirs(lbl_dest, exist_ok=True)
        
        for img_file in files:
            lbl_file = os.path.splitext(img_file)[0] + ".txt"
            
            shutil.copy(os.path.join(image_dir, img_file), os.path.join(img_dest, img_file))
            if os.path.exists(os.path.join(label_dir, lbl_file)):
                shutil.copy(os.path.join(label_dir, lbl_file), os.path.join(lbl_dest, lbl_file))
    
    print("Veri başarıyla ayrıldı!")

# Kullanım
source_directory = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\dataset\train" # YOLO datasetinin bulunduğu dizin
output_directory = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\dataset\dataset"  # Train/Valid/Test dizinlerinin oluşturulacağı yer
split_yolo_data(source_directory, output_directory)
