document.addEventListener("DOMContentLoaded",()=>{
 const file=document.querySelector("#csvFile"), drop=document.querySelector("#dropZone");
 async function loadSample(id){try{const p=await DF.get("/api/samples/"+id);show(p);DF.notify("Sample dataset loaded.","success")}catch(e){DF.notify(e.message,"error")}}
 function show(p){document.querySelector("#profile").hidden=false;document.querySelector("#profileName").textContent=p.name;document.querySelector("#profileStats").textContent=`${p.rows} rows · ${p.columns} columns · ${p.missing_values} missing values · ${p.duplicate_rows} duplicate rows`;document.querySelector("#preview").innerHTML=DF.table(p.preview);document.querySelector("#types").innerHTML=p.column_details.map(c=>`<li><b>${DF.esc(c.name)}</b> — ${DF.esc(c.type)} · ${c.missing} missing ${c.sensitive_warning?'<span class="warning">· possible identifier</span>':''}</li>`).join("");}
 document.querySelectorAll("[data-sample]").forEach(b=>b.addEventListener("click",()=>loadSample(b.dataset.sample)));
 document.querySelector("#uploadForm").addEventListener("submit",async e=>{e.preventDefault();if(!file.files[0])return DF.notify("Choose a CSV file first.","error");let f=new FormData();f.append("file",file.files[0]);try{show(await DF.upload("/api/upload",f));DF.notify("CSV uploaded and profiled.","success")}catch(err){DF.notify(err.message,"error")}});
 drop.addEventListener("dragover",e=>{e.preventDefault();drop.classList.add("dragover")});
 drop.addEventListener("dragleave",()=>drop.classList.remove("dragover"));
 drop.addEventListener("drop",e=>{e.preventDefault();drop.classList.remove("dragover");if(e.dataTransfer.files[0]){file.files=e.dataTransfer.files;document.querySelector("#fileName").textContent=e.dataTransfer.files[0].name}});
 file.addEventListener("change",()=>document.querySelector("#fileName").textContent=file.files[0]?.name||"No file selected");
 document.querySelector("#schemaForm").addEventListener("submit",async e=>{e.preventDefault();const cols=document.querySelector("#schemaColumns").value.split(",").map(x=>x.trim()).filter(Boolean).map(name=>({name,type:"text"}));try{show(await DF.post("/api/dataset/create",{name:document.querySelector("#schemaName").value,rows:Number(document.querySelector("#schemaRows").value),columns:cols}));DF.notify("Custom dataset created.","success")}catch(err){DF.notify(err.message,"error")}});
});
