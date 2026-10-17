"""Rebuild the static storefront from products.json. Run: python tools/build.py."""
from pathlib import Path
import json, re, html, hashlib
from urllib.parse import quote

src=Path(__file__).resolve().parent.parent
out=src
asset_versions={name:hashlib.sha256((src/'assets'/name).read_bytes()).hexdigest()[:12] for name in ['modern.css','modern.js']}
originals={}
for path in src.rglob('index.html'):
    route='/' if path.parent==src else '/'+path.parent.relative_to(src).as_posix()+'/'
    originals[route]=path.read_text(encoding='utf-8')
products=json.loads((src/'products.json').read_text(encoding='utf-8'))['products']
esc=lambda s:html.escape(str(s),quote=True)
money=lambda n: f'{n:,.2f}'.replace(',','X').replace('.',',').replace('X','.')+' TL'
def short(p):
 return re.sub(r'\s*\(1:64\)|\s*\(1:18\)','',p['title'].replace('Diecast Model Araba ','')).strip()
def url(p): return '/urun/'+p['slug']+'/'
def wa(p):
 msg=f"Merhaba, {short(p)} ile ilgileniyorum. Sitedeki KDV dahil ürün fiyatı: {money(p['price']*1.2)}. Güncel stok ve kargo bedelini öğrenip sipariş vermek istiyorum. https://supermod.com.tr{url(p)}"
 return 'https://wa.me/905301100520?text='+quote(msg)
header='''<a class="skip" href="#main">İçeriğe geç</a><div class="announcement">Koleksiyonunuzu yakından tanıyın. <span>Ataşehir mağaza · Takipli kargo</span></div><header class="mast"><div class="wrap nav"><a href="/" aria-label="Süpermod ana sayfa"><img class="logo" src="/assets/logo-header.png" alt="Süpermod" width="176" height="40"></a><nav aria-label="Ana menü"><a href="/#koleksiyon">Koleksiyonu keşfet</a><a href="/urunler/">Tüm modeller</a><a href="/hakkimizda/">Mağaza & iletişim</a></nav><button class="selection-open" type="button" aria-haspopup="dialog" hidden>Listem <span class="selection-count">0</span></button><a class="nav-contact" href="https://wa.me/905301100520" target="_blank" rel="noopener">Bize ulaşın ↗</a></div></header>'''
footer='''<footer class="footer"><div class="wrap footer-grid"><div><img src="/assets/logo-header.png" alt="Süpermod" width="176" height="40"><p>Küçük ölçekte büyük tutkular.<br>Ataşehir'den koleksiyonunuza.</p></div><div><h3>Mağazamız</h3><p>Ferhatpaşa Mah. Yeditepe Cad. No:32/B<br>Ataşehir / İstanbul</p><a href="/hakkimizda/">Mağazayı keşfet ↗</a></div><div><h3>İletişim</h3><a href="tel:+905301100520">0530 110 05 20</a><a href="https://www.instagram.com/supermodcomtr/" target="_blank" rel="noopener">Instagram ↗</a><a href="/kvkk/">Gizlilik (mevcut taslak)</a><a href="/mesafeli-satis/">Mesafeli satış (mevcut taslak)</a></div></div><div class="wrap copyright">© 2026 Süpermod · SONORA Teknoloji Market & Servis</div></footer>'''
def selection_button(p):
 return '<button class="list-button" type="button" data-select="'+esc(p['slug'])+'" aria-pressed="false" aria-label="'+esc(short(p))+' modelini listeye ekle">Listeye ekle +</button>'

def card(p):
 return f'''<article class="product-card" data-brand="{esc(p['brand'])}" data-total="{p['price']*1.2:.2f}" data-search="{esc(p['title'])}"><a class="product-image" href="{url(p)}"><img src="{esc(p['images'][0]['thumb'])}" alt="{esc(short(p))}" width="600" height="600" loading="lazy"><span class="image-arrow" aria-hidden="true">↗</span></a><div class="product-meta">{esc(p['brand'])}</div><h3><a href="{url(p)}">{esc(short(p))}</a></h3><div class="card-bottom"><div><strong>{money(p['price']*1.2)}</strong><small>KDV dahil · Kargo ayrıca</small></div><a class="card-link" href="{url(p)}" aria-label="{esc(short(p))} detayları">İncele →</a></div>{selection_button(p)}</article>'''

