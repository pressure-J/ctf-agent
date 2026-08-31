async function searchKB(){try{
  const q=document.getElementById("kb-query").value.trim(); if(!q)return;
  const r=await fetch("/api/knowledge/search?query="+encodeURIComponent(q)+"&top_k=5",{headers:hdr()});
  const j=await r.json(); const el=document.getElementById("kb-results"); el.innerHTML="";
  (j.results||[]).forEach(x=>{const d=document.createElement("div");d.className="row";
    d.textContent=`[${x.source||""} score=${x.score}] ${(x.text||"").slice(0,80)}`;el.appendChild(d)});
}catch(e){addLine("error","检索失败: "+e.message)}}