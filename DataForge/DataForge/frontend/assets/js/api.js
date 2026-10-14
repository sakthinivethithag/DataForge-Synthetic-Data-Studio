window.DF = {
  async request(url, options={}) {
    const response = await fetch(url, options);
    const type = response.headers.get("content-type") || "";
    if (!type.includes("application/json")) {
      if (!response.ok) throw new Error("Request failed (" + response.status + ")");
      return response;
    }
    const body = await response.json();
    if (!response.ok || !body.success) throw new Error(body.error || "Request failed");
    return body.data;
  },
  get(url) { return this.request(url); },
  post(url, body) { return this.request(url, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)}); },
  upload(url, form) { return this.request(url, {method:"POST", body:form}); },
  notify(message, type="info") {
    let el=document.querySelector("#toast");
    if(!el){el=document.createElement("div");el.id="toast";el.className="toast";document.body.appendChild(el);}
    el.textContent=message; el.dataset.type=type; el.classList.add("show");
    clearTimeout(window.__dfToast); window.__dfToast=setTimeout(()=>el.classList.remove("show"),3500);
  },
  esc(value) { return String(value ?? "").replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); },
  table(rows) {
    if(!rows || !rows.length) return '<p class="muted">No preview available yet.</p>';
    const cols=Object.keys(rows[0]);
    return '<div class="table-wrap"><table><thead><tr>'+cols.map(c=>'<th>'+this.esc(c)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map(c=>'<td>'+this.esc(r[c])+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
  }
};
