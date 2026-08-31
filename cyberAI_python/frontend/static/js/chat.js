let CURR=null;
function _tf(dt){const now=new Date(),d=new Date(dt||now);
  const a=new Date(now.getFullYear(),now.getMonth(),now.getDate()),b=new Date(d.getFullYear(),d.getMonth(),d.getDate());
  const day=Math.round((a-b)/86400000);return day<=0?"今天":day===1?"昨天":day<=7?"过去七天":"更早";}
async function loadConvs(){try{
  const j=await (await fetch("/api/conversations",{headers:hdr()})).json();
  const q=(document.getElementById("conv-search").value||"").toLowerCase();
  const list=(j.conversations||[]).filter(c=>!q||(c.title||"").toLowerCase().includes(q));
  const groups={};list.forEach(c=>{const k=_tf(c.updated_at||c.created_at);(groups[k]=groups[k]||[]).push(c)});
  const el=document.getElementById("conv-list");el.innerHTML="";
  Object.keys(groups).forEach(g=>{const hd=document.createElement("div");hd.className="conv-group";hd.textContent=g;el.appendChild(hd);
    groups[g].forEach(c=>{const d=document.createElement("div");d.className="conv-item"+(c.id===CURR?" on":"");
      const t=document.createElement("span");t.textContent=c.title;t.onclick=()=>selectConv(c.id);
      const x=document.createElement("button");x.textContent="\u2715";x.className="conv-del";x.onclick=e=>{e.stopPropagation();delConv(c.id)};
      d.appendChild(t);d.appendChild(x);el.appendChild(d);});});
  if(!list.length)el.textContent=q?"(无匹配)":"(暂无会话，点「+ 新对话」开始)";
}catch(e){}}
async function newConv(){try{const j=await (await fetch("/api/conversations",{method:"POST",headers:hdr()})).json();CURR=j.id;document.getElementById("log").innerHTML="";loadConvs();}catch(e){}}
async function selectConv(id){try{
  CURR=id;const j=await (await fetch("/api/conversations/"+id,{headers:hdr()})).json();
  const log=document.getElementById("log");log.innerHTML="";
  (j.messages||[]).forEach(msg=>{const d=document.createElement("div");d.className="line "+msg.role;d.textContent=msg.content;log.appendChild(d)});log.scrollTop=log.scrollHeight;
  loadConvs();
}catch(e){}}
async function delConv(id){try{await fetch("/api/conversations/"+id,{method:"DELETE",headers:hdr()});if(CURR===id)CURR=null;loadConvs();}catch(e){}}
function toggleSettings(){const s=document.getElementById("conv-settings");s.style.display=s.style.display==="none"?"block":"none"}
async function sendOnce(msg){try{
  const r=await fetch("/api/chat",{method:"POST",headers:hdr(),body:JSON.stringify({message:msg,conversation_id:CURR})});
  const j=await r.json();addLine("assistant",j.response||JSON.stringify(j));CURR=j.conversation_id;loadConvs();
}catch(e){addLine("error","错误: "+e.message)}}
async function sendStream(msg){try{
  const r=await fetch("/api/chat/stream",{method:"POST",headers:hdr(),body:JSON.stringify({message:msg,conversation_id:CURR})});
  const reader=r.body.getReader(),dec=new TextDecoder();let buf="";const log=document.getElementById("log");
  let cur=document.createElement("div");cur.className="line assistant";log.appendChild(cur);
  while(1){const {done,value}=await reader.read();if(done)break;buf+=dec.decode(value,{stream:true});
    const parts=buf.split("\n\n");buf=parts.pop();
    for(const ln of parts){if(!ln.startsWith("data:"))continue;const s=ln.slice(5).trim();if(s==="[DONE]")break;
      let ev;try{ev=JSON.parse(s)}catch{continue}
      if(ev.type==="llm")cur.textContent+=ev.delta||"";
      else if(ev.type==="tool_call"){const d=document.createElement("div");d.className="line tool";d.textContent="[工具] "+ev.name;log.appendChild(d);cur=d}
      else if(ev.type==="done"){cur=document.createElement("div");cur.className="line assistant";log.appendChild(cur)}
      else if(ev.type==="error"){const d=document.createElement("div");d.className="line error";d.textContent=ev.message;log.appendChild(d)}
      log.scrollTop=log.scrollHeight;}}
  loadConvs();
}catch(e){addLine("error","错误: "+e.message)}}
async function sendMsg(){const inp=document.getElementById("msg"),msg=inp.value.trim();if(!msg)return;inp.value="";addLine("user",msg);(document.getElementById("stream").checked)?sendStream(msg):sendOnce(msg);}
