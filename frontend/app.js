(() => {
  const $ = (s) => document.querySelector(s);
  const thread = $("#thread"), form = $("#form"), msg = $("#msg"), send = $("#send");
  const fileInput = $("#file"), preview = $("#preview"), chips = $("#chips");
  const welcome = $("#welcome");

  const sid = (() => {
    let v = sessionStorage.getItem("sid");
    if (!v) {
      v = (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2) + Date.now());
      sessionStorage.setItem("sid", v);
    }
    return v;
  })();

  let currentFile = null;

  /* ---------- utilitaires ---------- */
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function md(text) {
    const inline = (t) => esc(t).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/(^|[^\w])_(.+?)_(?=[^\w]|$)/g, "$1<em>$2</em>");
    const out = []; let list = null;
    const close = () => { if (list) { out.push(`</${list}>`); list = null; } };
    for (const raw of String(text).split("\n")) {
      const line = raw.trimEnd();
      let m;
      if ((m = line.match(/^#{1,4}\s+(.*)/))) { close(); out.push(`<h3>${inline(m[1])}</h3>`); }
      else if ((m = line.match(/^\s*[-*•]\s+(.*)/))) { if (list !== "ul") { close(); out.push("<ul>"); list = "ul"; } out.push(`<li>${inline(m[1])}</li>`); }
      else if ((m = line.match(/^\s*\d+[.)]\s+(.*)/))) { if (list !== "ol") { close(); out.push("<ol>"); list = "ol"; } out.push(`<li>${inline(m[1])}</li>`); }
      else if (!line.trim()) { close(); }
      else { close(); out.push(`<p>${inline(line)}</p>`); }
    }
    close();
    return out.join("");
  }

  function scrollDown() { thread.scrollTo({ top: thread.scrollHeight, behavior: "smooth" }); }

  function addBubble(cls, html) {
    const el = document.createElement("div");
    el.className = "bubble " + cls;
    el.innerHTML = html;
    thread.appendChild(el);
    scrollDown();
    return el;
  }

  function showThread() {
    if (welcome) welcome.hidden = true;
    thread.style.display = "flex";
  }

  function showWelcome() {
    if (welcome) welcome.hidden = false;
    thread.style.display = "none";
    thread.innerHTML = "";
    setMode("scan");
    setChips([]);
  }

  function setMode(mode) {
    const m = $("#mode");
    if (mode === "learn") {
      m.textContent = "Apprendre";
      m.classList.add("learn");
      msg.placeholder = "Pose une question ou réponds…";
    } else {
      m.textContent = "Scanner";
      m.classList.remove("learn");
      msg.placeholder = "Colle le SMS ici…";
    }
  }

  function setChips(list) {
    chips.innerHTML = "";
    (list || []).forEach((c) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "chip"; b.textContent = c;
      b.addEventListener("click", () => {
        msg.value = c + (c === "/plan" ? " " : "");
        msg.focus(); autosize();
        if (c !== "/plan") form.requestSubmit();
      });
      chips.appendChild(b);
    });
  }

  function autosize() { msg.style.height = "auto"; msg.style.height = Math.min(msg.scrollHeight, 140) + "px"; }
  msg.addEventListener("input", autosize);
  msg.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });

  /* ---------- fichier joint ---------- */
  fileInput.addEventListener("change", () => { currentFile = fileInput.files[0] || null; renderPreview(); });
  function renderPreview() {
    if (!currentFile) { preview.hidden = true; preview.innerHTML = ""; return; }
    preview.hidden = false; preview.innerHTML = "";
    if (currentFile.type.startsWith("image/")) {
      const img = document.createElement("img"); img.src = URL.createObjectURL(currentFile); img.alt = ""; preview.appendChild(img);
    }
    const name = document.createElement("span"); name.textContent = currentFile.name; preview.appendChild(name);
    const rm = document.createElement("button"); rm.type = "button"; rm.textContent = "Retirer";
    rm.onclick = () => { currentFile = null; fileInput.value = ""; renderPreview(); };
    preview.appendChild(rm);
  }

  /* ---------- boutons d'accueil ---------- */
  $("#btnScan").addEventListener("click", () => { showThread(); msg.focus(); });
  $("#btnPhoto").addEventListener("click", () => { showThread(); fileInput.click(); });
  $("#btnLearn").addEventListener("click", () => { showThread(); msg.value = "/apprendre"; form.requestSubmit(); });
  $("#btnExamples").addEventListener("click", () => {
    const panel = $("#examplesPanel");
    panel.hidden = !panel.hidden;
  });
  $("#qHome").addEventListener("click", showWelcome);

  /* ---------- carte verdict ---------- */
  const ICONS = {
    legitime: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    suspect: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M12 6v8M12 18v.5"/></svg>',
    arnaque: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    illisible: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 .9-1 1.7M12 17.5v.5"/></svg>',
  };
  const SUB = { legitime: "Semble authentique", suspect: "Prudence", arnaque: "Ne fais rien de ce qu'il demande", illisible: "Je n'ai pas pu lire" };
  const EXLABELS = { expediteur: "Expéditeur", operateur_pretendu: "Opérateur annoncé", montant: "Montant", reference_transaction: "Référence", demande: "Ce qu'il demande", lien_ou_numero: "Lien ou numéro" };

  function renderVerdict(r) {
    const v = ["legitime", "suspect", "arnaque", "illisible"].includes(r.verdict) ? r.verdict : "suspect";
    const el = document.createElement("article");
    el.className = "verdict " + v;

    const signaux = (r.signaux || []).map((s) => `<li>${esc(s)}</li>`).join("");
    const ex = r.extraction || {};
    const rows = Object.keys(EXLABELS).filter((k) => ex[k]).map((k) => `<tr><th>${EXLABELS[k]}</th><td>${esc(ex[k])}</td></tr>`).join("");
    const an = r.analyse || {};
    const format = an.format_conforme_officiel === true ? "Oui" : an.format_conforme_officiel === false ? "Non" : null;
    const ecarts = (an.ecarts || []).map((s) => `<li>${esc(s)}</li>`).join("");
    const tact = (an.tactiques || []).map((s) => `<li>${esc(s)}</li>`).join("");

    el.innerHTML = `
      <div class="v-head">
        <div class="v-icon" aria-hidden="true">${ICONS[v]}</div>
        <div><h2 class="v-title">${esc(r.titre || "Résultat")}</h2><p class="v-sub">${SUB[v]}</p></div>
      </div>
      <div class="v-body">
        <p>${esc(r.explication || "")}</p>
        ${signaux ? `<h3>Pourquoi ?</h3><ul>${signaux}</ul>` : ""}
        ${r.conseil ? `<div class="todo"><strong>Que faire ?</strong>${esc(r.conseil)}</div>` : ""}
        ${r.traduction ? `<div class="trad"><small>Traduction (expérimentale)</small>${esc(typeof r.traduction === "string" ? r.traduction : JSON.stringify(r.traduction))}</div>` : ""}
        <div class="v-actions"><button class="btn" type="button" data-say>🔊 Écouter</button></div>
        <details>
          <summary>Détails (${esc(r.confiance)} % de certitude)</summary>
          ${rows ? `<table class="ex">${rows}</table>` : ""}
          ${format ? `<p>Format officiel : <strong>${format}</strong></p>` : ""}
          ${ecarts ? `<h3>Écarts</h3><ul>${ecarts}</ul>` : ""}
          ${tact ? `<h3>Tactiques</h3><ul>${tact}</ul>` : ""}
        </details>
      </div>`;
    el.querySelector("[data-say]").addEventListener("click", () => speak([r.titre, r.explication, r.conseil].filter(Boolean).join(". ")));
    thread.appendChild(el);
    scrollDown();
  }

  function speak(text) {
    if (!("speechSynthesis" in window)) { alert("Lecture vocale non disponible."); return; }
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text); u.lang = "fr-FR"; u.rate = 0.9;
    speechSynthesis.speak(u);
  }

  /* ---------- envoi ---------- */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = msg.value.trim();
    if (!text && !currentFile) return;

    showThread();
    const mine = document.createElement("div");
    mine.className = "bubble user";
    if (currentFile && currentFile.type.startsWith("image/")) {
      const img = document.createElement("img"); img.src = URL.createObjectURL(currentFile); img.alt = "Capture"; mine.appendChild(img);
    } else if (currentFile) {
      const f = document.createElement("div"); f.textContent = "📎 " + currentFile.name; mine.appendChild(f);
    }
    if (text) mine.appendChild(document.createTextNode(text));
    thread.appendChild(mine);

    const fd = new FormData();
    fd.append("session_id", sid);
    fd.append("message", text);
    fd.append("langue", $("#langue").value);
    if (currentFile) fd.append("file", currentFile);

    msg.value = ""; autosize(); currentFile = null; fileInput.value = ""; renderPreview(); setChips([]);
    send.disabled = true;
    const wait = addBubble("bot wait", "⏳ Je lis le message…");

    try {
      const res = await fetch("/api/chat", { method: "POST", body: fd });
      const data = await res.json();
      wait.remove();
      if (data.mode) setMode(data.mode);
      if (data.type === "scan") renderVerdict(data.result);
      else if (data.type === "error") addBubble("bot error", md(data.markdown));
      else { addBubble("bot", md(data.markdown)); setChips(data.suggestions); }
    } catch (err) {
      wait.remove();
      addBubble("bot error", "<p>Pas de connexion au serveur. Vérifie que l'application est lancée.</p>");
    } finally {
      send.disabled = false; msg.focus();
    }
  });

  /* ---------- exemples ---------- */
  fetch("/api/exemples").then((r) => r.json()).then((list) => {
    const box = $("#samples");
    list.forEach((x) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "sample";
      b.innerHTML = `<b>${esc(x.titre)}</b>${esc(x.texte.length > 80 ? x.texte.slice(0, 80) + "…" : x.texte)}`;
      b.addEventListener("click", () => { showThread(); msg.value = x.texte; autosize(); msg.focus(); });
      box.appendChild(b);
    });
  }).catch(() => {});

  /* ---------- init ---------- */
  thread.style.display = "none";
})();
