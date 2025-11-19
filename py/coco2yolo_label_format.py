import json
import os
from tqdm import tqdm # İlerleme çubuğu için (isteğe bağlı, pip install tqdm)
import argparse

def convert_coco_bbox_to_yolo(coco_bbox, img_width, img_height):
  """
  COCO bounding box formatını [x_min, y_min, width, height]
  YOLO formatına [x_center_norm, y_center_norm, width_norm, height_norm] dönüştürür.

  Args:
      coco_bbox: [x_min, y_min, width, height] formatında COCO bbox listesi.
      img_width: Görüntü genişliği.
      img_height: Görüntü yüksekliği.

  Returns:
      [x_center_norm, y_center_norm, width_norm, height_norm] formatında YOLO bbox listesi.
      None: Geçersiz girdi durumunda.
  """
  if not coco_bbox or len(coco_bbox) != 4 or img_width <= 0 or img_height <= 0:
    print(f"Uyarı: Geçersiz bbox veya görüntü boyutu: bbox={coco_bbox}, w={img_width}, h={img_height}")
    return None

  x_min, y_min, w, h = coco_bbox

  # Koordinatların geçerliliğini kontrol et
  if x_min < 0 or y_min < 0 or w <= 0 or h <= 0 or x_min + w > img_width or y_min + h > img_height:
     # Sınırları kırpma veya uyarı verme stratejisi burada belirlenebilir
     print(f"Uyarı: Görüntü sınırlarının dışına çıkan bbox: {coco_bbox}, img_w={img_width}, img_h={img_height}. Kırpılıyor.")
     x_min = max(0, x_min)
     y_min = max(0, y_min)
     w = min(w, img_width - x_min)
     h = min(h, img_height - y_min)
     if w <= 0 or h <= 0:
        print("Uyarı: Kırpma sonrası geçersiz bbox, atlanıyor.")
        return None


  x_center = x_min + w / 2
  y_center = y_min + h / 2

  x_center_norm = x_center / img_width
  y_center_norm = y_center / img_height
  width_norm = w / img_width
  height_norm = h / img_height

  return [x_center_norm, y_center_norm, width_norm, height_norm]

def coco_to_yolo(coco_json_path, output_dir):
  """
  COCO JSON formatındaki veri setini YOLO formatına dönüştürür.

  Args:
      coco_json_path: COCO formatındaki JSON dosyasının yolu.
      output_dir: Oluşturulacak YOLO .txt etiket dosyalarının kaydedileceği dizin.
  """
  try:
    with open(coco_json_path, 'r') as f:
      coco_data = json.load(f)
  except FileNotFoundError:
    print(f"Hata: COCO JSON dosyası bulunamadı: {coco_json_path}")
    return
  except json.JSONDecodeError:
    print(f"Hata: COCO JSON dosyası okunamadı veya bozuk: {coco_json_path}")
    return

  # Çıktı dizinini oluştur (varsa hata verme)
  os.makedirs(output_dir, exist_ok=True)

  # ----- Kategori ID'lerini YOLO indexlerine (0'dan başlayarak) eşle -----
  if 'categories' not in coco_data:
      print("Hata: JSON dosyasında 'categories' anahtarı bulunamadı.")
      return

  coco_cat_id_to_yolo_idx = {}
  yolo_idx_counter = 0
  # Kategori ID'leri sıralı olmayabilir, bu yüzden sıralayarak tutarlılık sağlıyoruz.
  sorted_categories = sorted(coco_data['categories'], key=lambda x: x['id'])
  for category in sorted_categories:
    # Eğer aynı ID tekrar gelirse atla (hatalı COCO formatı durumunda)
    if category['id'] not in coco_cat_id_to_yolo_idx:
        coco_cat_id_to_yolo_idx[category['id']] = yolo_idx_counter
        yolo_idx_counter += 1

  # ----- Görüntü bilgilerini hızlı erişim için haritala -----
  if 'images' not in coco_data:
      print("Hata: JSON dosyasında 'images' anahtarı bulunamadı.")
      return

  image_id_to_info = {}
  for img in coco_data['images']:
    image_id_to_info[img['id']] = {
        'file_name': img['file_name'],
        'width': img['width'],
        'height': img['height']
    }

  # ----- Annotasyonları görüntü ID'lerine göre grupla -----
  if 'annotations' not in coco_data:
      print("Uyarı: JSON dosyasında 'annotations' anahtarı bulunamadı. Etiket dosyaları boş olabilir.")
      annotations = []
  else:
      annotations = coco_data['annotations']

  image_id_to_annotations = {}
  for ann in annotations:
    image_id = ann['image_id']
    if image_id not in image_id_to_annotations:
      image_id_to_annotations[image_id] = []
    image_id_to_annotations[image_id].append(ann)

  # ----- YOLO formatında etiket dosyalarını oluştur -----
  missing_images_count = 0
  processed_images_count = 0
  print(f"Toplam {len(image_id_to_info)} görüntü işleniyor...")

  for image_id, img_info in tqdm(image_id_to_info.items(), desc="Dönüştürülüyor"):
    img_filename_base = os.path.splitext(img_info['file_name'])[0]
    yolo_txt_filename = f"{img_filename_base}.txt"
    yolo_txt_path = os.path.join(output_dir, yolo_txt_filename)

    img_width = img_info['width']
    img_height = img_info['height']

    with open(yolo_txt_path, 'w') as yolo_f:
      if image_id in image_id_to_annotations:
        for ann in image_id_to_annotations[image_id]:
          coco_cat_id = ann['category_id']
          coco_bbox = ann['bbox']

          if coco_cat_id not in coco_cat_id_to_yolo_idx:
              print(f"Uyarı: Bilinmeyen kategori ID'si {coco_cat_id} bulundu, atlanıyor. Görüntü: {img_info['file_name']}")
              continue

          yolo_class_index = coco_cat_id_to_yolo_idx[coco_cat_id]
          yolo_bbox = convert_coco_bbox_to_yolo(coco_bbox, img_width, img_height)

          if yolo_bbox: # Dönüşüm başarılıysa yaz
              x_center, y_center, w_norm, h_norm = yolo_bbox
              yolo_f.write(f"{yolo_class_index} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n")
      else:
        # Eğer bir görüntü için hiç anotasyon yoksa boş dosya oluşturulur (YOLO bunu bekler)
        pass # Dosya zaten 'w' modunda açıldığı için boş kalacak

    processed_images_count += 1

  print("\nDönüştürme tamamlandı.")
  print(f"Toplam {processed_images_count} etiket dosyası oluşturuldu: {output_dir}")
  if missing_images_count > 0:
      print(f"Uyarı: {missing_images_count} görüntü için JSON içinde bilgi bulunamadı.")

# Komut satırı argümanlarını işlemek için (isteğe bağlı)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert COCO JSON annotations to YOLO format.')
    parser.add_argument('json_file', type=str, help='Path to the COCO JSON annotation file.')
    parser.add_argument('output_dir', type=str, help='Directory to save the output YOLO .txt files.')

    args = parser.parse_args()

    coco_to_yolo(args.json_file, args.output_dir)

    # Örnek kullanım (komut satırı yerine doğrudan çalıştırmak isterseniz):
    # coco_json_input_path = 'val.json' # COCO JSON dosyanızın yolu
    # yolo_output_labels_dir = 'labels' # YOLO etiketlerinin kaydedileceği klasör
    # coco_to_yolo(coco_json_input_path, yolo_output_labels_dir)