selection_dialog='''<dialog class="selection-dialog" aria-labelledby="selection-title"><div class="selection-heading"><div><p class="eyebrow">KOLEKSİYONUNUZUN SONRAKİ PARÇALARI</p><h2 id="selection-title">Seçtiğim modeller</h2></div><button type="button" class="selection-close" aria-label="Listeyi kapat">×</button></div><p class="selection-help">En fazla 6 modeli tek mesajda sorun. Listeye eklemek stok ayırmaz.</p><div class="selection-items"></div><p class="selection-empty">Listeniz henüz boş. Beğendiğiniz modellerde “Listeye ekle” düğmesine dokunun.</p><div class="selection-summary" hidden><div class="selection-total"><span>KDV dahil ürün toplamı</span><strong></strong></div><p>Kargo ayrıca. Güncel stok, fiyat ve teslimat WhatsApp üzerinden teyit edilir.</p><a class="button accent selection-send" target="_blank" rel="noopener">Listeyi WhatsApp'ta sor ↗</a></div><p class="selection-storage">Listeniz bu tarayıcıda saklanır.</p><p class="selection-status" role="status" aria-live="polite"></p></dialog><div class="selection-toast" role="status" aria-live="polite"></div>'''

def page(title,body,canonical='/'):
    # Preserve canonical, social images and structured data from existing pages.
    old=originals.get(canonical,originals['/'])
    head=re.search(r'<head>(.*?)</head>',old,re.S).group(1)
    head=re.sub(r'<title>.*?</title>','<title>'+esc(title)+'</title>',head,flags=re.S)
    head=re.sub(r'<meta (?:property="og:title"|name="twitter:title") content="[^"]*">',lambda m: re.sub(r'content="[^"]*"','content="'+esc(title)+'"',m.group()),head)
    head=re.sub(r'<meta name="robots" content="[^"]*">','',head)
    head=head.replace('/assets/style.css','/assets/modern.css')
    if '/assets/modern.js' not in head:
        head+='<script src="/assets/modern.js" defer></script>'
    for name,version in asset_versions.items():
        head=re.sub(r'/assets/'+re.escape(name)+r'(?:\?v=[a-f0-9]+)?', '/assets/'+name+'?v='+version,head)
    product=next((p for p in products if url(p)==canonical),None)
    if product:
        total=format(product['price']*1.2,'.2f')
        description=product['short']+' KDV dahil ürün fiyatı: '+money(product['price']*1.2)+'. Kargo ayrıca; güncel stok için iletişime geçin.'
        head=re.sub(r'<meta (?:name="description"|property="og:description"|name="twitter:description") content="[^"]*">',lambda m: re.sub(r'content="[^"]*"','content="'+esc(description)+'"',m.group()),head)
        head=re.sub(r'<meta property="product:price:amount" content="[^"]*">','<meta property="product:price:amount" content="'+total+'">',head)
        def update_schema(m):
            data=json.loads(m.group(1))
            if data.get('@type')=='Product' and isinstance(data.get('offers'),dict):
                data['offers']['price']=total
                if isinstance(data['offers'].get('priceSpecification'),dict):
                    data['offers']['priceSpecification']['price']=total
            return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'
        head=re.sub(r'<script type="application/ld\+json">(.*?)</script>',update_schema,head,flags=re.S)
    return '<!doctype html><html lang="tr"><head>'+head+'</head><body>'+header+body+footer+selection_dialog+'</body></html>'
