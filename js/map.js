
(function(){
const DATA=window.PTA_BOARD_RESPONSE_INDEX||{};
const minLat=30.8,maxLat=41.8,minLng=129.5,maxLng=142.5;
const esc=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function region(lat,lng){if(lat>=40.2)return '北海道・北東北'; if(lat>=37.0)return '東北・北陸'; if(lat>=35.1&&lng>=138.5)return '関東'; if(lat>=34.2&&lng>=136.0&&lng<138.9)return '中部・東海'; if(lat>=34.0&&lng>=134.0&&lng<136.2)return '近畿'; if(lng<134.0&&lat>=32.0)return '中国・四国・九州'; return 'その他';}
function typeLabel(k){return DATA.typeMap?.[k]?.label||k}
function show(m){const info=document.getElementById('mapInfo'); if(!info)return; info.innerHTML=`<h3>${esc(m.municipality)}</h3><small>類型：${(m.types||[]).map(typeLabel).map(esc).join(' / ')}｜本文 ${esc(m.detailCount||0)}件</small><p>${esc((m.firstBody||'本文は回答DBで確認してください。').slice(0,360))}${(m.firstBody||'').length>360?'…':''}</p><div class="btns"><a class="btn-primary" href="responses.html?q=${encodeURIComponent(m.municipality)}">回答DBで開く</a></div>`}
function renderMap(){const map=document.getElementById('japanMap'); if(!map)return; const items=(DATA.municipalities||[]).filter(m=>Array.isArray(m.coordinates)); map.innerHTML=''; items.forEach((m,i)=>{const [lat,lng]=m.coordinates; const x=(lng-minLng)/(maxLng-minLng)*82+7; const y=(maxLat-lat)/(maxLat-minLat)*88+5; const b=document.createElement('button'); b.className='marker'; b.style.left=x+'%'; b.style.top=y+'%'; b.dataset.types=(m.types||[]).join(','); b.title=m.municipality; b.addEventListener('click',()=>show(m)); map.appendChild(b)}); if(items[0])show(items[0]);}
function renderRegions(){const box=document.getElementById('regionList'); if(!box)return; const counts={}; (DATA.municipalities||[]).forEach(m=>{if(!Array.isArray(m.coordinates))return; const [lat,lng]=m.coordinates; const r=region(lat,lng); counts[r]=(counts[r]||0)+1}); box.innerHTML=Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([r,n])=>`<div class="region-row"><span>${esc(r)}</span><b>${n}</b></div>`).join('')}
function renderTypeMini(){const box=document.getElementById('typeMini'); if(!box)return; box.innerHTML=Object.entries(DATA.typeMap||{}).filter(([k])=>(DATA.typeCounts?.[k]||0)>0).map(([k,v])=>`<div class="region-row"><span>${esc(v.label)}</span><b>${esc(DATA.typeCounts?.[k]||0)}</b></div>`).join('')}
document.addEventListener('DOMContentLoaded',()=>{renderMap();renderRegions();renderTypeMini()});
})();
