import json
import gensim
from gensim.models import Word2Vec
import numpy as np

# JSON dosyasını yükleyin
try:
    with open("C:\\Users\\burcu\\proje1\\proje\\yapayzeka.json", "r", encoding="utf-8") as f: 
       tarifler = json.load(f)
       print("Tarifler başarıyla yüklendi.")
except FileNotFoundError:
    print("yapayzeka.json dosyası bulunamadı. Lütfen tarifleri ekleyin.")
    exit()


# Malzemeleri bir listede topla (tüm tarifler için)
tum_malzemeler = []
for tarif in tarifler['tarifler']:
    tum_malzemeler.extend([m.lower() for m in tarif["malzemeler"]])

# Word2Vec modelini eğit (daha iyi parametrelerle)
model = Word2Vec([tum_malzemeler], min_count=1, vector_size=100, window=5, sg=1)

def benzerlik_hesapla(malzemeler, hedef_malzemeler):
    if not malzemeler or not hedef_malzemeler:
        return 0
    benzerlikler = []
    for malzeme in malzemeler:
        malzeme_benzerlikleri = []
        for hedef in hedef_malzemeler:
            try:
                malzeme_benzerlikleri.append(model.wv.similarity(malzeme, hedef))
            except KeyError:  # Kelime modelde yoksa 0 benzerlik kabul et
                pass
        if malzeme_benzerlikleri:
            benzerlikler.append(max(malzeme_benzerlikleri)) # Bir malzeme için en yüksek benzerliği al
    return np.mean(benzerlikler)  if benzerlikler else 0 # tüm benzerliklerin ortalamasını alarak tarifin genel benzerlik oranını çıkartıyor

mevcut_malzemeler = input("Elindeki malzemeleri virgülle ayirarak girin: ").split(",")
mevcut_malzemeler = [malzeme.strip().lower() for malzeme in mevcut_malzemeler]

uygun_tarifler = []
for tarif in tarifler['tarifler']:
    tarif_malzemeleri = [malzeme.lower() for malzeme in tarif["malzemeler"]]
    benzerlik = benzerlik_hesapla(mevcut_malzemeler, tarif_malzemeleri)
    if benzerlik > 0:  # Sadece pozitif benzerlikleri ekle
        uygun_tarifler.append((tarif, benzerlik))

uygun_tarifler.sort(key=lambda x: x[1], reverse=True)

if uygun_tarifler:
    print("Elindeki malzemelere en benzer ilk 5 tarif:")
    for i, (tarif, benzerlik) in enumerate(uygun_tarifler[:5]):  # Sadece ilk 5 tarifi göster
        tarif_adi = tarif.get('tarif_adi', tarif.get('isim', 'Bilinmeyen Tarif'))
        malzemeler = tarif.get('malzemeler', [])
        yapilisi = tarif.get('yapılışı', tarif.get('tarif', 'Yapılış bilgisi bulunamadı.')) 
        print(f"\n{i+1}. {tarif_adi} (Benzerlik: {benzerlik:.2f})")
        print(f"  Malzemeler: {', '.join(malzemeler)}")
        print(f"  Yapılışı: {yapilisi}")
else:
    print("Elindeki malzemelere benzer bir tarif bulunamadi.")