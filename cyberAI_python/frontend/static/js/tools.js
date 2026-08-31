async function loadTools(){try{
  const j=await (await fetch("/api/tools",{headers:hdr()})).json();
  const el=document.getElementById("tools-list"); el.innerHTML="";
  document.getElementById("tools-count").textContent=j.count||"";
  (j.tools||[]).forEach(t=>{const d=document.createElement("div");d.className="row";
    d.textContent=(typeof t==="string")?t:(`${t.name||""} [${t.category||"?"}] ${(t.description||"").slice(0,55)}`).trim();el.appendChild(d)});
}catch(e){addLine("error","工具加载失败: "+e.message)}}