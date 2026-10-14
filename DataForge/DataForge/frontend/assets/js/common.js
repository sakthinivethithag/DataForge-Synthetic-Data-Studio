document.addEventListener("DOMContentLoaded",()=>{
 const path=location.pathname.split("/").pop()||"index.html";
 document.querySelectorAll(".nav-link").forEach(a=>{if(a.getAttribute("href")===path)a.classList.add("active")});
 const reset=document.querySelector("[data-reset]");
 if(reset) reset.addEventListener("click",async()=>{try{await DF.post("/api/reset",{});DF.notify("Workspace reset.");setTimeout(()=>location.href="/upload.html",500)}catch(e){DF.notify(e.message,"error")}});
});
