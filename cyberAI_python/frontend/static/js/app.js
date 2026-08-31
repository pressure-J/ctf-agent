// 全局: token/headers/渲染 + 路由(对标Go switchPage), 侧边导航切换模块
function getTok(){return localStorage.getItem("token")}
function setTok(t){t?localStorage.setItem("token",t):localStorage.removeItem("token")}
function hdr(){return {"Content-Type":"application/json","Authorization":"Bearer "+getTok()}}
function showLogin(){document.getElementById("login-view").style.display="flex";document.getElementById("layout").style.display="none"}
function showApp(){document.getElementById("login-view").style.display="none";document.getElementById("layout").style.display="block"}
function addLine(cls,text){const l=document.getElementById("log");const d=document.createElement("div");d.className="line "+cls;d.textContent=text;l.appendChild(d);l.scrollTop=l.scrollHeight}
function addDelta(text){const l=document.getElementById("log");let last=l.lastElementChild;
  if(!last||last.className.indexOf("assistant")<0){last=document.createElement("div");last.className="line assistant";l.appendChild(last)}
  last.textContent+=text;l.scrollTop=l.scrollHeight}
const LOADERS={dashboard:loadDashboard,tools:loadTools,agents:loadAgents,workflows:loadWorkflows,knowledge:()=>{},admin:loadAdmin};
function go(page){
  document.querySelectorAll(".page").forEach(s=>s.style.display="none");
  const el=document.getElementById("page-"+page);if(el)el.style.display="block";
  document.querySelectorAll(".sidebar a").forEach(a=>a.classList.toggle("on",a.dataset.page===page));
  if(LOADERS[page])LOADERS[page]();
}
document.addEventListener("DOMContentLoaded",()=>{if(getTok()){showApp();go("dashboard")}else{showLogin()}});