hero=next(p for p in products if p['slug']=='dka-084-nissan-skyline-gt-r-r34-chameleon-1-64')
brands=sorted(set(p['brand'] for p in products))
body=f'''<main id="main"><section class="hero-modern"><div class="wrap hero-layout"><div class="hero-copy"><p class="eyebrow">SÜPERMOD / KOLEKSİYON & DIECAST</p><h1>Bir modelden<br>çok daha <em>fazlası.</em></h1><p class="hero-description">İkonik otomobiller, ince detaylar ve koleksiyonunuzda yerini bekleyen modeller. Kendi favorinizi keşfedin.</p><a class="button accent" href="#koleksiyon">Koleksiyonu keşfet <span>↗</span></a><div class="hero-footnote"><span>01 /</span> Küçük ölçekte büyük tutkular.</div></div><a class="hero-art" href="{url(hero)}"><div class="hero-image"><img src="{hero['images'][1]['src']}" alt="{esc(short(hero))}" width="900" height="760" fetchpriority="high"></div><span class="hero-caption"><span><small>VİTRİNDEN BİR MODEL</small><b>Nissan Skyline GT-R R34</b></span><span class="round-arrow">↗</span></span></a></div></section><div class="benefits"><div class="wrap benefit-grid"><div><b>Gerçek ürün fotoğrafları</b><span>Detayları yakından inceleyin</span></div><div><b>Açık kondisyon bilgisi</b><span>Ürün ve kutu durumu açıklamada</span></div><div><b>Mağazadan teslim</b><span>Ataşehir / Ferhatpaşa</span></div><div><b>WhatsApp ile sipariş</b><span>Stok ve teslimatı birlikte netleştirelim</span></div></div></div><section class="wrap collection" id="koleksiyon"><div class="section-head"><div><p class="eyebrow">KOLEKSİYONUNUZUN SONRAKİ PARÇASI</p><h2>Favorinizi bulun.</h2></div><a href="/urunler/">Tüm ürünler ↗</a></div><form class="filters" role="search"><div class="field search-field"><label for="query">Model veya marka ara</label><input id="query" type="search" placeholder="Örn. Ferrari, Skyline, Hot Wheels"></div><div class="field"><label for="brand">Marka</label><select id="brand"><option value="">Tüm markalar</option>{''.join(f'<option>{esc(b)}</option>' for b in brands)}</select></div><div class="field"><label for="budget">KDV dahil bütçe</label><select id="budget"><option value="">Tüm fiyatlar</option><option value="1000">1.000 TL ve altı</option><option value="2500">2.500 TL ve altı</option><option value="5000">5.000 TL ve altı</option></select></div><div class="field"><label for="sort">Sıralama</label><select id="sort"><option value="default">Vitrin sırası</option><option value="asc">Fiyat: Artan</option><option value="desc">Fiyat: Azalan</option></select></div></form><p class="result-count" role="status" aria-live="polite"></p><div class="product-grid">{''.join(card(p) for p in products[:8])}</div><div class="empty" hidden><h3>Bu filtrelerde model bulunamadı.</h3><p>Başka bir model adı deneyin veya filtreleri temizleyin.</p></div><div class="collection-end"><button class="button outline" id="show-all" type="button">Tüm {len(products)} modeli göster ↓</button><button class="reset" type="button">Filtreleri temizle</button></div><template id="remaining-products">{''.join(card(p) for p in products[8:])}</template></section><section class="wrap editorial"><div><p class="eyebrow">YAKINDAN GÖRÜN. DETAYLARI KEŞFEDİN.</p><h2>Ekranda beğenin.<br>Mağazada tanışın.</h2></div><div><p>Koleksiyon modelinizi Ataşehir mağazamızda inceleyebilir, mağazadan teslim alabilir veya takipli kargo seçeneklerini sorabilirsiniz.</p><a class="button dark" href="/hakkimizda/">Mağaza & iletişim ↗</a></div></section><section class="wrap steps"><p class="eyebrow">SİPARİŞ NASIL İLERLİYOR?</p><div class="step-grid"><div><span>01</span><h3>Modelinizi seçin</h3><p>Fotoğrafları, özellikleri ve ürün durumunu inceleyin.</p></div><div><span>02</span><h3>WhatsApp'tan yazın</h3><p>Güncel stok, kargo bedeli ve ödeme seçeneklerini netleştirin.</p></div><div><span>03</span><h3>Teslimatı planlayın</h3><p>Mağazadan teslim veya takipli kargo seçeneğiyle ilerleyin.</p></div></div></section></main>'''
(out/'index.html').write_text(page('Süpermod — Küçük ölçekte büyük tutkular',body),encoding='utf-8')
for p in products:
 specs=dict(p['specs'])
 name=specs.get('Model',specs.get('Araç',short(p)))
 related=[x for x in products if x['slug']!=p['slug']][:4]
 body=f'''<main id="main" class="wrap detail-main"><nav class="breadcrumbs" aria-label="Sayfa yolu"><a href="/">Ana sayfa</a><span>/</span><a href="/urunler/">Koleksiyon</a><span>/</span><span>{esc(name)}</span></nav><div class="detail-layout"><section class="gallery" aria-label="Ürün fotoğrafları"><div class="gallery-main"><img id="gallery-main" src="{p['images'][0]['src']}" alt="{esc(short(p))}" width="1000" height="1000" fetchpriority="high"></div><div class="thumbnails">{''.join(f'<button type="button" class="thumbnail {"selected" if i==0 else ""}" data-src="{im["src"]}" aria-label="Ürün fotoğrafı {i+1}" aria-pressed="{"true" if i==0 else "false"}"><img src="{im["thumb"]}" alt="" width="80" height="80"></button>' for i,im in enumerate(p['images']))}</div><p class="photo-note">Ürünün kendi fotoğrafları.</p></section><section class="detail-copy"><p class="eyebrow">{esc(p['brand'])} / {esc(specs.get('Ölçek','Koleksiyon'))}</p><h1>{esc(name)}</h1><p class="detail-subtitle">{esc(short(p))}</p><p class="detail-intro">{esc(p['short'])}</p><div class="detail-price"><strong>{money(p['price']*1.2)}</strong><span>KDV dahil ürün fiyatı</span><small>Kargo bedeli ve güncel stok sipariş öncesinde netleştirilir.</small></div><a class="button accent order-button" href="{wa(p)}" target="_blank" rel="noopener">WhatsApp ile sipariş ver <span>↗</span></a>{selection_button(p)}<p class="order-note">Ürün adı ve bağlantısı mesajınıza hazır eklenir.</p><div class="delivery"><div><b>Ürün ve paket durumu</b><span>{esc(specs.get('Durum','Detaylar ürün açıklamasında'))} · {esc(specs.get('Paket','Paket bilgisi için iletişime geçin'))}</span></div><div><b>Ödeme & teslimat</b><span>Havale/EFT, kredi kartı veya link ile ödeme.<br>Ataşehir mağazadan teslim veya takipli kargo.</span></div></div><details open><summary>Ürün özellikleri</summary><dl>{''.join(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k,v in p['specs'])}</dl></details><details open><summary>Model ve kondisyon hakkında</summary>{''.join('<p>'+esc(d)+'</p>' for d in p['description'])}<ul>{''.join('<li>'+esc(f)+'</li>' for f in p['features'])}</ul></details></section></div><section class="related"><div class="section-head"><div><p class="eyebrow">KEŞFETMEYE DEVAM EDİN</p><h2>Vitrinden diğer modeller.</h2></div></div><div class="product-grid">{''.join(card(x) for x in related)}</div></section><div class="mobile-buy"><div><strong>{money(p['price']*1.2)}</strong><small>KDV dahil · Kargo ayrıca</small></div><a class="button accent" href="{wa(p)}" target="_blank" rel="noopener">Sipariş ver ↗</a></div></main>'''
 target=out/url(p).strip('/')/'index.html'
 target.write_text(page(short(p)+' | Süpermod',body,url(p)),encoding='utf-8')

