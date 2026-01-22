# Müşteri Yaşam Boyu Değeri (CLTV) Tahmini

Bu proje, BG-NBD ve Gamma-Gamma modellerini kullanarak müşterilerin gelecekteki satın alma davranışlarını ve şirkete bırakacakları toplam parasal değeri tahmin etmektedir.

## 🚀 Proje Özeti
- **Veri Seti:** İngiltere merkezli bir perakende şirketinin 2010-2011 satış verileri.
- **Modelleme:** BG-NBD (İşlem Tahmini) & Gamma-Gamma (Kâr Tahmini).
- **Segmentasyon:** Müşteriler CLTV değerlerine göre 4 gruba (A, B, C, D) ayrıldı.

## 📊 Öne Çıkan Çıktılar
- Müşterilerin 3 ve 6 aylık gelecek satın alma projeksiyonları oluşturuldu.
- En değerli segmentte yer alan (A) ancak terk etme riski taşıyan (Churn Risk) müşteriler tespit edildi.
- Segment bazlı stratejik aksiyon planları hazırlandı.

## 💻 Gereksinimler
`pip install lifetimes pandas matplotlib seaborn`