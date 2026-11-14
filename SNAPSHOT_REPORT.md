# 📸 Test Başarısızlığı Snapshot Raporu Sistemi

## Genel Bakış

Test başarısız olduğunda otomatik olarak 3D görselleştirmeler kaydeder, HTML raporunu oluşturur ve tarayıcıda incelenebilir hale getirir.

## ✨ Özellikler

### 1. **Otomatik Snapshot Kaydetme**
```
Test Başarısız → Snapshot Alınır → HTML Oluşturulur → Rapor Hazır
```

### 2. **3D Görselleştirme**
- **Gövde** (Mavi renk) - Durağan konumda
- **Kapak** (Kırmızı/Yeşil renk) - Test edilen açıda
- **Açı Bilgisi** - Her resimde yazılı
- **Bakış Açısı** - Optimal görüş için ayarlanmış

### 3. **Karşılaştırma Görselleri**
Sorunlu pozisyon ile güvenli pozisyonu yan yana gösterir:
- **Sol Panel**: Kapalı konumda çarpışma (❌)
- **Sağ Panel**: Açık konumda sorunsuz (✅)

### 4. **İnteraktif HTML Rapor**
- Responsive tasarım (desktop, tablet, mobile)
- İstatistik kartları
- Ayrıntılı hata bilgileri
- Stil ve renk kodlaması

## 📊 Rapor İçeriği

### İstatistik Bölümü
```
┌─────────────────────────────────────┐
│  2 Başarısız  │  32 Toplam  │ 93.75% │
└─────────────────────────────────────┘
```

### Başarısız Test Bölümleri
Her başarısız test için:
- Test adı ve tarifi
- Açı bilgisi
- Hata mesajı (kırmızı kutuda)
- 3D snapshot görseli
- Karşılaştırma görseli (varsa)

## 🚀 Kullanım

### Test Çalıştırma ve Rapor Oluşturma

```bash
cd /Users/enesoncu/llm-hacker

# Tüm testleri çalıştır
docker-compose run --rm box-assembly-test pytest -v tests/

# Snapshot'lar otomatik kaydedilir: test_failures_report/
```

### Raporu Açma (3 Yol)

**Yol 1: Web Sunucusu ile**
```bash
# Terminalde
cd /Users/enesoncu/llm-hacker/test_failures_report
python3 -m http.server 8765

# Tarayıcıda
open http://localhost:8765/index.html
```

**Yol 2: Direkt Dosya Aç**
```bash
open /Users/enesoncu/llm-hacker/test_failures_report/index.html
```

**Yol 3: Tarayıcıda Yazarak**
```
file:///Users/enesoncu/llm-hacker/test_failures_report/index.html
```

## 📁 Dosya Yapısı

```
test_failures_report/
├── index.html                    # Ana rapor dosyası
├── collision_angle_0deg.png      # 0° açıda çarpışma
├── collision_angle_15deg.png     # 15° açıda çarpışma
├── collision_angle_30deg.png     # 30° açıda çarpışma
├── unsafe_angle_0deg.png         # Güvensiz: 0°
├── unsafe_angle_5deg.png         # Güvensiz: 5°
├── unsafe_angle_10deg.png        # Güvensiz: 10°
├── unsafe_angle_15deg.png        # Güvensiz: 15°
├── unsafe_angle_20deg.png        # Güvensiz: 20°
├── unsafe_angle_25deg.png        # Güvensiz: 25°
├── unsafe_angle_30deg.png        # Güvensiz: 30°
├── unsafe_angle_35deg.png        # Güvensiz: 35°
└── comparison_closed_vs_open.png # Kapalı vs Açık karşılaştırması
```

## 🎨 Renk Kodlaması

| Renk | Anlamı | Durum |
|------|--------|-------|
| **Mavi** | Gövde | Sabit |
| **Kırmızı** | Kapak (Kapalı) | Çarpışma var |
| **Yeşil** | Kapak (Açık) | Sorunsuz |

## 📊 Snapshot'lardaki Bilgiler

### Başlık
```
Çarpışma Tespiti - Açı: 0°
```
Test adı ve test edildi açı

### Görsel Içeriği
- **3D Model**: Mesh triangles ile tam geometri
- **Koordinat Eksenleri**: X (kırmızı), Y (yeşil), Z (mavi)
- **Bakış Açısı**: Elev: 20°, Azimut: -60°
- **Grid**: Referans için arka plan grid'i

## 🔍 Analiz Yapma

