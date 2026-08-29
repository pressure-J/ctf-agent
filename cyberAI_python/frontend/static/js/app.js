// 轻量单页 JS: token 存取 + 视图切换 + 渲染工具(全部走 fetch 调后端 API)
function getTok(){return localStorage.getItem("token")}
function setTok(t){t?localStorage.setItem("token",t):localStorage.removeItem("token")}
function showView(id){document.getElementById("login-view").style.display=id==="login"?"block":"none";
  document.getElementById("app-view").style.display=id==="app"?"block":"none"}
function addLine(cls,text){const l=document.getElementById("log");
  const d=document.createElement("div"); d.className="line "+cls; d.textContent=text; l.appendChild(d); l.scrollTop=l.scrollHeight}
function addDelta(text){const l=document.getElementById("log");
  let last=l.lastElementChild;
  if(!last||last.className.indexOf("assistant")<0){last=document.createElement("div");last.className="line assistant";l.appendChild(last)}
  last.textContent+=text; l.scrollTop=l.scrollHeight}
document.addEventListener("DOMContentLoaded",()=>{if(getTok()){showView("app");who()}});
function who(){fetch("/api/conversations",{headers:{Authorization:"Bearer "+getTok()}}).then(()=>{})}
