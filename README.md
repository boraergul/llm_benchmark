# 🚀 LLM Benchmark Otomasyon ve Görselleştirme Kılavuzu

Bu araç; Ollama üzerinde barındırılan yerel dil modellerinin (LLM) çıkarım (inference) performansını, kararlılığını ve hızını (Token/s) otomatik olarak test etmek ve sonuçları yüksek çözünürlüklü grafiklerle görselleştirmek için geliştirilmiştir.

---

## 📋 İçindekiler
1. [Gereksinimler](#1-gereksinimler)
2. [Kurulum ve Hazırlık](#2-kurulum-ve-hazırlık)
3. [Benchmark Çalıştırma](#3-benchmark-çalıştırma)
4. [Görselleştirme ve Grafik Analizleri](#4-görselleştirme-ve-grafik-analizleri)
5. [Proje Yapısı ve Dosyalar](#5-proje-yapısı-ve-dosyalar)
6. [Benchmark Mantığı ve Sorular](#6-benchmark-mantığı-ve-sorular)

---

## 1. Gereksinimler

Sistemin düzgün çalışabilmesi için aşağıdaki bileşenlerin yüklü ve çalışır durumda olması gerekir:
- **İşletim Sistemi:** Linux (Ubuntu/Debian önerilir)
- **Python:** Python 3.8 veya üzeri
- **Ollama:** Yerel model çıkarım sunucusu (`localhost:11434` portunda çalışmalı)
- **GPU Sürücüleri (İsteğe Bağlı):** AMD GPU'lar için ROCm veya NVIDIA GPU'lar için CUDA (Ollama'nın GPU ivmelendirmesini kullanabilmesi için)

---

## 2. Kurulum ve Hazırlık

### Adım 1: Sanal Ortam Oluşturma ve Aktifleştirme
Terminalde proje dizinine gidin ve bağımlılıkların izole çalışması için bir sanal ortam oluşturun:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Adım 2: Gerekli Kütüphanelerin Yüklenmesi
Grafik çizimi ve veri işleme için gereken kütüphaneleri yükleyin:
```bash
pip install pandas matplotlib seaborn requests
```

### Adım 3: Ollama Sunucusunun Başlatılması
Ollama servisinin arka planda çalıştığından emin olun.
```bash
# Ollama durum kontrolü
systemctl status ollama
```

---

## 3. Benchmark Çalıştırma

Tüm test sürecini başlatmak için `benchmark.py` dosyasını çalıştırın:
```bash
python3 benchmark.py
```

### 💬 Çalışma Esnasındaki Adımlar:
1. **Model Seçimi:** Script Ollama üzerinde yüklü olan modelleri çeker ve listeler. Test etmek istediğiniz modelin numarasını girebilir veya tüm modelleri sırayla test etmek için en son seçeneği (`TÜM MODELLERİ SIRAYLA ÇALIŞTIR`) seçebilirsiniz.
2. **Zaman Aşımı (Timeout) Ayarı:** Her bir test sorusu için maksimum yanıt süresini saniye cinsinden belirlersiniz (Varsayılan: `300` saniye, sınırsız için `0`). Büyük modellerin CPU üzerinde çalışırken takılmasını veya base modellerin sonsuz döngüye girmesini engellemek için önemlidir.
3. **Veri Kaydı (Dual-Saving):** Test tamamlandığında veriler iki yere aynı onda yazılır:
   - `benchmark_results_YYYYMMDD_HHMMSS.csv` (Tarih damgalı arşiv dosyası)
   - `benchmark_results.csv` (Kümülatif tüm zamanlar veri tabanı)
4. **Otomatik Görselleştirme:** Test bittiği an, grafik çizim kodları otomatik olarak tetiklenerek en güncel grafikler üretilir.

---

## 4. Görselleştirme ve Grafik Analizleri

Grafik oluşturucular varsayılan olarak kümülatif `benchmark_results.csv` dosyasını okur. Ancak isterseniz geçmiş bir test oturumunu da ayrıca görselleştirebilirsiniz.

### 📊 Mevcut Grafik Türleri
1. **01_model_hiz_karsilastirma.png:** Modellerin saniye başına ürettiği ortalama token sayısını (Tokens / Saniye) büyükten küçüğe sıralı gösterir.
2. **02_kategori_bazli_hizlar.png:** Modellerin kategorilere (Bilgi, Mantık, Kodlama, Yaratıcılık vb.) göre hız performanslarını yan yana karşılaştırır.
3. **03_model_kararlilik_boxplot.png:** Modellerin çıkarım hızlarındaki dalgalanmaları ve kararlılığını gösteren kutu grafiği (Boxplot).
4. **04_boyut_vs_hiz_korelasyon.png:** Model parametre boyutu (Milyar parametre - B) arttıkça çıkarım hızının nasıl değiştiğini ve CPU/GPU dağılımının etkisini gösteren saçılım grafiği (Scatter Plot).
5. **05_toplam_sure_karsilastirma.png:** Her modelin tüm testi tamamlamak için harcadığı toplam süreyi gösterir.

### 🛠️ Manuel Grafik Üretimi

**Tüm zamanların (kümülatif) grafiğini yenilemek için:**
```bash
python3 visualize_all.py
python3 visualize_benchmark.py
```

**Belirli bir geçmiş testi görselleştirmek için:**
```bash
python3 visualize_all.py benchmark_results_20260524_134216.csv
python3 visualize_benchmark.py benchmark_results_20260524_134216.csv
```

---

## 5. Proje Yapısı ve Dosyalar

* **`benchmark.py`:** Testleri yürüten, API isteklerini atan ve verileri CSV'ye kaydeden ana script.
* **`visualize_benchmark.py`:** Ortalama hız ve kategori bazlı hız grafiklerini (Grafik 1 ve 2) çizen script.
* **`visualize_all.py`:** Boyut korelasyonu, kararlılık boxplotu ve toplam süre analizini (Grafik 3, 4 ve 5) çizen script.
* **`questions.json`:** Test sırasında modellere yöneltilen benchmark sorularını ve sıcaklık (temperature) değerlerini içeren dosya.
* **`benchmark_results.csv`:** Şimdiye kadar yapılan tüm testlerin biriktiği ana veri tabanı.
* **`logbook.md`:** Donanım gözlemleri ve performans notlarının manuel kaydedildiği günlük.

---

## 6. Benchmark Mantığı ve Sorular

Benchmark soruları (`questions.json`), modellerin farklı yönlerini test etmek için özel olarak tasarlanmış 6 kategoriden oluşur:

1. **Knowledge (Bilgi) [KNL-01]:** Teorik ve akademik bilgi kalitesini ve dil tonunu test eder.
2. **Reasoning (Mantık) [REA-01]:** Matematiksel ve mantıksal problem çözme becerilerini ölçer.
3. **Reasoning/Coding (Yazılım) [COD-01]:** Kodlama ve yapısal algoritmalar geliştirme yeteneğini test eder.
4. **Instruction Following (Kural Takibi) [INS-01]:** Modelin karmaşık kurallara ve kısıtlamalara ne kadar sadık kaldığını ölçer.
5. **Creativity (Yaratıcılık) [CRT-01]:** Modelin hikaye anlatımı ve edebi yaratıcılığını test eder.
6. **Safety/Guardrails (Güvenlik) [SAF-01]:** Modelin zararlı isteklere karşı güvenlik önlemlerini (reddetme davranışı veya sınırlarını) test eder.
