import os
import cv2
import glob
from ultralytics import YOLO
from sahi import AutoDetectionModel
from sahi.predict import get_prediction

# YOLO modelini SAHI için yükleme
model_path = "pt/yandan.pt"
detection_model = AutoDetectionModel.from_pretrained(
    model_type="ultralytics",
    model_path=model_path,
    confidence_threshold=0.6,
    device="cuda",  # 'cuda:0' kullanabilirsin
)

def yolo_format(x_center, y_center, width, height, img_width, img_height):
    """ Normalize koordinatları YOLO formatına dönüştür """
    return f"{x_center / img_width} {y_center / img_height} {width / img_width} {height / img_height}"

def detect_and_label(image_path, output_dir):
    """ Resmi işler, nesneleri tespit eder ve YOLO formatında kaydeder """
    img = cv2.imread(image_path)
    height, width, _ = img.shape
    
    # SAHI ile tahmin al
    results = get_prediction(image_path, detection_model)
    
    labels_path = os.path.join(output_dir, os.path.basename(image_path).replace(".jpg", ".txt"))
    
    with open(labels_path, "w") as f:
        for obj in results.object_prediction_list:  # Doğrudan sonuçları kullan
            x1, y1, x2, y2 = obj.bbox.to_xyxy()  # SAHI bbox erişimi
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            w = x2 - x1
            h = y2 - y1
            class_id = obj.category.id  # SAHI sınıf ID'si
            
            f.write(f"{class_id} {yolo_format(x_center, y_center, w, h, width, height)}\n")
    
    print(f"Etiket kaydedildi: {labels_path}")

def process_images(image_dir, output_dir):
    """ Dizindeki tüm resimleri YOLO formatında etiketle """
    os.makedirs(output_dir, exist_ok=True)
    images = glob.glob(os.path.join(image_dir, "*.jpg"))
    
    for image_path in images:
        detect_and_label(image_path, output_dir)
    
    print("Tüm resimler işlendi!")

# Kullanım
dataset_path = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\yarımca_kamyon\Annotation\images"  # Resimlerin olduğu klasör
output_labels = r"C:\Users\524ha\Desktop\AYGAZ_DATAS\Datasets\yarımca_kamyon\Annotation\images\labels"  # Etiketlerin kaydedileceği klasör

process_images(dataset_path, output_labels)
