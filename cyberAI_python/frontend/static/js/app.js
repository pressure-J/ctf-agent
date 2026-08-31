function getTok(){return localStorage.getItem("token")}
function setTok(t){t?localStorage.setItem("token",t):localStorage.removeItem("token")}
function hdr(){return {"Content-Type":"application/json","Authorization":"Bearer "+getTok()}}
function showLogin(){document.getElementById("login-view").style.display="flex";document.getElementById("layout").style.display="none"}
function showApp(){document.getElementById("login-view").style.display="none";document.getElementById("layout").style.display="block"}
function addLine(cls,text){const l=document.getElementById("log");const d=document.createElement("div");d.className="line "+cls;d.textContent=text;l.appendChild(d);l.scrollTop=l.scrollHeight}
function addDelta(text){const l=document.getElementById("log");let last=l.lastElementChild;
  if(!last||last.className.indexOf("assistant")<0){last=document.createElement("div");last.className="line assistant";l.appendChild(last)}
  last.textContent+=text;l.scrollTop=l.scrollHeight}
const LOADERS={tools:"loadTools",agents:"loadAgents",workflows:"loadWorkflows",knowledge:"",admin:"loadChannels",audit:"loadAudit"};
function go(page){
  document.querySelectorAll(".page").forEach(s=>s.style.display="none");
  const el=document.getElementById("page-"+page);if(el)el.style.display="block";
  document.querySelectorAll(".sidebar a").forEach(a=>a.classList.toggle("on",a.dataset.page===page));
  const fn=window[LOADERS[page]]; if(typeof fn==="function") fn();
}
function initUI(){ try{ if(getTok()){showApp();go("chat")}else{showLogin()} }catch(_e){ showLogin() } }
initUI()
