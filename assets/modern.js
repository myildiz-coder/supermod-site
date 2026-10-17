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
