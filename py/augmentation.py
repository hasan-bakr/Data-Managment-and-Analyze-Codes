import os
from PIL import Image, ImageEnhance
import shutil

def parlaklik_azalt(dizin_yolu, parlaklik_orani=0.8):
    try:
        for dosya_adi in os.listdir(dizin_yolu):
            dosya_yolu = os.path.join(dizin_yolu, dosya_adi)

            if dosya_adi.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
                try:
                    resim = Image.open(dosya_yolu)
                    enhancer = ImageEnhance.Brightness(resim)
                    yeni_resim = enhancer.enhance(parlaklik_orani)

                    yeni_dosya_adi = f"{os.path.splitext(dosya_adi)[0]}_parlaklik_azaltilmis{os.path.splitext(dosya_adi)[1]}"
                    yeni_dosya_yolu = os.path.join(dizin_yolu, yeni_dosya_adi)

                    # Yeni resmi kaydet
                    yeni_resim.save(yeni_dosya_yolu)
                    print(f"{dosya_adi} parlaklığı azaltıldı ve {yeni_dosya_adi} olarak kaydedildi.")

                    enhancer = ImageEnhance.Brightness(resim)
                    yeni_resim = enhancer.enhance(2 - parlaklik_orani)

                    yeni_dosya_adi = f"{os.path.splitext(dosya_adi)[0]}_parlaklik_artirilmis{os.path.splitext(dosya_adi)[1]}"
                    yeni_dosya_yolu = os.path.join(dizin_yolu, yeni_dosya_adi)

                    # Yeni resmi kaydet
                    yeni_resim.save(yeni_dosya_yolu)
                    print(f"{dosya_adi} parlaklığı artirildi ve {yeni_dosya_adi} olarak kaydedildi.")
                    # Eski resmi sil
                    #os.remove(dosya_yolu)

                    # Eğer aynı isimde bir .txt dosyası varsa
                    etiket_dosya_yolu = os.path.splitext(dosya_yolu)[0] + ".txt"
                    if os.path.exists(etiket_dosya_yolu):
                        yeni_etiket_dosya_adi_az = f"{os.path.splitext(dosya_adi)[0]}_parlaklik_azaltilmis.txt"
                        yeni_etiket_dosya_yolu_parlaklik_az = os.path.join(dizin_yolu, yeni_etiket_dosya_adi_az)
                        
                        yeni_etiket_dosya_adi_art = f"{os.path.splitext(dosya_adi)[0]}_parlaklik_artirilmis.txt"
                        yeni_etiket_dosya_yolu_parlaklik_art = os.path.join(dizin_yolu, yeni_etiket_dosya_adi_art)

                        # Dosyayı kopyala
                        shutil.copy(etiket_dosya_yolu, yeni_etiket_dosya_yolu_parlaklik_az)
                        shutil.copy(etiket_dosya_yolu, yeni_etiket_dosya_yolu_parlaklik_art)

                        print(f"{etiket_dosya_yolu} dosyası {yeni_etiket_dosya_adi_az} olarak yeniden adlandırıldı.")
                        print(f"{etiket_dosya_yolu} dosyası {yeni_etiket_dosya_adi_az} olarak yeniden adlandırıldı.")

                except Exception as e:
                    print(f"Hata: {dosya_adi} işlenirken bir sorun oluştu. {e}")

    except FileNotFoundError:
        print("Belirtilen dizin yolu bulunamadı.")
    except Exception as e:
        print(f"Hata: {e}")

dizin_yolu = r"C:\Users\524ha\Desktop\Tugra-1\sari_kapak_ev_etiket\MaksiSariKapak\tbkli"
parlaklik_azalt(dizin_yolu, 0.7)