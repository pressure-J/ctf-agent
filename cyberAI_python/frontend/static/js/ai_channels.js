// AI 通道配置(管理页): 列表/新增/保存/删除/设默认/测试连接(消费 /api/settings/ai-channels)
let _CHS=[], _CUR=null;
function _v(id){return document.getElementById(id).value}
function _fill(c){["ch-name","ch-provider","ch-baseurl","ch-model","ch-maxctx","ch-maxout"].forEach(id=>document.getElementById(id).value="");
  document.getElementById("ch-name").value=c.name||"";document.getElementById("ch-provider").value=c.provider||"openai";
  document.getElementById("ch-baseurl").value=c.base_url||"";document.getElementById("ch-model").value=c.model||"";
  document.getElementById("ch-maxctx").value=c.max_context||"";document.getElementById("ch-maxout").value=c.max_output||"";
  document.getElementById("ch-apikey").value="";}
function _cur(){return _CUR!=null?_CHS[_CUR]:null}
async function loadChannels(){try{
  const j=await (await fetch("/api/settings/ai-channels",{headers:hdr()})).json(); _CHS=j.channels||[];
  const sel=document.getElementById("ch-select"); sel.innerHTML="";
  _CHS.forEach((c,i)=>{const o=document.createElement("option");o.value=i;o.textContent=c.name+(c.is_default?" (默认)":"");sel.appendChild(o)});
  if(_CUR==null&&_CHS.length)_CUR=0;
  if(_CUR!=null&&_CHS[_CUR])_fill(_CHS[_CUR]);
}catch(e){document.getElementById("ch-msg").textContent="加载失败"}}
function selectChannel(){_CUR=+document.getElementById("ch-select").value;if(_CHS[_CUR])_fill(_CHS[_CUR]);}
function addChannel(){_CUR=null;["ch-name","ch-provider","ch-baseurl","ch-model","ch-maxctx","ch-maxout"].forEach(id=>document.getElementById(id).value="");document.getElementById("ch-apikey").value="";document.getElementById("ch-name").focus();}
async function saveChannel(){try{
  const body={name:_v("ch-name"),provider:_v("ch-provider")||"openai",base_url:_v("ch-baseurl"),api_key:_v("ch-apikey"),
    model:_v("ch-model"),max_context:+_v("ch-maxctx")||120000,max_output:+_v("ch-maxout")||32768};
  const cur=_cur(), url=cur?"/api/settings/ai-channels/"+cur.id:"/api/settings/ai-channels";
  const r=await fetch(url,{method:cur?"PUT":"POST",headers:hdr(),body:JSON.stringify(body)});
  document.getElementById("ch-msg").textContent=r.ok?"已保存(切换模型需重启生效)":"保存失败";
  if(r.ok){_CUR=null;loadChannels();}
}catch(e){document.getElementById("ch-msg").textContent="保存失败: "+e.message}}
async function deleteChannel(){const cur=_cur();if(!cur)return;await fetch("/api/settings/ai-channels/"+cur.id,{method:"DELETE",headers:hdr()});_CUR=null;loadChannels();}
async function setDefault(){const cur=_cur();if(!cur)return;const r=await fetch("/api/settings/ai-channels/"+cur.id+"/default",{method:"POST",headers:hdr()});_CUR=null;if(r.ok)loadChannels();}
async function testChannel(){try{
  const j=await (await fetch("/api/settings/ai-channels/test",{method:"POST",headers:hdr(),
    body:JSON.stringify({base_url:_v("ch-baseurl"),api_key:_v("ch-apikey"),model:_v("ch-model")})})).json();
  document.getElementById("ch-msg").textContent=j.ok?"✓ 连接正常":("✗ 失败: "+(j.error||""));
}catch(e){document.getElementById("ch-msg").textContent="测试失败"}}