home=(out/'index.html').read_text(encoding='utf-8')
collection=re.search(r'<section class="wrap collection".*?</section>',home).group()
routes={
 'urunler':('Tüm modeller.',products),
 'diecast-model-araba':('Diecast koleksiyonu.',[p for p in products if p['category'].startswith('diecast')]),
 '1-64-diecast-model-araba':('1/64 diecast modeller.',[p for p in products if p['category']=='diecast-1-64']),
 '1-18-model-araba':('1/18 model arabalar.',[p for p in products if dict(p['specs']).get('Ölçek','').startswith('1/18')]),
 'maket-kamyon-tir':('Kamyon & tır modelleri.',[p for p in products if p['brand']=='MASDI']),
 'aksiyon-figur':('Aksiyon figürleri.',[p for p in products if p['category']=='aksiyon-figur'])}
for route,(title,items) in routes.items():
 if not items:
  continue
 section=collection.replace('Favorinizi bulun.',title)
 section=section.replace('<h2>'+title+'</h2>','<h1 class="catalog-title">'+title+'</h1>')
 category_links='<nav class="category-links" aria-label="Koleksiyon kategorileri">'+''.join('<a href="/'+r+'/"'+(' aria-current="page"' if r==route else '')+'>'+label+'</a>' for r,label in [('urunler','Tüm modeller'),('1-64-diecast-model-araba','1/64'),('1-18-model-araba','1/18'),('maket-kamyon-tir','Kamyon & Tır')])+'</nav>'
 section=section.replace('<form class="filters"',category_links+'<form class="filters"')
 section=re.sub(r'<div class="product-grid">.*?</div><div class="empty"',lambda _: '<div class="product-grid">'+''.join(card(p) for p in items)+'</div><div class="empty"',section,flags=re.S)
 section=re.sub(r'<template id="remaining-products">.*?</template>','<template id="remaining-products"></template>',section,flags=re.S)
 section=section.replace('id="show-all"','id="show-all" hidden')
 section=section.replace('class="wrap collection"','class="wrap collection" data-expanded="true"')
 target=out/route/'index.html';target.parent.mkdir(exist_ok=True)
 target.write_text(page(title+' | Süpermod','<main id="main">'+section+'</main>','/'+route+'/'),encoding='utf-8')

