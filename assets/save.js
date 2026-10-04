/* Shortlist saved in this browser: localStorage 'shortlist' = [slug, ...] */
(function(){
  var KEY = 'shortlist';
  function get(){ try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch(e) { return []; } }
  function set(a){ try { localStorage.setItem(KEY, JSON.stringify(a)); } catch(e) {} paint(); }
  function paint(){
    var a = get();
    document.querySelectorAll('[data-saved-count]').forEach(function(el){ el.textContent = a.length; });
    document.querySelectorAll('[data-save]').forEach(function(b){
      var on = a.indexOf(b.dataset.save) > -1;
      b.setAttribute('aria-pressed', on);
      b.innerHTML = on ? '★ Saved' : '☆ Save';
    });
  }
  document.addEventListener('click', function(ev){
    var b = ev.target.closest && ev.target.closest('[data-save]'); if (!b) return;
    ev.preventDefault();
    var a = get(), s = b.dataset.save, i = a.indexOf(s);
    if (i > -1) a.splice(i, 1); else a.push(s);
    set(a);
  });
  window.addEventListener('storage', function(e){ if (e.key === KEY) paint(); });
  window.Shortlist = {get: get, set: set, paint: paint};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', paint); else paint();
})();
