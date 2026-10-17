"""Check generated prices, product information, SEO and local references."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, parse_qs
import json, re

ROOT=Path(__file__).resolve().parent.parent
errors=[]
class References(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('href','src','data-src') and value and value.startswith('/'):
                target=ROOT/urlsplit(value).path.lstrip('/')
                if target.is_dir():target=target/'index.html'
                if not target.exists():errors.append(f'Missing reference: {target.relative_to(ROOT)}')

products=json.loads((ROOT/'products.json').read_text(encoding='utf-8'))['products']
catalog=json.loads((ROOT/'assets/catalog.json').read_text(encoding='utf-8'))
assert len(catalog)==len(products)
for item,p in zip(catalog,products):
    assert item['slug']==p['slug']
    assert item['totalCents']==round(p['price']*120)
    assert item['url']=='/urun/'+p['slug']+'/'
for file in ROOT.rglob('index.html'):
    text=file.read_text(encoding='utf-8')
    References().feed(text)
    if 'http-equiv="refresh"' in text:
        continue  # Retain legacy redirect pages, including their noindex tags.
    assert len(re.findall(r'<h1\b',text))==1, f'{file}: expected one main heading'
    assert 'noindex' not in text, f'{file}: preview indexing restriction'
    assert '<link rel="canonical"' in text, f'{file}: canonical missing'
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):
        json.loads(raw)

for p in products:
    file=ROOT/'urun'/p['slug']/'index.html'
    text=file.read_text(encoding='utf-8')
    total=f"{p['price']*1.2:.2f}"
    schemas=[json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)]
    product=next(s for s in schemas if s.get('@type')=='Product')
    assert product['offers']['price']==total, f'{p["slug"]}: schema price mismatch'
    assert f'property="product:price:amount" content="{total}"' in text
    assert '/assets/modern.css?v=' in text
    assert '/assets/modern.js?v=' in text
    assert f'data-select="{p["slug"]}"' in text
    assert text.count('id="selection-title"')==1
    for href in re.findall(r'href="(https://wa.me/[^\"]*)"',text):
        if '?text=' not in href:continue
        message=parse_qs(urlsplit(href).query)['text'][0]
        assert 'KDV dahil' in message and p['slug'] in message
    assert 'KDV dahil ürün fiyatı' in text

for route,count in [('urunler',25),('1-64-diecast-model-araba',23),('1-18-model-araba',1),('maket-kamyon-tir',2)]:
    actual=(ROOT/route/'index.html').read_text(encoding='utf-8').count('<article class="product-card"')
    assert actual==count, f'{route}: expected {count}, got {actual}'
assert not errors,'\n'.join(errors)
print(f'PASS: {len(products)} products; prices, WhatsApp messages, SEO, category counts and local references.')
