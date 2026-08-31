// 全局: token/请求头/视图/渲染 + 页签切换(每次只加载当前页数据)
function getTok(){return localStorage.getItem("token")}
function setTok(t){t?localStorage.setItem("token",t):localStorage.removeItem("token")}
function hdr(){return {"Content-Type":"application/json","Authorization":"Bearer "+getTok()}}
function showView(id){document.getElementById("login-view").style.display=id==="login"?"block":"none";
  document.getElementById("app-view").style.display=id==="app"?"block":"none"}
function addLine(cls,text){const l=document.getElementById("log");
  const d=document.createElement("div"); d.className="line "+cls; d.textContent=text; l.appendChild(d); l.scrollTop=l.scrollHeight}
function addDelta(text){const l=document.getElementById("log");
  let last=l.lastElementChild;
  if(!last||last.className.indexOf("assistant")<0){last=document.createElement("div");last.className="line assistant";l.appendChild(last)}
  last.textContent+=text; l.scrollTop=l.scrollHeight}
const LOADERS={tools:loadTools,agents:loadAgents,workflows:loadWorkflows,knowledge:()=>{},admin:loadAdmin};
function switchTab(tab){
  document.querySelectorAll(".tab-page").forEach(s=>s.style.display="none");
  document.getElementById("tab-"+tab).style.display="block";
  document.querySelectorAll("header nav a").forEach(a=>a.classList.toggle("on",a.dataset.tab===tab));
  if(LOADERS[tab]) LOADERS[tab]();
}
document.addEventListener("DOMContentLoaded",()=>{if(getTok()){showView("app");switchTab("chat")}});
