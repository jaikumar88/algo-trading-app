// Small client helpers for the Trading UI
document.addEventListener('DOMContentLoaded', function(){
  // highlight active nav link
  const path = location.pathname.replace(/\/$/, '');
  document.querySelectorAll('.nav-link').forEach(a=>{
    try{
      const href = a.getAttribute('href').replace(/\/$/, '');
      if(href === path) a.classList.add('active');
    }catch(e){}
  });

  // offcanvas toggle behavior for #sidebar when using data-bs-target
  const btn = document.getElementById('btn-toggle');
  if(btn){
    btn.addEventListener('click', ()=>{
      // on mobile, use bootstrap offcanvas if present
      const off = document.getElementById('sidebarOffcanvas');
      if(off){
        const oc = new bootstrap.Offcanvas(off);
        oc.toggle();
      } else {
        const sb = document.getElementById('sidebar');
        if(sb) sb.classList.toggle('d-none');
      }
    });
  }
});
