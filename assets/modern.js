const grid=document.querySelector('.collection .product-grid');
if(grid){
 const form=document.querySelector('.filters'),query=document.querySelector('#query'),brand=document.querySelector('#brand'),budget=document.querySelector('#budget'),sort=document.querySelector('#sort'),more=document.querySelector('#show-all');
 let expanded=document.querySelector('.collection').dataset.expanded==='true';
 const normalize=s=>s.toLocaleLowerCase('tr-TR').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ı/g,'i');
 function expand(){if(expanded)return;grid.append(document.querySelector('#remaining-products').content.cloneNode(true));expanded=true;more.hidden=true;}
 function filter(){
  if(query.value||brand.value||budget.value||sort.value!=='default')expand();
  const cards=[...grid.children];cards.forEach((c,i)=>{if(!c.dataset.position)c.dataset.position=i+1;c.hidden=!(normalize(c.dataset.search).includes(normalize(query.value.trim()))&&(!brand.value||c.dataset.brand===brand.value)&&(!budget.value||Number(c.dataset.total)<=Number(budget.value)));});
  cards.sort((a,b)=>sort.value==='default'?a.dataset.position-b.dataset.position:sort.value==='asc'?a.dataset.total-b.dataset.total:b.dataset.total-a.dataset.total).forEach(c=>grid.append(c));
  const count=cards.filter(c=>!c.hidden).length;document.querySelector('.result-count').textContent=`${count} model gösteriliyor${expanded?'':' · Daha fazlasını aşağıdan keşfedin'}`;document.querySelector('.empty').hidden=count!==0;
 }
 form.addEventListener('submit',e=>e.preventDefault());form.addEventListener('input',filter);form.addEventListener('change',filter);more.addEventListener('click',()=>{expand();filter()});document.querySelector('.reset').addEventListener('click',()=>{form.reset();filter();query.focus()});filter();
}
document.querySelectorAll('.thumbnail').forEach(button=>button.addEventListener('click',()=>{document.querySelector('#gallery-main').src=button.dataset.src;document.querySelectorAll('.thumbnail').forEach(b=>{b.classList.toggle('selected',b===button);b.setAttribute('aria-pressed',b===button?'true':'false')})}));

