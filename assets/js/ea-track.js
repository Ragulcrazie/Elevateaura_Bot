/* Elevate Aura conversion tracking. Loads GA4 and reports the enquiry actions that matter:
   WhatsApp, phone, email, demo/CTA clicks, downloads and form activity. Safe to include on
   every page; it does nothing if GA fails to load. */
(function () {
  var GA_ID = 'G-3XX97R8F1Y';
  if (!window.dataLayer) { window.dataLayer = []; }
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  if (!document.querySelector('script[src*="googletagmanager.com/gtag/js"]')) {
    var s = document.createElement('script'); s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', GA_ID, { send_page_view: true });
  }
  function product() {
    var p = location.pathname.split('/').filter(Boolean)[0] || 'home';
    return p.replace('.html', '');
  }
  function send(name, params) {
    params = params || {};
    params.product_cluster = product();
    params.page_path = location.pathname;
    try { gtag('event', name, params); } catch (e) {}
  }
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a,button');
    if (!a) return;
    var href = (a.getAttribute('href') || '').toLowerCase();
    var label = (a.textContent || '').trim().slice(0, 80);
    if (href.indexOf('wa.me') > -1 || href.indexOf('whatsapp') > -1) {
      send('whatsapp_click', { link_text: label });
    } else if (href.indexOf('tel:') === 0) {
      send('phone_click', { link_text: label });
    } else if (href.indexOf('mailto:') === 0) {
      send('email_click', { link_text: label });
    } else if (/\.(exe|msi|zip|pdf|apk)(\?|$)/.test(href) || a.hasAttribute('download')) {
      send('file_download', { link_url: href });
    } else if (a.classList.contains('btn') || a.classList.contains('nav-cta') || /demo|strategy|quote|call|contact/.test(href + ' ' + label.toLowerCase())) {
      send('cta_click', { link_text: label, link_url: href });
    }
  }, true);
  var formStarted = false;
  document.addEventListener('focusin', function (ev) {
    if (!formStarted && ev.target && ev.target.form) { formStarted = true; send('form_start', {}); }
  });
  document.addEventListener('submit', function (ev) {
    var f = ev.target; var id = f.getAttribute('id') || f.getAttribute('name') || 'form';
    send('form_submit', { form_id: id });
  }, true);
})();
