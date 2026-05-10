
const AUDITS={
 parent:{label:'保護者',lead:'自分の同意・個人情報・会費負担を確認します。',questions:[
  ['入会意思','入会届・申込フォームなど、自分がPTAへ入会する意思を示した記録がありますか。',[['記録がある',0],['不明',2],['ない／見たことがない',5]]],
  ['会費','PTA会費の請求主体・金額・任意性が学校徴収金とは別に示されていますか。',[['明示されている',0],['一部不明',3],['学校徴収金と一体に見える',5]]],
  ['個人情報','学校が保有する児童・保護者情報をPTAへ提供する同意を取られていますか。',[['同意記録がある',0],['不明',3],['同意なく提供されている可能性',5]]],
  ['非会員','非会員児童に不利益がないことが説明されていますか。',[['説明あり',0],['不明',2],['不利益が示唆される',5]]],
  ['相談導線','学校・教育委員会・PTAのどこに確認すべきか分かりますか。',[['分かる',0],['一部不明',2],['分からない',4]]]
 ]},
 pta:{label:'PTA役員',lead:'役員個人が慣例の責任を背負わないため、団体運営の記録を確認します。',questions:[
  ['会則','会則に入退会手続、会費、会計、役員選出が明記されていますか。',[['明記あり',0],['一部不足',3],['不明／古い',5]]],
  ['入会記録','会員名簿は本人の入会意思確認記録に基づいていますか。',[['基づいている',0],['一部不明',3],['児童名簿等を流用している',5]]],
  ['会計','会計帳簿・領収書・監査記録を会員に説明できる状態ですか。',[['説明できる',0],['一部不足',3],['説明困難',5]]],
  ['学校分離','PTA会費徴収・督促・名簿管理を学校職員へ依存していませんか。',[['依存していない',0],['一部依存',3],['恒常的に依存',5]]],
  ['個人情報','個人情報の取得元・利用目的・保管者・廃棄方法が決まっていますか。',[['決まっている',0],['一部不明',3],['決まっていない',5]]]
 ]},
 school:{label:'学校管理職・教育委員会',lead:'学校の服務、会計、個人情報、指導責任の観点からリスクを確認します。',questions:[
  ['徴収分離','学校徴収金とPTA会費を、主体・口座・説明文書の上で分離していますか。',[['分離している',0],['説明上のみ分離',3],['一括徴収・混在',5]]],
  ['個人情報','学校保有情報をPTAへ提供しない手順、または適法な提供根拠を文書化していますか。',[['文書化済み',0],['学校判断に依存',3],['慣例提供がある',5]]],
  ['職務分離','校務分掌からPTA内部事務を除外し、連絡調整に限定していますか。',[['限定している',0],['一部曖昧',3],['内部事務を含む',5]]],
  ['媒体利用','学校配布物・連絡アプリ・学校HPでPTA加入が学校手続のように見えないよう整理していますか。',[['整理済み',0],['一部曖昧',3],['学校手続のように見える',5]]],
  ['説明責任','開示請求・住民監査請求に対し、根拠文書を提示できる状態ですか。',[['提示できる',0],['一部不足',3],['根拠不明',5]]]
 ]}
};
let profile='parent', index=0, answers={parent:[],pta:[],school:[]};
const esc=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
function setProfile(p){profile=p;index=0;document.querySelectorAll('[data-profile]').forEach(b=>b.classList.toggle('is-active',b.dataset.profile===p));render()}
function render(){const bank=AUDITS[profile], q=bank.questions[index], ans=answers[profile][index];document.getElementById('auditTitle').textContent=bank.label+'向け監査';document.getElementById('auditLead').textContent=bank.lead;document.getElementById('auditAxis').textContent='論点：'+q[0];document.getElementById('auditQuestion').textContent=q[1];const box=document.getElementById('auditChoices');box.innerHTML=q[2].map((c,i)=>`<button class="audit-choice ${ans?.choice===i?'is-selected':''}" data-choice="${i}">${esc(c[0])}</button>`).join('');box.querySelectorAll('button').forEach(b=>b.onclick=()=>{answers[profile][index]={choice:+b.dataset.choice,text:q[2][+b.dataset.choice][0],score:q[2][+b.dataset.choice][1],axis:q[0]};render()});document.getElementById('auditPrev').disabled=index===0;document.getElementById('auditNext').textContent=index===bank.questions.length-1?'結果を見る':'次へ';document.getElementById('auditProgressText').textContent=`${index+1} / ${bank.questions.length}`;updateBar();document.getElementById('auditResult').innerHTML=''}
function updateBar(){const arr=answers[profile];const score=arr.reduce((s,a)=>s+(a?.score||0),0);const pct=Math.min(100,score/(AUDITS[profile].questions.length*5)*100);document.querySelector('.riskbar span').style.width=pct+'%'}
function next(){if(!answers[profile][index]){alert('回答を選択してください。');return} if(index<AUDITS[profile].questions.length-1){index++;render()}else result()}
function result(){const arr=answers[profile], score=arr.reduce((s,a)=>s+(a?.score||0),0);const level=score>=18?'高リスク':score>=9?'中リスク':'低リスク';const advice=level==='高リスク'?'資料の所在確認と運用分離を早急に行う必要があります。':level==='中リスク'?'不明点を原資料で確認し、会則・同意・徴収・職務の記録を整えてください。':'大きな危険信号は少ない状態です。ただし記録保存と定期点検が必要です。';document.getElementById('auditResult').innerHTML=`<div class="result-box"><h3>総合評価：${level}</h3><p><strong>${score}点</strong> ／ ${AUDITS[profile].questions.length*5}点</p><p>${advice}</p><ul>${arr.map(a=>`<li>${esc(a.axis)}：${esc(a.text)}（${a.score}点）</li>`).join('')}</ul><div class="btns"><a class="btn-primary" href="responses.html">回答DBで確認</a><a class="btn" href="evidence.html">必要資料を見る</a></div></div>`}
document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('[data-profile]').forEach(b=>b.onclick=()=>setProfile(b.dataset.profile));document.getElementById('auditPrev').onclick=()=>{if(index>0){index--;render()}};document.getElementById('auditNext').onclick=next;render()});
