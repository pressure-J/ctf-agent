let _CHS=[], _CUR=null;
function _v(id){return document.getElementById(id).value}
function _fillCfg(c){["ch-name","ch-provider","ch-baseurl","ch-maxctx","ch-maxout"].forEach(id=>document.getElementById(id).value="");
  document.getElementById("ch-name").value=c.name||"";document.getElementById("ch-provider").value=c.provider||"openai";
  document.getElementById("ch-baseurl").value=c.base_url||"";document.getElementById("ch-maxctx").value=c.max_context||"";
  document.getElementById("ch-maxout").value=c.max_output||"";document.getElementById("ch-apikey").value="";
  const sel=document.getElementById("ch-model"); if(c.model){sel.innerHTML=`<option value="${c.model}">${c.model}</option>`;sel.value=c.model;}}
function _cur(){return _CUR!=null?_CHS[_CUR]:null}
async function loadChannels(){try{
  const j=await (await fetch("/api/settings/ai-channels",{headers:hdr()})).json(); _CHS=j.channels||[];
  const sel=document.getElementById("ch-select"); sel.innerHTML="";
  _CHS.forEach((c,i)=>{const o=document.createElement("option");o.value=i;o.textContent=c.name+(c.is_default?" (默认)":"");sel.appendChild(o)});
  if(_CUR==null&&_CHS.length)_CUR=0;
  if(_CUR!=null&&_CHS[_CUR])_fillCfg(_CHS[_CUR]);
}catch(e){document.getElementById("ch-msg").textContent="加载失败"}}
function selectChannel(){_CUR=+document.getElementById("ch-select").value;if(_CHS[_CUR])_fillCfg(_CHS[_CUR]);}
function addChannel(){_CUR=null;["ch-name","ch-provider","ch-baseurl","ch-maxctx","ch-maxout"].forEach(id=>document.getElementById(id).value="");
  document.getElementById("ch-apikey").value="";document.getElementById("ch-name").focus();}
async function loadModels(){try{
  const j=await (await fetch("/api/settings/ai-channels/models",{method:"POST",headers:hdr(),
    body:JSON.stringify({base_url:_v("ch-baseurl"),api_key:_v("ch-apikey")})})).json();
  const sel=document.getElementById("ch-model"); sel.innerHTML="";
  if(j.ok){ (j.models||[]).forEach(m=>{const o=document.createElement("option");o.value=m;o.textContent=m;sel.appendChild(o)});
    document.getElementById("ch-msg").textContent=`已加载 ${j.count} 个模型，请选择`; }
  else { sel.innerHTML=`<option value="">获取失败</option>`; document.getElementById("ch-msg").textContent="获取模型失败: "+(j.error||""); }
}catch(e){document.getElementById("ch-msg").textContent="获取模型失败"}}
async function saveChannel(){try{
  const body={name:_v("ch-name"),provider:_v("ch-provider")||"openai",base_url:_v("ch-baseurl"),api_key:_v("ch-apikey"),
    model:_v("ch-model"),max_context:+_v("ch-maxctx")||120000,max_output:+_v("ch-maxout")||32768};
  const cur=_cur(), url=cur?"/api/settings/ai-channels/"+cur.id:"/api/settings/ai-channels";
  const r=await fetch(url,{method:cur?"PUT":"POST",headers:hdr(),body:JSON.stringify(body)});
  const saved=r.ok?await r.json():null;
  document.getElementById("ch-msg").textContent=r.ok?"已保存(切换模型需重启生效)":"保存失败";
  if(r.ok){ const rid=(saved&&saved.id)||(cur&&cur.id); _CUR=null; await loadChannels();
    if(rid){ const i=_CHS.findIndex(x=>x.id===rid); if(i>=0){_CUR=i;_fillCfg(_CHS[i]);document.getElementById("ch-select").value=i;} }
  }
}catch(e){document.getElementById("ch-msg").textContent="保存失败: "+e.message}}
async function deleteChannel(){const cur=_cur();if(!cur)return;await fetch("/api/settings/ai-channels/"+cur.id,{method:"DELETE",headers:hdr()});_CUR=null;loadChannels();}
async function setDefault(){const cur=_cur();if(!cur)return;const r=await fetch("/api/settings/ai-channels/"+cur.id+"/default",{method:"POST",headers:hdr()});_CUR=null;if(r.ok)loadChannels();}
async function testChannel(){try{
  const j=await (await fetch("/api/settings/ai-channels/test",{method:"POST",headers:hdr(),
    body:JSON.stringify({base_url:_v("ch-baseurl"),api_key:_v("ch-apikey"),model:_v("ch-model")})})).json();
  document.getElementById("ch-msg").textContent=j.ok?"✓ 连接正常":("✗ 失败: "+(j.error||""));
}catch(e){document.getElementById("ch-msg").textContent="测试失败"}}
