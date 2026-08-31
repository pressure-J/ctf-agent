async function loadDashboard(){try{
  const s=await (await fetch("/api/admin/stats",{headers:hdr()})).json();
  const el=document.getElementById("dash-stats");el.innerHTML="";
  [["会话",s.total_conversations],["消息",s.total_messages],["工具执行",s.total_tool_executions],["注册工具",s.registered_tools]].forEach(([k,v])=>{
    const d=document.createElement("div");d.className="stat";d.innerHTML=`<b>${v}</b><span>${k}</span>`;el.appendChild(d)});
}catch(e){document.getElementById("dash-stats").textContent="加载失败"}}