// Only product IDs remain in local storage. Prices always come from the current catalog.
(async function selectionList(){
 const dialog=document.querySelector('.selection-dialog');
 if(!dialog)return;
 const storageKey='supermod-selection-v1',limit=6;
 const openButton=document.querySelector('.selection-open'),closeButton=dialog.querySelector('.selection-close');
 const items=dialog.querySelector('.selection-items'),summary=dialog.querySelector('.selection-summary');
 const toast=document.querySelector('.selection-toast'),storageNote=dialog.querySelector('.selection-storage');
 let catalog,selected=[],persistent=true,timer;
 const format=cents=>new Intl.NumberFormat('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2}).format(cents/100)+' TL';
 try{
  const response=await fetch('/assets/catalog.json',{cache:'no-store',signal:AbortSignal.timeout(8000)});
  if(!response.ok)throw new Error('Catalog unavailable');
  const values=await response.json();
  if(!Array.isArray(values))return;
  catalog=new Map(values.filter(p=>p&&typeof p.slug==='string'&&typeof p.name==='string'&&Number.isSafeInteger(p.totalCents)&&p.totalCents>=0&&p.url==='/urun/'+p.slug+'/'&&/^\/img\//.test(p.image)).map(p=>[p.slug,p]));
 }catch{return;} // The existing catalog and direct WhatsApp ordering remain available.
 const normalize=value=>Array.isArray(value)?[...new Set(value.filter(id=>typeof id==='string'&&catalog.has(id)))].slice(0,limit):[];
 try{const saved=localStorage.getItem(storageKey);try{selected=normalize(JSON.parse(saved||'[]'));}catch{selected=[];}}catch{persistent=false;}
 function notify(message){clearTimeout(timer);toast.textContent=message;toast.classList.add('visible');timer=setTimeout(()=>toast.classList.remove('visible'),3500);}
 function save(){
  try{localStorage.setItem(storageKey,JSON.stringify(selected));persistent=true;}catch{persistent=false;}
  storageNote.textContent=persistent?'Listeniz bu tarayıcıda saklanır.':'Tarayıcı kaydı kapalı. Listeniz yalnızca bu sayfa açıkken korunur.';
 }
 function updateButtons(){
  document.querySelectorAll('[data-select]').forEach(button=>{
   const p=catalog.get(button.dataset.select);if(!p)return;
   const active=selected.includes(p.slug);
   button.setAttribute('aria-pressed',String(active));
   button.setAttribute('aria-label',p.name+(active?' modelini listeden çıkar':' modelini listeye ekle'));
   button.textContent=active?'Listede ✓':'Listeye ekle +';
  });
  document.querySelectorAll('.selection-count').forEach(counter=>counter.textContent=selected.length);
  openButton.setAttribute('aria-label','Seçtiğim modeller, '+selected.length+' model');
 }
 function element(tag,className,text){const node=document.createElement(tag);node.className=className;if(text!==undefined)node.textContent=text;return node;}
 function render(){
  items.replaceChildren();let total=0;
  selected.forEach(id=>{
   const p=catalog.get(id);total+=p.totalCents;
   const row=element('div','selection-row'),image=element('img','');image.src=p.image;image.alt='';image.width=76;image.height=76;
   const info=element('div','selection-info'),link=element('a','',p.name);link.href=p.url;
   info.append(link,element('strong','',format(p.totalCents)));
   const remove=element('button','selection-remove','Çıkar');remove.type='button';remove.dataset.remove=id;remove.setAttribute('aria-label',p.name+' modelini listeden çıkar');
   row.append(image,info,remove);items.append(row);
  });
  dialog.querySelector('.selection-empty').hidden=selected.length!==0;summary.hidden=selected.length===0;
  summary.querySelector('.selection-total strong').textContent=format(total);
  const lines=selected.map((id,i)=>{const p=catalog.get(id);return `${i+1}. ${p.name} — ${format(p.totalCents)}\nhttps://supermod.com.tr${p.url}`;});
  const message='Merhaba, aşağıdaki modellerle ilgileniyorum (her birinden 1 adet):\n\n'+lines.join('\n\n')+'\n\nSitedeki KDV dahil ürün toplamı: '+format(total)+'. Kargo hariçtir. Güncel stok, fiyat, ödeme ve teslimat seçeneklerini öğrenmek istiyorum.';
  const send=dialog.querySelector('.selection-send');
  if(selected.length)send.href='https://wa.me/905301100520?text='+encodeURIComponent(message);else send.removeAttribute('href');
  storageNote.textContent=persistent?'Listeniz bu tarayıcıda saklanır.':'Tarayıcı kaydı kapalı. Listeniz yalnızca bu sayfa açıkken korunur.';
  updateButtons();
 }
 document.documentElement.classList.add('selection-ready');openButton.hidden=false;render();
 if(grid)new MutationObserver(updateButtons).observe(grid,{childList:true});
 document.addEventListener('click',event=>{
  const button=event.target.closest('[data-select]');if(!button)return;
  const id=button.dataset.select;if(!catalog.has(id))return;
  if(selected.includes(id)){selected=selected.filter(value=>value!==id);notify('Model listenizden çıkarıldı.');}
  else if(selected.length>=limit){notify('Listenize en fazla 6 model ekleyebilirsiniz. Önce bir modeli çıkarın.');return;}
  else{selected.push(id);notify('Model listenize eklendi. Üstteki Listem düğmesinden görebilirsiniz.');}
  save();render();
 });
 openButton.addEventListener('click',()=>{render();dialog.showModal();closeButton.focus();});
 closeButton.addEventListener('click',()=>dialog.close());
 items.addEventListener('click',event=>{
  const button=event.target.closest('[data-remove]');if(!button)return;
  selected=selected.filter(id=>id!==button.dataset.remove);save();render();
  (items.querySelector('button')||closeButton).focus();
 });
 window.addEventListener('storage',event=>{if(event.key!==storageKey)return;try{selected=normalize(JSON.parse(event.newValue||'[]'));render();}catch{/* Ignore malformed data from another tab. */}});
})();
