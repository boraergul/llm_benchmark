import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import sys

# 1. Veriyi yükle ve temizle
csv_file = "benchmark_results.csv"
if len(sys.argv) > 1:
    csv_file = sys.argv[1]

print(f"📖 Veriler okunuyor: {csv_file}")
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    print(f"Hata: '{csv_file}' dosyası bulunamadı!")
    exit()

# Hatalı/boş satırları temizle
df = df[df["tokens_per_sec"] > 0]

# İsimlerdeki gizli boşlukları kökten temizle (Grafikteki eksikliğin ana çözümü)
df["model_name"] = df["model_name"].astype(str).str.strip()
df["category"] = df["category"].astype(str).str.strip()

# Parametre boyutlarını numerik yap (Örn: 8.0B -> 8.0)
def clean_param(val):
    if pd.isna(val): return 0.0
    val = str(val).upper().replace("B", "").strip()
    try: return float(val)
    except: return 0.0

df["param_numeric"] = df["param_size"].apply(clean_param)

# Grafik şablon ayarları
sns.set_theme(style="darkgrid")
plt.rcParams.update({'font.size': 10, 'axes.labelsize': 12, 'axes.titlesize': 14})

print(f"📊 Toplam {df['model_name'].nunique()} benzersiz model bulundu. Grafikler çiziliyor...")

# ------------------------------------------------------------------
# GRAFİK 3: Model Kararlılığı ve Hız Dağılımı (Boxplot)
# ------------------------------------------------------------------
plt.figure(figsize=(12, 6))
# Hıza göre modelleri sıralayalım
order = df.groupby("model_name")["tokens_per_sec"].mean().sort_values(ascending=False).index

sns.boxplot(x="tokens_per_sec", y="model_name", data=df, order=order, palette="vlag")
plt.title("Modellerin Çıkarım Hızı Dağılımı ve Kararlılığı", fontweight="bold", pad=15)
plt.xlabel("Tokens / Saniye")
plt.ylabel("Model Adı")
plt.tight_layout()
plt.savefig("03_model_kararlilik_boxplot.png", dpi=300)
plt.close()
print("✓ 03_model_kararlilik_boxplot.png oluşturuldu.")

# ------------------------------------------------------------------
# GRAFİK 4: Model Boyutu vs Hız İlişkisi (Scatter Plot - Darboğaz Analizi)
# ------------------------------------------------------------------
plt.figure(figsize=(10, 6))
# Benzersiz modellerin ortalama hız ve boyutlarını alalım
scatter_df = df.groupby(["model_name", "param_numeric", "processor"])["tokens_per_sec"].mean().reset_index()

sns.scatterplot(
    x="param_numeric", 
    y="tokens_per_sec", 
    hue="processor", 
    style="processor",
    s=200, 
    data=scatter_df, 
    palette="Set1"
)

# Noktaların yanına model isimlerini yazalım
for i in range(scatter_df.shape[0]):
    plt.text(
        x=scatter_df.param_numeric[i] + 0.5, 
        y=scatter_df.tokens_per_sec[i] + 3, 
        s=scatter_df.model_name[i], 
        fontweight='semibold', 
        size=9
    )

plt.title("Model Boyutu (Billion) vs Çıkarım Hızı (T/s)", fontweight="bold", pad=15)
plt.xlabel("Model Parametre Boyutu (Milyar - B)")
plt.ylabel("Ortalama Tokens / Saniye")
plt.xlim(0, scatter_df["param_numeric"].max() + 5)
plt.tight_layout()
plt.savefig("04_boyut_vs_hiz_korelasyon.png", dpi=300)
plt.close()
print("✓ 04_boyut_vs_hiz_korelasyon.png oluşturuldu.")

# ------------------------------------------------------------------
# GRAFİK 5: Toplam Yanıt Süreleri (Cumulative Duration)
# ------------------------------------------------------------------
plt.figure(figsize=(12, 6))
duration_df = df.groupby("model_name")["duration_sec"].sum().sort_values().reset_index()

sns.barplot(x="duration_sec", y="model_name", data=duration_df, palette="Reds_r")
plt.title("Modellerin Toplam Test Yanıt Süreleri (Daha kısa daha iyi)", fontweight="bold", pad=15)
plt.xlabel("Toplam Harcanan Süre (Saniye)")
plt.ylabel("Model Adı")

for index, value in enumerate(duration_df["duration_sec"]):
    plt.text(value + 1, index, f"{value:.1f} sn", va="center", fontweight="bold")

plt.tight_layout()
plt.savefig("05_toplam_sure_karsilastirma.png", dpi=300)
plt.close()
print("✓ 05_toplam_sure_karsilastirma.png oluşturuldu.")

print("\n🎉 Tüm yeni analiz grafikleri başarıyla üretildi!")