// 对话: /api/chat (普通) 或 /api/chat/stream (SSE 流式, tool_call/tool_result/llm/done)
function hdr(){return {"Content-Type":"application/json","Authorization":"Bearer "+getTok()}}
async function sendMsg(){
  const inp=document.getElementById("msg"), msg=inp.value.trim(); if(!msg)return;
  inp.value=""; addLine("user",msg);
  document.getElementById("stream").checked ? await sendStream(msg) : await sendOnce(msg);
}
async function sendOnce(msg){
  addLine("assistant","…");
  try{const r=await fetch("/api/chat",{method:"POST",headers:hdr(),body:JSON.stringify({message:msg})});
    const j=await r.json(); addLine("assistant", j.response||JSON.stringify(j));
  }catch(e){addLine("error","错误: "+e.message)}
}
async function sendStream(msg){
  try{
    const r=await fetch("/api/chat/stream",{method:"POST",headers:hdr(),body:JSON.stringify({message:msg})});
    const reader=r.body.getReader(), dec=new TextDecoder(); let buf="";
    const log=document.getElementById("log");
    function freshLine(cls){const d=document.createElement("div");d.className="line "+cls;log.appendChild(d);return d}
    let cur=freshLine("assistant");
    while(1){const {done,value}=await reader.read(); if(done)break;
      buf+=dec.decode(value,{stream:true}); const parts=buf.split("\n\n"); buf=parts.pop();
      for(const ln of parts){ if(!ln.startsWith("data:"))continue;
        const s=ln.slice(5).trim(); if(s==="[DONE]")continue; let ev; try{ev=JSON.parse(s)}catch{continue}
        if(ev.type==="llm") cur.textContent+=ev.delta;
        else if(ev.type==="tool_call"){cur=freshLine("tool");cur.textContent="[工具] "+ev.name+" "+ev.arguments}
        else if(ev.type==="tool_result"){cur=freshLine("tool");cur.textContent="[工具结果] 已执行"}
        else if(ev.type==="done"){if(ev.answer)cur.textContent+=ev.answer;cur=freshLine("assistant")}
        else if(ev.type==="error"){cur=freshLine("error");cur.textContent="错误: "+ev.message}
        log.scrollTop=log.scrollHeight;
      }
    }
  }catch(e){addLine("error","错误: "+e.message)}
}
