import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Uyarıları tamamen kapatıyoruz
warnings.filterwarnings('ignore')

print("1. Adım: Belediye Şikayet Veri Tabanı Oluşturuluyor...")
# Bellekte geçici SQL veri tabanı açıyoruz
conn = sqlite3.connect(':memory:')

# 200 adet şikayet kaydı simüle edelim
np.random.seed(10)
ilceler = ['Kadikoy', 'Besiktas', 'Uskudar', 'Fatih', 'Pendik', 'Umraniye']
kategoriler = ['Ulasim', 'Cevre ve Parklar', 'Altyapi/Yol', 'Imar', 'Sosyal Yardim']

sikayet_data = pd.DataFrame({
    'sikayet_id': range(5001, 5201),
    'ilce': np.random.choice(ilceler, size=200),
    'kategori': np.random.choice(kategoriler, size=200, p=[0.35, 0.20, 0.25, 0.10, 0.10]),
    'cozum_suresi_gun': np.random.randint(1, 15, size=200),
    'vatandas_memnuniyeti_10': np.random.randint(1, 11, size=200)
})

# Veriyi SQL tablosuna aktaralım
sikayet_data.to_sql('municipal_complaints', conn, index=False, if_exists='replace')

print("\n2. Adım: SQL ile İlçe Bazlı Yoğunluk ve Memnuniyet Sorgusu Çalıştırılıyor...")
# Belediyenin performansını ilçelere göre özetleyen SQL sorgusu
sql_query = """
SELECT 
    ilce,
    COUNT(sikayet_id) AS toplam_sikayet,
    ROUND(AVG(cozum_suresi_gun), 1) AS ortalama_cozum_suresi,
    ROUND(AVG(vatandas_memnuniyeti_10), 1) AS ortalama_memnuniyet
FROM municipal_complaints
GROUP BY ilce
ORDER BY toplam_sikayet DESC;
"""

df_belediye = pd.read_sql_query(sql_query, conn)
print("\n--- SQL Sorgu Sonucu (İlçe Bazlı Özet) ---")
print(df_belediye)

print("\n3. Adım: Kategorilere Göre Şikayet Dağılımı Grafiği Çiziliyor...")
# Şikayet kategorilerinin sayısal dağılımını çekelim
kategori_counts = sikayet_data['kategori'].value_counts().reset_index()
kategori_counts.columns = ['Kategori', 'Sikayet_Sayisi']

# Grafik oluşturma
plt.figure(figsize=(10, 5))
sns.barplot(
    data=kategori_counts,
    y='Kategori',
    x='Sikayet_Sayisi',
    hue='Kategori',
    palette='magma',
    legend=False
)

plt.title('Belediye Beyaz Masa Şikayet Kategorileri Dağılımı')
plt.xlabel('Toplam Başvuru Sayısı')
plt.ylabel('Başvuru Kategorisi')
plt.grid(axis='x', linestyle='--', alpha=0.5)

# Grafiği kaydet
plt.savefig('belediye_sikayet_analizi_grafik.png', dpi=300, bbox_inches='tight')
print("\n[BAŞARILI] Grafik 'belediye_sikayet_analizi_grafik.png' adıyla klasörünüze kaydedildi!")

conn.close()