map_url='https://www.google.com/maps/search/?api=1&query='+quote('Süpermod Ferhatpaşa Mah. Yeditepe Cad. No:32/B Ataşehir')
about=f'''<main id="main"><section class="store-hero"><div class="wrap"><p class="eyebrow">SÜPERMOD / ATAŞEHİR</p><h1>Koleksiyon tutkusu.<br>Gerçek bir buluşma noktası.</h1><p>Modelinizi yakından inceleyin, detayları keşfedin.<br>Sizi Ataşehir mağazamıza bekliyoruz.</p><a class="button accent" href="{map_url}" target="_blank" rel="noopener">Yol tarifi al ↗</a></div></section><section class="wrap store-grid" id="iletisim"><div><p class="eyebrow">MAĞAZA & İLETİŞİM</p><h2>Bir merhaba ile<br>başlayalım.</h2><p>Koleksiyonluk diecast modelleri mağazamızda inceleyebilir; stok, ödeme ve teslimat için bize ulaşabilirsiniz.</p><h3>Süpermod</h3><p>Ferhatpaşa Mah. Yeditepe Cad. No:32/B<br>Ataşehir / İstanbul</p><a class="button dark" href="{map_url}" target="_blank" rel="noopener">Google Haritalar'da aç ↗</a></div><div class="contact-panel"><h3>Size nasıl yardımcı olabiliriz?</h3><a href="https://wa.me/905301100520" target="_blank" rel="noopener"><b>WhatsApp ↗</b><span>Ürün, stok ve sipariş soruları</span></a><a href="tel:+905301100520"><b>0530 110 05 20 ↗</b><span>Telefonla iletişim</span></a><a href="https://www.instagram.com/supermodcomtr/" target="_blank" rel="noopener"><b>@supermodcomtr ↗</b><span>Instagram'da keşfedin</span></a><p>Yasal unvan: SONORA Teknoloji Market & Servis</p></div></section><section class="wrap faq"><p class="eyebrow">SİPARİŞ ÖNCESİ</p><h2>Merak ettikleriniz.</h2><details open><summary>Nasıl sipariş verebilirim?</summary><p>Ürün sayfasındaki WhatsApp düğmesiyle yazın. Ürün adı, bağlantısı ve KDV dahil fiyat mesaja eklenir. Stok, ödeme ve teslimat seçeneklerini birlikte netleştiririz.</p></details><details><summary>Kargo bedeli fiyata dahil mi?</summary><p>Gösterilen fiyatlar KDV dahil ürün fiyatıdır. Kargo bedeli ayrıca sipariş öncesinde netleştirilir.</p></details><details><summary>Ürünü mağazada inceleyebilir miyim?</summary><p>Evet, ürünleri Ataşehir mağazamızda inceleyebilirsiniz. Gelmeden önce ilgilendiğiniz modelin güncel stok durumunu sorabilirsiniz.</p></details><details><summary>Kutu ve ürün durumunu nerede görebilirim?</summary><p>Her modelin ürün sayfasında fotoğraflar, paket bilgisi ve kondisyon açıklaması bulunur. Kutusuz ürünler ve açıklanmış yıpranmalar ilgili sayfada belirtilir.</p></details></section></main>'''
(out/'hakkimizda/index.html').write_text(page('Mağaza & iletişim | Süpermod Ataşehir',about,'/hakkimizda/'),encoding='utf-8')

# Keep existing legal wording intact while bringing its shell into the same design.
for route in ['kvkk','mesafeli-satis']:
 original=(src/route/'index.html').read_text(encoding='utf-8')
 main=re.search(r'<main.*?</main>',original,re.S).group()
 main=main.replace('<main>','<main id="main" class="legal-main">')
 (out/route/'index.html').write_text(page(('Gizlilik' if route=='kvkk' else 'Mesafeli satış')+' (mevcut taslak) | Süpermod',main,'/'+route+'/'),encoding='utf-8')

# Store only current, public display data for the client-side selection list.
catalog=[dict(slug=p['slug'],name=short(p),totalCents=round(p['price']*120),image=p['images'][0]['thumb'],url=url(p)) for p in products]
(out/'assets/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False),encoding='utf-8')
