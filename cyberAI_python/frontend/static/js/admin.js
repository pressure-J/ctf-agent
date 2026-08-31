async function loadAdmin(){try{
  const s=await (await fetch("/api/admin/stats",{headers:hdr()})).json();
  document.getElementById("admin-stats").innerHTML=
    `<div class="row">会话 ${s.total_conversations} · 消息 ${s.total_messages} · 工具执行 ${s.total_tool_executions} · 注册工具 ${s.registered_tools}</div>`;
  const a=await (await fetch("/api/admin/audit?limit=20",{headers:hdr()})).json();
  const el=document.getElementById("admin-audit"); el.innerHTML="";
  (a.logs||[]).forEach(x=>{const d=document.createElement("div");d.className="row";d.textContent=JSON.stringify(x).slice(0,100);el.appendChild(d)});
}catch(e){addLine("error","统计失败: "+e.message)}}