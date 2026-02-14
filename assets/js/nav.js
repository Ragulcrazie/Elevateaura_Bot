document.addEventListener("DOMContentLoaded",function(){
  const nav=`
  <nav class="nav">
    <div class="container nav-inner">
      <a class="logo" href="/">Elevate Aura</a>
      <div class="nav-links">
        <a href="/pages/ssc-daily-practice.html">SSC</a>
        <a href="/pages/rrb-daily-practice.html">RRB</a>
        <a href="/pages/bank-daily-practice.html">Bank</a>
        <a href="/pages/police-daily-practice.html">Police</a>
      </div>
    </div>
  </nav>`;
  document.body.insertAdjacentHTML("afterbegin",nav);
});
