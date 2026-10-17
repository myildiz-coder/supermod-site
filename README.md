# Süpermod

Statik mağaza sitesi. `main` dalı GitHub Pages üzerinden yayınlanır; alan adı `CNAME` dosyasında tutulur.

## Ürün güncelleme

Ürünlerin kaynağı `products.json` dosyasıdır. Mevcut veri sözleşmesinde `price` KDV hariç tutardır; arayüz mevcut %20 hesabıyla KDV dahil ürün fiyatını gösterir. Kargo ayrıca belirtilir.

Ürünleri veya `tools/build.py` içindeki sayfa şablonlarını değiştirdikten sonra:

```sh
python tools/build.py
python tools/check.py
node --check assets/modern.js
python -m http.server 8765
```

Üretilen HTML dosyalarını da commit edin. Derleyici, mevcut sayfalardaki canonical, sosyal paylaşım görselleri ve JSON-LD verilerini korur; ürün fiyatlarını günceller. Bir ürün sayfasını ilk kez eklerken aynı yapıda SEO başlığı ve Product/Breadcrumb şemaları içeren bir sayfa oluşturun; ardından derleyiciyi çalıştırın.

Kategoriler ürün verisi ve teknik özelliklerden üretilir. Kontrol komutundaki kategori sayıları mevcut katalog için bir regresyon kontrolüdür; katalog değişince beklenen sayıları güncelleyin.

## Arayüz

- `assets/modern.css`: responsive düzen, renkler ve tipografi.
- `assets/modern.js`: katalog arama/filtre/sıralama ve ürün galerisi.
- WhatsApp düğmeleri yalnızca ürün bilgilerini içeren mesaj bağlantısı açar; kendiliğinden mesaj göndermez.
- “Listem” en fazla 6 farklı modeli bir WhatsApp bilgi talebinde birleştirir. Her model bir adet kabul edilir; stok ayırmaz. Tarayıcıda yalnızca ürün kimlikleri saklanır, fiyatlar güncel `assets/catalog.json` dosyasından alınır. Depolama kapalıysa liste yalnızca sayfa açıkken korunur.
- CSS ve JavaScript bağlantıları içerik özetiyle sürümlenir; yeni yayında eski tarayıcı önbelleğinin tasarımı karıştırması önlenir.
- Yasal sayfaların mevcut taslak metinleri korunur.
- Ziyaretçi takip kodu veya harici yazı tipi eklenmez.

Mobil yerleşim tarayıcıda 390 piksel genişlikte kontrol edilmiştir; fiziksel cihaz testi ayrıca yapılabilir.
