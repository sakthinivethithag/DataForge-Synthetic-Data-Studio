document.addEventListener("DOMContentLoaded",async()=>{
 try {
  const p=await DF.get("/api/dataset/profile");
  document.querySelector("#datasetName").textContent=p.name;
  document.querySelector("#rows").textContent=p.rows.toLocaleString();
  document.querySelector("#columns").textContent=p.columns;
  document.querySelector("#missing").textContent=p.missing_values;
  document.querySelector("#duplicates").textContent=p.duplicate_rows;
  document.querySelector("#quality").textContent=p.quality;
  const s=await DF.get("/api/reports/summary");
  document.querySelector("#genStatus").textContent=s.generation?.rows ? `${s.generation.rows} rows generated (${s.generation.method})` : "Not generated yet";
  document.querySelector("#privacyStatus").textContent=s.privacy?.risk_level || "Run a privacy check";
  if(window.Chart && p.column_details.some(c=>["integer","decimal"].includes(c.type))){
   const c=p.column_details.find(c=>["integer","decimal"].includes(c.type)).name;
   const values=p.preview.map(r=>Number(r[c])).filter(Number.isFinite);
   new Chart(document.querySelector("#dashChart"),{type:"bar",data:{labels:values.map((_,i)=>i+1),datasets:[{label:c,data:values}]},options:{responsive:true,plugins:{legend:{display:false}}}});
  }
 }catch(e){document.querySelector("#dashEmpty").hidden=false;document.querySelector("#dashEmpty").textContent="No active dataset. Open Dataset Workspace and load a sample or upload a CSV."}
});
