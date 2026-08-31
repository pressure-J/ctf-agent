async function loadAgents(){try{
  const j=await (await fetch("/api/agents",{headers:hdr()})).json();
  const el=document.getElementById("agents-list"); el.innerHTML="";
  const list=j.agents||[]; if(!list.length)el.textContent="(暂无Agent, 可用 POST /api/agents 创建)";
  list.forEach(a=>{const d=document.createElement("div");d.className="row";d.textContent=JSON.stringify(a);el.appendChild(d)});
}catch(e){addLine("error","Agent加载失败: "+e.message)}}