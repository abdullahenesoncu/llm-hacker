# Box Assembly Test Suite - Kutu ve Kapak Montaj Testi

Temiz, Docker-tabanlı test suite'i kutu ve kapak montajının dizaynını doğrulayan kapsamlı testler içerir.

## Test Türleri

### 1. Yerçekimi Direnç Testi (`test_gravity_resistance.py`)
Kutu havada tutulurken kapağın düşüp düşmediğini, farklı rotasyonlarda stabilitesini kontrol eder.

- ✅ 15°-90° açılarda kapak güvenli
- ❌ 0°-35° açılarda kapak gövdeye çarpıyor (TASARIM HATASI)

### 2. Su Sızdırmama Testi (`test_watertightness.py`)
Montajın su geçirmezliğini ve mesh kalitesini doğrular.

- ✅ Gövde su geçirmez
- ✅ Kapak su geçirmez
- ✅ Geçerli geometriler
- ✅ Mesh kalitesi iyi

### 3. Menteşe Dönme Testi (`test_hinge_rotation.py`)
Menteşe etrafında kapağın düzgün ve güvenli dönüşünü test eder.

- ✅ Menteşe pozisyonu doğru algılandı
- ✅ 0°-180° aralığında dönüş güvenli
- ✅ Dönüş düzgün
- ✅ Boşluk yeterli

## Test Sonuçları

```
======================== 30 PASSED, 2 FAILED ========================
```

### Geçen Testler (30)
- Menteşe Dönme Testleri: 13/13 ✅
- Su Sızdırmama Testleri: 10/10 ✅
- Yerçekimi (Açılı): 7/9 ✅

### Başarısız Testler (2)
- **test_lid_no_collision_at_angle[0]**: Kapak kapalı konumda (0°) gövdeye çarpıyor
- **test_all_angles_safe**: 0°-35° aralığında çarpışma tespit edildi

## Tespit Edilen Sorun

**Kritik Tasarım Hatası**: Kapak kapalı konumda gövdeye çarpıyor!

```
Güvensiz açılar: 0°, 5°, 10°, 15°, 20°, 25°, 30°, 35°
```

Bu sorun:
1. Kapağın kapanmasını zorlaştırır
2. Kullanıcı deneyimini kötüleştirir
3. Montaj aşamasında hasar riskini artırır

## Çalıştırma

```bash
# Docker ile tüm testleri çalıştır
docker-compose run --rm box-assembly-test pytest -v tests/

# Belirli bir test modülünü çalıştır
docker-compose run --rm box-assembly-test pytest -v tests/test_hinge_rotation.py

# Sadece başarılı testleri göster
docker-compose run --rm box-assembly-test pytest tests/ -v --tb=no

# Detaylı hata raporu
docker-compose run --rm box-assembly-test pytest tests/ -v --tb=short
```

## Test Yapısı

```
tests/
├── conftest.py                # Pytest fixtures (kutu-kapak montajı)
├── test_gravity_resistance.py # Yerçekimi & dönüş direnci
├── test_hinge_rotation.py     # Menteşe dönem mekanizması
└── test_watertightness.py     # Su sızdırmama & geometri
```

## Sonuç

✅ **Mekanik olarak**: Menteşe sistemi 40°+ açılarında sorunsuzca çalışıyor

❌ **Tasarımda Sorun**: Kapak kapalı/açılmaya başladığı konumlarda gövdeye çarpıyor - DİZAYN REVIZYON GEREKLİ

## Geliştirme Seçenekleri

1. **Kapak boşluğunu artır** - Gövde ile kapak arasına 0.5mm+ boşluk ekle
2. **Menteşe pozisyonunu değiştir** - Menteşeyi daha geriye/ileriye taşı
3. **Gövde şekline kil** - İç kenarları eğileştir

---
*Docker'da Python 3.11, trimesh, numpy, scipy kullanılarak test edilmiştir.*
