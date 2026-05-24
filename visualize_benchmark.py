import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import sys

# 1. CSV Verisini Oku
csv_file = "benchmark_results.csv"
if len(sys.argv) > 1:
    csv_file = sys.argv[1]

print(f"📖 Veriler okunuyor: {csv_file}")
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    print(f"Hata: '{csv_file}' dosyası bulunamadı! Lütfen doğru klasörde olduğunuzdan emin olun.")
    exit()

# 2. Veri Temizliği: Başarısız veya 0.0 olan satırları (OOM hatası verenleri) ele
df = df[df["tokens_per_sec"] > 0]

# Estetik ve modern bir tema seçelim
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 11, 'figure.titlesize': 14})

print("📊 Grafik üretim süreci başlatıldı...")

# ------------------------------------------------------------------
# GRAFİK 1: Model Bazında Ortalama Üretim Hızı (Sıralı Yatay Bar)
# ------------------------------------------------------------------
# Modellerin ortalama hızlarını hesaplayıp büyükten küçüğe sıralayalım
model_speeds = df.groupby("model_name")["tokens_per_sec"].mean().sort_values(ascending=False).reset_index()

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    x="tokens_per_sec",
    y="model_name",
    data=model_speeds,
    palette="coolwarm_r",  # Hızlılar sıcak, yavaşlar soğuk renk
    ax=ax
)

# Grafik süslemeleri ve okunurluk ayarları
ax.set_title("Modellerin Ortalama Çıkarım Hızı (Tokens / Saniye)", fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Saniyede Üretilen Token (Daha yüksek daha iyi)", fontsize=12, labelpad=10)
ax.set_ylabel("Model Adı", fontsize=12)
ax.xaxis.grid(True, linestyle="--", alpha=0.6)

# Çubukların üzerine tam hız değerlerini yazalım (Okunurluğu artırır)
for index, value in enumerate(model_speeds["tokens_per_sec"]):
    ax.text(value + 2, index, f"{value:.1f} T/s", va="center", fontweight="bold", fontsize=10)

plt.tight_layout()
plt.savefig("01_model_hiz_karsilastirma.png", dpi=300)
plt.close()
print("✓ Grafik 1 Kaydedildi: 01_model_hiz_karsilastirma.png")

# ------------------------------------------------------------------
# GRAFİK 2: Kategori Bazında Model Performansı (Gruplanmış Bar)
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 7))

sns.barplot(
    x="category",
    y="tokens_per_sec",
    hue="model_name",
    data=df,
    palette="tab10",
    ax=ax
)

ax.set_title("Test Kategorilerine Göre Model Hız Dağılımları", fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Benchmark Kategorisi", fontsize=12, labelpad=10)
ax.set_ylabel("Tokens / Saniye", fontsize=12)
ax.yaxis.grid(True, linestyle="--", alpha=0.6)

# Kategori isimlerinin çakışmaması için hafif eğelim
plt.xticks(rotation=15, ha="right")

# Lejantı (Model isim kutusunu) grafiğin dışına taşıyalım ki veriyi kapatmasın
plt.legend(title="Modeller", bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)

plt.tight_layout()
plt.savefig("02_kategori_bazli_hizlar.png", dpi=300)
plt.close()
print("✓ Grafik 2 Kaydedildi: 02_kategori_bazli_hizlar.png")

print("\n🎉 Tebrikler! Tüm grafikler yüksek çözünürlükte (300 DPI) başarıyla üretildi.")