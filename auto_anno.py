import cv2
import os
from ultralytics import YOLO
 
# Model tanımlaması
model = YOLO(r"./ev2best.pt")  # Model yolu
classes_to_count = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # Etiketlenecek sınıf ID'leri
 
def process_frames_from_folder(frame_folder, destination_folder):
    """Belirtilen klasördeki frameleri işler ve çıktı dosyalarını kaydeder."""
    os.makedirs(destination_folder, exist_ok=True)
 
    # Klasördeki tüm görüntü dosyalarını al
    image_files = [f for f in os.listdir(frame_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
 
    for image_file in image_files:
        image_path = os.path.join(frame_folder, image_file)
        frame_name = os.path.splitext(image_file)[0]
        txt_path = os.path.join(destination_folder, f"{frame_name}.txt")
        output_image_path = os.path.join(destination_folder, image_file)
 
        # Görüntüyü yükle
        im0 = cv2.imread(image_path)
        if im0 is None:
            print(f"{image_path} yüklenemedi, atlanıyor.")
            continue
 
        # Tahmin yap
        results = model.predict(im0, classes=classes_to_count)
 
        # Tahmin sonuçlarını txt dosyasına yaz
        with open(txt_path, 'w') as txt_file:
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)  # Nesne koordinatları
                    class_id = int(box.cls)
 
                    # YOLO formatına dönüştür
                    width = x2 - x1
                    height = y2 - y1
                    center_x = x1 + width / 2
                    center_y = y1 + height / 2
                    img_height, img_width, _ = im0.shape
 
                    yolo_format = f"{class_id} {center_x / img_width:.6f} {center_y / img_height:.6f} {width / img_width:.6f} {height / img_height:.6f}\n"
                    txt_file.write(yolo_format)
 
        # Etiketlenmiş çerçeveyi kaydet
        cv2.imwrite(output_image_path, im0)
 
    print("Tüm frameler etiketlendi ve çıktı dosyaları kaydedildi.")
 
def process_video(video_path, destination_folder):
    """Belirtilen video dosyasını işler ve çıktı dosyalarını kaydeder."""
    os.makedirs(destination_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), f"Video dosyası açılamadı: {video_path}"
 
    frame_count = 0
    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            print("Video işleme tamamlandı.")
            break
 
        frame_count += 1
        frame_name = f"frame_{frame_count}"
        txt_path = os.path.join(destination_folder, f"{frame_name}.txt")
        output_image_path = os.path.join(destination_folder, f"{frame_name}.jpg")
 
        # Tahmin yap
        results = model.predict(im0, verbose = False, classes=classes_to_count)
 
        # Tahmin sonuçlarını txt dosyasına yaz
        with open(txt_path, 'w') as txt_file:
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)  # Nesne koordinatları
                    class_id = int(box.cls)
 
                    # YOLO formatına dönüştür
                    width = x2 - x1
                    height = y2 - y1
                    center_x = x1 + width / 2
                    center_y = y1 + height / 2
                    img_height, img_width, _ = im0.shape
 
                    yolo_format = f"{class_id} {center_x / img_width:.6f} {center_y / img_height:.6f} {width / img_width:.6f} {height / img_height:.6f}\n"
                    txt_file.write(yolo_format)
 
        # Etiketlenmiş çerçeveyi kaydet
        cv2.imwrite(output_image_path, im0)
 
    cap.release()
    print("Video etiketleme tamamlandı ve çıktı dosyaları kaydedildi.")
 
# Örnek kullanım:
#process_frames_from_folder(r"", r"")
process_video("mogaz.mp4", r"C:\Users\524ha\Desktop\data_managment\Mogaz")