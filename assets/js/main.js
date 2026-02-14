(function(){
  document.querySelectorAll('a[data-telegram]').forEach(a=>{
    const u=new URL(a.href);
    const p=new URLSearchParams(window.location.search);
    p.forEach((v,k)=>u.searchParams.set(k,v));
    a.href=u.toString();
  });
})();
