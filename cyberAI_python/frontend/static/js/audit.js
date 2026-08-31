async function loadAudit(){try{
  const a=await (await fetch("/api/admin/audit?limit=50",{headers:hdr()})).json();
  const el=document.getElementById("audit-list"); el.innerHTML="";
  if(!(a.logs||[]).length)el.textContent="(暂无审计日志)";
  (a.logs||[]).forEach(x=>{const d=document.createElement("div");d.className="row";d.textContent=JSON.stringify(x).slice(0,120);el.appendChild(d)});
}catch(e){document.getElementById("audit-list").textContent="加载失败"}}