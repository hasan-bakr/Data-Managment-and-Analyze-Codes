# Data Management and Analyze Codes

Bu proje, veri yönetimi ve analizine yönelik çeşitli Python betikleri ve Jupyter Notebook dosyalarını içerir. Özellikle görüntü ve video etiketleme, veri seti düzenleme, veri temizleme ve makine öğrenimi eğitim süreçlerini kolaylaştırmak için tasarlanmıştır.

## Klasörler

- **notebooks/**: Görüntü ve video etiketleme, veri temizleme, veri bölme ve model eğitimi gibi işlemler için Jupyter Notebook dosyaları.
- **py/**: Veri işleme, etiket düzenleme, veri seti oluşturma ve analiz için Python betikleri.

## Öne Çıkan Dosyalar

### Notebooks
- `autolabel_to_image.ipynb`: Görüntülere otomatik etiket ekleme.
- `autolabel_to_video.ipynb`: Videolara otomatik etiket ekleme.
- `train_fasterrcnn.ipynb`: Faster R-CNN ile model eğitimi.
- `train_valid_test_split_code.ipynb`: Veri setini eğitim, doğrulama ve test olarak bölme.
- `delete_duplicate.ipynb`: Yinelenen dosyaları silme.

### Python Scriptleri
- `coco2yolo_label_format.py`: COCO etiket formatını YOLO formatına dönüştürme.
- `make_dataset_with_equalized_labels_and_augmentations.py`: Etiketleri eşitleyerek ve veri artırma uygulayarak veri seti oluşturma.
- `delete_edge_labels.py`: Kenar etiketlerini silme.
- `merge_class_folders_to_create_datas.py`: Sınıf klasörlerini birleştirerek veri seti oluşturma.

## Kurulum

1. Python 3.8+ kurulu olmalıdır.
2. Gerekli paketleri yüklemek için:
   ```bash
   pip install -r requirements.txt
   ```
   (Not: requirements.txt dosyasını kendiniz oluşturmalısınız veya notebooklarda kullanılan paketleri manuel yükleyebilirsiniz.)

## Kullanım

- Jupyter Notebook dosyalarını çalıştırmak için:
  ```bash
  jupyter notebook
  ```
- Python betiklerini çalıştırmak için:
  ```bash
  python py/<dosya_adı>.py
  ```

## Katkı

Katkıda bulunmak için yeni bir dal oluşturup değişikliklerinizi gönderin. Pull request açabilirsiniz.

