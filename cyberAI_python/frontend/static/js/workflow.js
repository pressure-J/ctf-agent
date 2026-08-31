async function loadWorkflows(){try{
  const j=await (await fetch("/api/workflows",{headers:hdr()})).json();
  const el=document.getElementById("workflows-list"); el.innerHTML="";
  (j.workflows||[]).forEach(w=>{const d=document.createElement("div");d.className="row";
    d.textContent=`${w.name||w.id}  ${(w.description||"").slice(0,50)}`;el.appendChild(d)});
}catch(e){addLine("error","工作流加载失败: "+e.message)}}
async function executeWorkflow(){  // 简单: 执行第一个工作流(真实可多选)
  try{const wf=(await (await fetch("/api/workflows",{headers:hdr()})).json()).workflows||[];
    if(!wf.length){return addLine("error","无工作流可执行")}
    let data={}; try{data=JSON.parse(document.getElementById("wf-input").value||"{}")}catch{}
    const r=await fetch("/api/workflows/"+wf[0].id+"/execute",{method:"POST",headers:hdr(),body:JSON.stringify(data)});
    const j=await r.json(); addLine("tool","结果: "+JSON.stringify(j.result).slice(0,300));
  }catch(e){addLine("error","执行失败: "+e.message)}}