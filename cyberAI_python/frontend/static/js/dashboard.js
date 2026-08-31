// 仪表盘(对标Go dashboard): 多维统计卡 + 功能入口
async function loadDashboard(){try{
  const s=await (await fetch("/api/admin/stats",{headers:hdr()})).json();
  const el=document.getElementById("dash-stats"); el.innerHTML="";
  const items=[["会话",s.total_conversations],["消息",s.total_messages],["工具执行",s.total_tool_executions],
    ["注册工具",s.registered_tools],["用户",s.total_users],["Agent",s.total_agents],
    ["工作流",s.total_workflows],["知识库chunk",s.knowledge_chunks],["AI通道",s.ai_channels]];
  items.forEach(([k,v])=>{const d=document.createElement("div");d.className="stat";
    d.innerHTML=`<b>${v??0}</b><span>${k}</span>`;el.appendChild(d)});
  const nav=document.createElement("div"); nav.className="dash-nav";
  [["对话","chat"],["工具","tools"],["Agent","agents"],["工作流","workflows"],["知识库","knowledge"],["管理","admin"]].forEach(([label,pg])=>{
    const b=document.createElement("button");b.textContent=label;b.onclick=()=>go(pg);nav.appendChild(b)});
  el.appendChild(nav);
}catch(e){document.getElementById("dash-stats").textContent="加载失败"}}
