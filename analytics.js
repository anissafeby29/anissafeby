/* Basic opt-in Analytics. Search strings, contact data and referring paths are excluded. */
(() => {
  'use strict';
  if (!['anissafeby.com', 'www.anissafeby.com'].includes(location.hostname)) return;
  const id = 'G-R5G70KHYDN';
  const key = 'anissafeby_analytics_consent';
  const lifetime = 180 * 86400000;
  const denied = {analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'};
  const status = document.getElementById('analytics-status');
  const controls = document.getElementById('analytics-preferences');
  let loaded = false, choice = null, storageAvailable = true, expiryTimer;
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('consent', 'default', denied);
  window['ga-disable-' + id] = true;

  function read() {
    try {
      const saved = JSON.parse(localStorage.getItem(key));
      return saved && ['granted','denied'].includes(saved.value) && Number.isFinite(saved.expires) && saved.expires > Date.now() ? saved : null;
    } catch { return null; }
  }
  function referrerOrigin() {
    try {
      const source = new URL(document.referrer);
      if (!['https:','http:'].includes(source.protocol) || source.username || source.password || source.hostname.replace(/^www\./,'') === location.hostname.replace(/^www\./,'')) return '';
      return source.origin + '/';
    } catch { return ''; }
  }
  function clearCookies() {
    for (const cookie of document.cookie.split(';')) {
      const name = cookie.trim().split('=')[0];
      if (!/^_ga(?:_|$)/.test(name)) continue;
      document.cookie = name + '=; Max-Age=0; path=/';
      const parts = location.hostname.split('.');
      for (let i=0;i<parts.length-1;i++) document.cookie = name + '=; Max-Age=0; path=/; domain=.' + parts.slice(i).join('.');
    }
  }
  function sync() {
    clearTimeout(expiryTimer);
    if (storageAvailable) choice = read();
    if (!choice || choice.expires <= Date.now() || choice.value !== 'granted') {
      window['ga-disable-' + id] = true;
      clearCookies();
      status.textContent = 'Optional analytics is off. The profile remains fully available.';
      if (!choice) controls.open = true;
      if (loaded) {
        window.gtag('consent','update',denied);
        location.reload();
      }
      return;
    }
    expiryTimer = setTimeout(sync,Math.min(choice.expires-Date.now()+1,2147483647));
    window['ga-disable-' + id] = false;
    status.textContent = 'Optional analytics is allowed. You can turn it off here.';
    if (loaded) return;
    loaded = true;
    window.gtag('consent','update',{...denied,analytics_storage:'granted'});
    window.gtag('set',{page_location:location.origin+'/',page_referrer:referrerOrigin(),page_title:'Anissa Feby'});
    window.gtag('js',new Date());
    window.gtag('config',id,{send_page_view:false,allow_google_signals:false,allow_ad_personalization_signals:false,cookie_expires:15552000,cookie_update:false});
    window.gtag('event','page_view',{send_to:id,page_location:location.origin+'/',page_referrer:referrerOrigin(),page_title:'Anissa Feby'});
    const script = document.createElement('script');
    script.id = 'anissafeby-ga4'; script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id='+id;
    document.head.appendChild(script);
  }
  function choose(value) {
    choice = {value,expires:Date.now()+lifetime};
    try { localStorage.setItem(key,JSON.stringify(choice)); storageAvailable = true; }
    catch { storageAvailable = false; }
    sync();
    controls.open = false;
  }
  document.getElementById('analytics-allow').addEventListener('click',()=>choose('granted'));
  document.getElementById('analytics-deny').addEventListener('click',()=>choose('denied'));
  window.addEventListener('storage',event=>{if (event.key === key || event.key === null) { storageAvailable = true; sync(); }});
  window.addEventListener('focus',sync);
  document.addEventListener('visibilitychange',()=>{if (!document.hidden) sync();});
  sync();
})();
