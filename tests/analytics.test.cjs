const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('analytics.js','utf8');
const id = 'G-R5G70KHYDN';
const key = 'anissafeby_analytics_consent';
function runtime({saved=null,referrer='https://www.google.com/search?q=PRIVATE#PRIVATE',blocked=false,hostname='anissafeby.com'}={}) {
  const values = new Map(saved ? [[key,typeof saved==='string'?saved:JSON.stringify(saved)]] : []);
  const nodes = Object.fromEntries(['analytics-status','analytics-preferences','analytics-allow','analytics-deny'].map(id=>[id,{textContent:'',open:false,handlers:{},addEventListener(n,h){this.handlers[n]=h;}}]));
  const scripts = [], deletes = [], winHandlers = {}, docHandlers = {}, timers = [];
  let reloads=0;
  const document={referrer,hidden:false,getElementById:id=>nodes[id],createElement:()=>({}),head:{appendChild:s=>scripts.push(s)},addEventListener:(n,h)=>docHandlers[n]=h};
  Object.defineProperty(document,'cookie',{get:()=> '_ga=FAKE; _ga_TEST=FAKE; essential=keep',set:v=>deletes.push(v)});
  const window={addEventListener:(n,h)=>winHandlers[n]=h};
  const context={window,document,location:{hostname,origin:'https://'+hostname,href:'https://'+hostname+'/?contact=PRIVATE#PRIVATE',reload:()=>reloads++},localStorage:{getItem:k=>{if(blocked)throw Error('blocked');return values.get(k)||null},setItem:(k,v)=>{if(blocked)throw Error('blocked');values.set(k,v)}},URL,Date,Set,Number,JSON,setTimeout:(h,ms)=>{timers.push({h,ms});return timers.length},clearTimeout:()=>{}};
  vm.runInNewContext(source,context);
  const records=()=>Array.from(window.dataLayer||[],entry=>Array.from(entry));
  return{window,nodes,scripts,deletes,values,winHandlers,docHandlers,timers,records,reloads:()=>reloads,click:id=>nodes[id].handlers.click()};
}
const future=()=>Date.now()+100000;
test('unknown, declined, expired, malformed, or unavailable consent never loads Google',()=>{
  for(const opts of [{},{saved:{value:'denied',expires:future()}},{saved:{value:'granted',expires:1}},{saved:'invalid'},{blocked:true}]){
    const r=runtime(opts);assert.equal(r.scripts.length,0);assert.equal(r.window['ga-disable-'+id],true);assert.equal(r.records().filter(x=>x[0]==='event').length,0);
  }
});
test('Google origin reaches one page_view only after explicit opt-in, with no private query or ads',()=>{
  const r=runtime();r.click('analytics-allow');r.winHandlers.focus();
  assert.equal(r.scripts.length,1);assert.equal(r.scripts[0].src,'https://www.googletagmanager.com/gtag/js?id='+id);
  const all=r.records(),config=all.find(x=>x[0]==='config'),events=all.filter(x=>x[0]==='event');
  assert.equal(events.length,1);assert.equal(events[0][1],'page_view');assert.equal(events[0][2].page_referrer,'https://www.google.com/');assert.equal(events[0][2].page_location,'https://anissafeby.com/');
  assert.equal('ignore_referrer' in config[2],false);assert.equal(config[2].send_page_view,false);assert.equal(config[2].allow_google_signals,false);assert.equal(config[2].allow_ad_personalization_signals,false);
  assert.equal(/PRIVATE|contact=|search\?/.test(JSON.stringify(all)),false);
  for(const x of all.filter(x=>x[0]==='consent')) for(const k of ['ad_storage','ad_user_data','ad_personalization'])assert.equal(x[2][k],'denied');
  assert.equal(JSON.parse(r.values.get(key)).value,'granted');assert(r.timers.some(t=>t.ms>0));
});
test('withdrawal disables collection, removes only GA cookies, and reloads loaded tag',()=>{
  const r=runtime();r.click('analytics-allow');r.click('analytics-deny');
  assert.equal(r.window['ga-disable-'+id],true);assert.equal(r.reloads(),1);assert.equal(JSON.parse(r.values.get(key)).value,'denied');
  assert(r.deletes.some(x=>x.startsWith('_ga=')));assert(r.deletes.some(x=>x.startsWith('_ga_TEST=')));assert(r.deletes.every(x=>!x.startsWith('essential=')));
  assert.equal(r.records().filter(x=>x[0]==='event').length,1);
  assert.equal(r.records().filter(x=>x[0]==='consent').at(-1)[2].analytics_storage,'denied');
});
test('cross-tab removal of consent withdraws collection',()=>{
  const r=runtime({saved:{value:'granted',expires:future()}});r.values.delete(key);r.winHandlers.storage({key});
  assert.equal(r.window['ga-disable-'+id],true);assert.equal(r.reloads(),1);
});
test('expiry while the page is open withdraws collection',()=>{const r=runtime({saved:{value:'granted',expires:future()}});r.values.set(key,JSON.stringify({value:'granted',expires:1}));r.timers.at(-1).h();assert.equal(r.window['ga-disable-'+id],true);assert.equal(r.reloads(),1);});
test('external origins are retained and internal, malformed, unsafe or credentialed referrers excluded',()=>{
  const cases=[['https://www.google.co.uk/search?q=PRIVATE','https://www.google.co.uk/'],['https://www.bing.com/search?q=PRIVATE','https://www.bing.com/'],['https://anissafeby.com/private?token=PRIVATE',''],['https://www.anissafeby.com/private',''],['https://user:secret@www.google.com/',''],['javascript:alert(1)',''],['bad-url',''],['','']];
  for(const [referrer,expected]of cases){const r=runtime({referrer,saved:{value:'granted',expires:future()}});assert.equal(r.records().find(x=>x[0]==='event')[2].page_referrer,expected,referrer);}
});
test('no collection on preview or unrelated host',()=>{const r=runtime({hostname:'localhost',saved:{value:'granted',expires:future()}});assert.equal(r.scripts.length,0);assert.equal(r.records().length,0)});
test('HTML loads only local adapter and supplies accessible consent controls',()=>{
  const html=fs.readFileSync('index.html','utf8');assert.match(html,/<script defer src="\/analytics.js"><\/script>/);assert(!html.includes('googletagmanager.com'));assert.match(html,/id="analytics-status" role="status"/);assert.match(html,/id="analytics-allow"/);assert.match(html,/id="analytics-deny"/);
});
