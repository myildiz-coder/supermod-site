"""Optional offline interest grouping. Requires TYPESAFE_API_KEY; never runs in the browser."""
from pathlib import Path
import hashlib,json,os
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent.parent
products=json.loads((ROOT/'products.json').read_text(encoding='utf-8'))['products']
state=[{key:p[key] for key in ['slug','title','brand','specs']} for p in products]
criteria={
 'ferrari':'Ferrari road or race car models, regardless of diecast manufacturer.',
 'japanese':'Japanese car models such as Nissan or Toyota. Excludes trucks and construction kits.',
 'german':'German car models such as BMW, Mercedes-Benz and Audi. Excludes trucks and construction kits.',
 'american':'American car models such as Ford, Chevrolet and Mercury.',
 'other_european':'Other European car models such as Lamborghini, Bentley and Koenigsegg; excludes Ferrari and German cars.',
 'truck':'Diecast trucks and tractor units, such as Scania. Excludes LEGO construction sets.',
 'construction':'LEGO and other construction kits, even when depicting a truck.',
 'other':'Not supported by the evidence or none of the above.'}
questions={str(i):{'type':'choice','instructions':f'Assign only `products[{i}]` to the collector interest group that follows from its title and specifications. Choose construction first for LEGO, truck for diecast trucks, then the vehicle marque group. Do not classify by diecast manufacturer nationality.','criteria':criteria} for i in range(len(products))}
key=os.environ.get('TYPESAFE_API_KEY')
if not key:raise SystemExit('TYPESAFE_API_KEY unavailable; existing grouping left intact.')
payload=json.dumps({'model':'jev-latest','state':{'products':state},'questions':questions}).encode()
request=Request('https://api.typesafe.ai/v1/systemone',data=payload,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
with urlopen(request,timeout=60) as response:result=json.load(response)
groups={}
for i,p in enumerate(products):
 answer=result['answers'][str(i)]
 assert answer['choice'] in criteria
 fingerprint=hashlib.sha256(json.dumps(state[i],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
 groups[p['slug']]={'group':answer['choice'],'confidence':answer['confidence'],'source_sha256':fingerprint}
 print(answer['choice'],round(answer['confidence'],3),p['slug'])
(ROOT/'tools/related-groups.json').write_text(json.dumps({'model':result['model'],'products':groups},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
