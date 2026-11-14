# Box Assembly Test Suite (Kutu Kapak Montaj Test Suite)

Kutu ve kapak STL modelleriyle montaj dizaynını test eden Docker-tabanlı pytest suite'i.

## 🎯 Amaç

3D baskı yapılan kutu ve kapağın:
- ✅ Menteşe mekanizmasının sorunsuz çalışışı
- ✅ Su sızdırmama kapasitesi
- ✅ Yapısal bütünlüğü
- ✅ Çeşitli rotasyonlarda fiziksel stabilitesi
- ❌ Tasarım hatalarını

...test etmek.

## 📋 Test Kapsamı

### Test 1: Yerçekimi Direnç Testi
```python
pytest tests/test_gravity_resistance.py
```
- Kutu havada tutulurken kapağın 0°-90° açılarda düşüp düşmediğini kontrol eder
- Kapalı konumda çarpışma kontrolü
- Açılı konumda stabilitesi

### Test 2: Su Sızdırmama
```python
pytest tests/test_watertightness.py
```
- Gövde ve kapağın watertight (su geçirmez) olması
- Geçerli geometriler
- Mesh kalite kontrolü

### Test 3: Menteşe Dönme Mekanizması
```python
pytest tests/test_hinge_rotation.py
```
- Menteşe ekseninin doğru algılanması
- 0°-180° aralığında güvenli dönüş
- Dönüşün düzgünlüğü (sudden jumps yok)
- Minimum boşluk kontrolü

## 🚀 Kullanım

### Tüm Testleri Çalıştır

```bash
docker-compose run --rm box-assembly-test pytest -v tests/
```

### Belirli Testleri Çalıştır

```bash
# Sadece menteşe testleri
docker-compose run --rm box-assembly-test pytest -v tests/test_hinge_rotation.py

# Sadece su sızdırmama testleri
docker-compose run --rm box-assembly-test pytest -v tests/test_watertightness.py

# Belirli bir test fonksiyonu
docker-compose run --rm box-assembly-test pytest -v tests/test_gravity_resistance.py::TestGravityResistance::test_lid_fully_open_angle
```

### Açıklamalı Rapor

```bash
# Hata detaylarıyla
docker-compose run --rm box-assembly-test pytest -v tests/ --tb=short

# Sadece başarı/başarısızlık
docker-compose run --rm box-assembly-test pytest -v tests/ --tb=no

# Çıktıyı dosyaya kaydet
docker-compose run --rm box-assembly-test pytest -v tests/ --tb=short > test_report.txt
```

## 📁 Proje Yapısı

```
.
├── Dockerfile                    # Docker imajı tanımı
├── docker-compose.yml            # Docker Compose konfigürasyonu
├── bottom.stl                    # Kutu gövdesi (STL dosyası)
├── top.stl                       # Kapak (STL dosyası)
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_gravity_resistance.py # Yerçekimi & rotasyon testleri
│   ├── test_hinge_rotation.py    # Menteşe mekanizması testleri
│   └── test_watertightness.py    # Su sızdırmama testleri
├── TEST_RESULTS.md              # Detaylı test sonuçları
└── README.md                     # Bu dosya
```

## 🔧 Teknik Detaylar

### Kullanılan Kütüphaneler
- **trimesh**: 3D mesh işleme ve çarpışma testi
- **numpy**: Sayısal hesaplamalar
- **pytest**: Test framework'ü
- **pybullet**: Fizik simülasyonu (opsiyonel)
- **python-fcl**: Collision detection (FCL wrapper)
- **scipy**: Gelişmiş sayısal algoritmaları
- **matplotlib**: Görselleştirme

### Docker İmajı
- Base: `python:3.11`
- İşletim Sistemi: Debian Trixie
- Sistem Paketleri: build-essential, cmake, git, liboctomap-dev, libfcl-dev

## 📊 Test Sonuçları

Son çalıştırma:
```
======================== 30 PASSED, 2 FAILED ========================

Başarılandı (30):
✅ Menteşe Dönme Testleri: 13/13
✅ Su Sızdırmama Testleri: 10/10
✅ Yerçekimi Testleri (Açılı): 7/9

Başarısız (2):
❌ test_gravity_resistance.py::test_lid_no_collision_at_angle[0]
   → Kapak 0° konumda gövdeye çarpıyor
❌ test_gravity_resistance.py::test_all_angles_safe
   → 0°-35° açı aralığında çarpışma tespit edildi
```

**Teşhis**: Tasarımda revizyon gerekli - kapak kapalı konumda boşluk yeterli değil.

## 🛠️ Menteşe Otomatik Algılaması

Test suite menteşe pozisyonunu otomatik olarak algılar:
```python
# Kapağın sınırlarından menteşe pozisyonunu hesapla
lid_bounds = lid_mesh.bounds
hinge_origin = np.array([
    lid_bounds[0][0],        # X minimum (Sol kenar)
    lid_bounds[1][1],        # Y maksimum (Arka yüz)
    lid_bounds[1][2]         # Z maksimum (Üst seviye)
])
hinge_axis = np.array([1, 0, 0])  # X ekseni etrafında dönme
```

## 🎓 Örnek: Özel Test Yazma

```python
# tests/test_custom.py
import pytest
import trimesh
import numpy as np

def test_my_custom_check(box_assembly):
    """Özel bir kontrol yaz"""
    body = box_assembly['body']
    lid = box_assembly['lid']
    
    # Testini yaz
    assert body.volume > 0
    print("✓ Özel test başarılı")
```

Çalıştır:
```bash
docker-compose run --rm box-assembly-test pytest -v tests/test_custom.py
```

## 📚 İlgili Belgeler

- [TEST_RESULTS.md](./TEST_RESULTS.md) - Detaylı test sonuçları ve analizy
- Trimesh Docs: https://trimesh.org/
- Pytest Docs: https://docs.pytest.org/

## 🤝 Katkı

Testleri geliştirmek veya hata rapor etmek için PR açın.

---

**Son Güncelleme**: 14 Kasım 2026
**Test Ortamı**: Docker + Python 3.11 + pytest
