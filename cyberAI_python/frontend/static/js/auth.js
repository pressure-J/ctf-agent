// 登录/退出: POST /api/auth/login
async function authLogin(){
  const u=document.getElementById("u").value, p=document.getElementById("p").value, m=document.getElementById("login-msg");
  try{
    const r=await fetch("/api/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:u,password:p})});
    const j=await r.json();
    if(r.ok){setTok(j.access_token);showView("app");m.textContent="";document.getElementById("who").textContent=u}
    else m.textContent=j.detail||"登录失败";
  }catch(e){m.textContent="连接失败: "+e.message}
}
function authLogout(){setTok(null);showView("login");document.getElementById("log").innerHTML=""}