### Çarpışma Noktalarını Bulma
1. Snapshots'u karşılaştırma görselinde açın
2. Sol tarafta (kapalı) kırmızı kapağı inceyin
3. Gövdenin (mavi) içine girdiği yerleri fark edin
4. Sağ tarafta (açık) yeşil kapağı görmek için kaydırın

### Açı Progresyonunu İzleme
1. 0°deg'den başlayarak artan açılar
2. Kapağın hangi açıdan güvenli hale geldiğini gözlemleyin
3. Desen fark edin: 0°-35° çarpışmalı, 40°+ sorunsuz

### Mesh Kalitesi Kontrol
- Üçgenlerin düzgün görünüşünü kontrol edin
- Delikler veya açıklamalar arayın
- Model boşluklarını fark edin

## 💡 İpuçları

### 1. **Rapor Paylaşma**
Tüm dosyaları (HTML + PNG'ler) bir klasör halinde gönderebilirsiniz:
```bash
zip -r test_report.zip test_failures_report/
# test_report.zip'i e-postayla gönder
```

### 2. **Tekrar Çalıştırma**
CAD modelini düzenledikten sonra:
```bash
# Yeni STL'leri yerleştir
# Testleri çalıştır
docker-compose run --rm box-assembly-test pytest -v tests/
# Yeni rapor otomatik oluşturulur (eski raporun üzerine yazılır)
```

### 3. **Spesifik Test Çalıştırma**
```bash
# Sadece başarısız testleri çalıştır
docker-compose run --rm box-assembly-test pytest -v tests/test_gravity_resistance.py

# Belirli açıyı test et
docker-compose run --rm box-assembly-test \
  pytest -v tests/test_gravity_resistance.py::TestGravityResistance::test_lid_no_collision_at_angle[0]
```

## 🔧 Teknik Detaylar

### Snapshot Oluşturma
```python
visualize_assembly(
    body_mesh,           # Gövde
    rotated_lid,         # Döndürülmüş kapak
    title,               # Başlık
    angle_deg=angle,     # Açı
    save_path=path       # Kaydetme yolu
)
```

### Karşılaştırma Görseli
```python
create_comparison_visualization(
    body_mesh,           # Gövde
    lid_mesh_before,     # Kapak (kapalı)
    lid_mesh_after,      # Kapak (açık)
    0,                   # Önceki açı
    45,                  # Sonraki açı
    "Başlık",
    save_path=path
)
```

### HTML Rapor
```python
create_html_report(failures_list)
# failures_list: [
#     {
#         'test_name': 'collision_angle_0deg',
#         'angle': 0,
#         'image_path': 'path/to/image.png',
#         'error_message': 'Çarpışma tespit edildi',
#         'comparison_image': 'path/to/comparison.png'
#     }
# ]
```

## 📊 Mevcut Sonuçlar

### Test Duruşu
- **Total**: 32 test
- **Geçen**: 30 test
- **Başarısız**: 2 test
- **Başarı Oranı**: 93.75%

### Kritik Bulgu
**Kapak Tasarım Hatası**: 0°-35° aralığında gövdeye çarpıyor
- Çarpışmalı: 0°, 5°, 10°, 15°, 20°, 25°, 30°, 35°
- Sorunsuz: 40°, 45°, 50°, ... 180°

### Snapshot İstatistiği
- Toplam Snapshot: 13
- Çarpışma Açısı: 0°, 15°, 30°
- Güvensiz Açı: 8 adet
- Karşılaştırma Görseli: 1 adet

## 🚨 Sorun Giderme

### Snapshot Kaydedilmedi
```bash
# Klasörü kontrol et
ls -la test_failures_report/

# Izinleri kontrol et
chmod 755 test_failures_report/
```

### HTML açılmıyor
```bash
# Dosya mevcut mu kontrol et
file test_failures_report/index.html

# Sunucu çalışıyor mu kontrol et
curl http://localhost:8765/index.html
```

### Görseller görüntülenmiyor
```bash
# PNG dosyaları kontrol et
file test_failures_report/*.png

# Dosya boyutlarını kontrol et
ls -lh test_failures_report/*.png
```

## 📚 Kaynaklar

- [Matplotlib 3D](https://matplotlib.org/stable/tutorials/toolkits/mplot3d.html)
- [Trimesh Documentation](https://trimesh.org/)
- [HTML Report Styling](https://developer.mozilla.org/en-US/docs/Web/CSS)

---

**Hazırlanma Tarihi**: 14 Kasım 2026  
**Test Ortamı**: Docker + Python 3.11 + Trimesh  
**Durum**: ✅ Aktif ve Çalışıyor
