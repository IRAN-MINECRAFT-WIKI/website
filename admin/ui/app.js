/* =========================================================================
   MineBed Admin — main front-end logic.
   Hash-based router (#/dashboard, #/mods, ...) + small API client.
   All page renderers use direct DOM manipulation (createElement / textContent).
   ========================================================================= */
(function () {
  "use strict";

  // ------------------------------------------------------------------
  // Tiny helpers
  // ------------------------------------------------------------------
  const $  = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  function el(tag, attrs, ...children) {
    const node = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (v == null) continue;
        if (k === "class") node.className = v;
        else if (k === "html") node.innerHTML = v;            // explicit opt-in
        else if (k === "text") node.textContent = v;
        else if (k.startsWith("on") && typeof v === "function")
          node.addEventListener(k.slice(2), v);
        else if (v === true) node.setAttribute(k, "");
        else if (v === false) /* skip */;
        else node.setAttribute(k, v);
      }
    }
    for (const c of children) {
      if (c == null || c === false) continue;
      if (typeof c === "string" || typeof c === "number") node.appendChild(document.createTextNode(String(c)));
      else node.appendChild(c);
    }
    return node;
  }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); return node; }

  function fmtTime(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    if (isNaN(d)) return iso;
    return d.toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, c => (
      { "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]
    ));
  }

  // ------------------------------------------------------------------
  // API client
  // ------------------------------------------------------------------
  const API = {
    async get(path) {
      const r = await fetch(path);
      if (!r.ok) throw new Error(`GET ${path} → ${r.status}`);
      return r.json();
    },
    async post(path, body) {
      const r = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body || {}),
      });
      const text = await r.text();
      let data; try { data = JSON.parse(text); } catch { data = { raw: text }; }
      if (!r.ok) throw new Error(data.error || data.raw || `POST ${path} → ${r.status}`);
      return data;
    },
    async put(path, body) {
      const r = await fetch(path, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body || {}),
      });
      const text = await r.text();
      let data; try { data = JSON.parse(text); } catch { data = { raw: text }; }
      if (!r.ok) throw new Error(data.error || data.raw || `PUT ${path} → ${r.status}`);
      return data;
    },
    async del(path) {
      const r = await fetch(path, { method: "DELETE" });
      if (!r.ok) throw new Error(`DELETE ${path} → ${r.status}`);
      return r.json().catch(() => ({ ok: true }));
    },
  };

  // ------------------------------------------------------------------
  // Toast + modal
  // ------------------------------------------------------------------
  function toast(msg, kind) {
    const host = $("#toast-host");
    const t = el("div", { class: "toast " + (kind || "") }, String(msg));
    host.appendChild(t);
    setTimeout(() => { t.style.opacity = "0"; t.style.transition = "opacity .3s"; }, 2800);
    setTimeout(() => t.remove(), 3200);
  }

  function openModal(title, buildBody) {
    const host = $("#modal-host");
    $("#modal-title").textContent = title;
    const body = clear($("#modal-body"));
    if (typeof buildBody === "function") buildBody(body);
    host.classList.remove("hidden");
    host.setAttribute("aria-hidden", "false");
  }
  function closeModal() {
    const host = $("#modal-host");
    host.classList.add("hidden");
    host.setAttribute("aria-hidden", "true");
  }
  document.addEventListener("DOMContentLoaded", () => {
    $("#modal-close").addEventListener("click", closeModal);
    $(".modal-backdrop").addEventListener("click", closeModal);
    document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });
  });

  // ------------------------------------------------------------------
  // Router
  // ------------------------------------------------------------------
  const PAGES = {
    dashboard: { title: "داشبورد", render: renderDashboard },
    autofetch: { title: "دریافت خودکار", render: renderAutofetch },
    crawl:     { title: "دریافت تکی", render: renderCrawl },
    mods:      { title: "مادها", render: renderMods },
    settings:  { title: "تنظیمات", render: renderSettings },
  };

  function currentRoute() {
    const h = (location.hash || "#/dashboard").slice(2);
    return h in PAGES ? h : "dashboard";
  }

  function render() {
    const route = currentRoute();
    // Active nav highlight
    $$(".nav-item").forEach(a => a.classList.toggle(
      "active", a.getAttribute("data-route") === route));
    const page = PAGES[route];
    $("#page-title").textContent = page.title;
    const content = clear($("#content"));
    page.render(content);
  }
  window.addEventListener("hashchange", render);
  window.addEventListener("DOMContentLoaded", render);

  // ------------------------------------------------------------------
  // Page: Dashboard
  // ------------------------------------------------------------------
  async function renderDashboard(root) {
    root.appendChild(el("div", { class: "loading" }, "در حال بارگذاری…"));

    let data;
    try { data = await API.get("/api/dashboard"); }
    catch (e) {
      clear(root);
      root.appendChild(el("div", { class: "card" },
        el("h3", { text: "خطا" }),
        el("p", { class: "muted" }, String(e.message))));
      return;
    }
    clear(root);

    // ---- Stats ----
    const stats = el("div", { class: "stat-grid" });
    stats.appendChild(statCard("مادها", data.mods_count, "مجموع مادها در سایت"));
    stats.appendChild(statCard("مادهای AI", data.ai_mods_count, "تولیدشده با Agnes AI"));
    stats.appendChild(statCard("سیدها", data.seeds_count, "فایل seeds.json"));
    stats.appendChild(statCard("وضعیت Auto-Fetch",
      data.autofetch_running ? "در حال اجرا" : "آماده",
      data.autofetch_running ? "در حال پردازش" : "سیستم بیکار",
      data.autofetch_running ? "ok" : "idle"));
    root.appendChild(stats);

    // ---- Services ----
    const services = el("div", { class: "card mb-24" });
    services.appendChild(el("div", { class: "section-title" }, "وضعیت سرویس‌ها"));
    const sGrid = el("div", { class: "grid grid-2" });
    sGrid.appendChild(serviceBox("Agnes AI", data.services.agnes));
    sGrid.appendChild(serviceBox("GitHub", data.services.github));
    services.appendChild(sGrid);
    root.appendChild(services);

    // ---- Quick actions ----
    const qa = el("div", { class: "card" });
    qa.appendChild(el("div", { class: "section-title" }, "اقدامات سریع"));
    const row = el("div", { class: "row" });
    row.appendChild(el("a", {
      class: "btn btn-primary", href: "#/autofetch", text: "⚡ دریافت خودکار",
    }));
    row.appendChild(el("a", {
      class: "btn", href: "#/crawl", text: "◐ دریافت یک آدرس",
    }));
    row.appendChild(el("a", {
      class: "btn", href: "#/mods", text: "≣ مدیریت مادها",
    }));
    qa.appendChild(row);
    root.appendChild(qa);

    // ---- Data path info ----
    root.appendChild(el("div", { class: "card mt-24" },
      el("div", { class: "section-title" }, "مسیرها"),
      el("div", { class: "row" },
        el("span", { class: "muted", text: "فایل مادها:" }),
        el("code", { class: "mono", text: data.data_path })),
      el("div", { class: "row mt-8" },
        el("span", { class: "muted", text: "مسیر داده Astro:" }),
        el("code", { class: "mono", text: data.astro_data_path })),
    ));
  }

  function statCard(label, value, sub, kind) {
    return el("div", { class: "stat" },
      el("div", { class: "stat-label", text: label }),
      el("div", { class: "stat-value" + (kind === "ok" ? "" : ""), text: String(value) }),
      sub ? el("div", { class: "stat-sub", text: sub }) : null,
    );
  }
  function serviceBox(name, info) {
    info = info || { ok: false, detail: { error: "نامشخص" } };
    const detail = info.detail || {};
    const box = el("div", { class: "card" });
    box.appendChild(el("div", { class: "row between" },
      el("strong", { text: name }),
      el("span", {
        class: "badge " + (info.ok ? "ok" : "bad"),
        text: info.ok ? "آنلاین" : "آفلاین",
      })));
    box.appendChild(el("div", { class: "mt-8 muted", text: detailText(name, detail) }));
    return box;
  }
  function detailText(name, d) {
    if (name === "Agnes AI") {
      return d.ok ? `مدل: ${d.model || "—"}` : `خطا: ${(d.error || "").slice(0, 80)}`;
    }
    if (name === "GitHub") {
      if (d.ok) return `ریپو: ${d.repo} • شاخه: ${d.branch}`;
      return `خطا: ${(d.error || "").slice(0, 80)}`;
    }
    return JSON.stringify(d).slice(0, 120);
  }

  // ------------------------------------------------------------------
  // Page: Auto-Fetch
  // ------------------------------------------------------------------
  let _afPollTimer = null;
  let _afLastTs = null;

  function renderAutofetch(root) {
    // Layout: top control bar, log box, review queue
    const controls = el("div", { class: "card mb-24" });
    controls.appendChild(el("div", { class: "section-title" }, "پیکربندی دریافت"));
    const form = el("div", { class: "row" });
    const countInput = el("input", {
      type: "number", id: "af-count", value: "10", min: "1", max: "50",
      style: "width:100px;",
    });
    form.appendChild(el("label", { class: "field", style: "margin-bottom:0; flex:0 0 auto;" },
      el("span", { text: "تعداد مادها (1–50)" }), countInput));
    const startBtn = el("button", { class: "btn btn-primary", text: "⚡ شروع" });
    const stopBtn  = el("button", { class: "btn", text: "■ توقف", disabled: true });
    const resetBtn = el("button", { class: "btn btn-ghost", text: "↺ پاک‌سازی" });
    form.appendChild(el("div", { class: "row" }, startBtn, stopBtn, resetBtn));
    controls.appendChild(form);
    root.appendChild(controls);

    // ---- Live status bar ----
    const statusCard = el("div", { class: "card mb-24" });
    const statusRow = el("div", { class: "row between" });
    const statusText = el("span", { class: "badge idle", text: "آماده" });
    const progressWrap = el("div", { class: "progress", style: "flex:1; margin:0 16px;" });
    const progressFill = el("div", {});
    progressWrap.appendChild(progressFill);
    statusRow.appendChild(statusText);
    statusRow.appendChild(progressWrap);
    statusRow.appendChild(el("span", { id: "af-progress-text", class: "mono faint", text: "0 / 0" }));
    statusCard.appendChild(statusRow);
    root.appendChild(statusCard);

    // ---- Log box ----
    const logCard = el("div", { class: "card mb-24" });
    logCard.appendChild(el("div", { class: "section-title" }, "لاگ زنده"));
    const logBox = el("div", { class: "log-box", id: "af-log" });
    logBox.appendChild(el("div", { class: "faint", text: "منتظر شروع…" }));
    logCard.appendChild(logBox);
    root.appendChild(logCard);

    // ---- Review queue ----
    const queueCard = el("div", { class: "card" });
    queueCard.appendChild(el("div", { class: "section-title" },
      "صف بازبینی — تأیید یا رد کنید"));
    const queueGrid = el("div", { class: "review-grid", id: "af-queue" });
    queueCard.appendChild(queueGrid);
    root.appendChild(queueCard);

    // ---- Wire up ----
    startBtn.addEventListener("click", async () => {
      const n = parseInt(countInput.value, 10);
      if (!n || n < 1 || n > 50) { toast("عدد باید بین ۱ و ۵۰ باشد", "error"); return; }
      try {
        await API.post("/api/autofetch/start", { count: n });
        _afLastTs = null;
        clear(logBox);
        toast("دریافت خودکار آغاز شد", "info");
      } catch (e) { toast(e.message, "error"); }
    });
    stopBtn.addEventListener("click", async () => {
      try { await API.post("/api/autofetch/stop", {}); toast("درخواست توقف ارسال شد", "info"); }
      catch (e) { toast(e.message, "error"); }
    });
    resetBtn.addEventListener("click", async () => {
      if (!confirm("پاک‌سازی صف و لاگ؟")) return;
      try { await API.post("/api/autofetch/reset", {}); _afLastTs = null;
        clear(logBox); clear(queueGrid); toast("بازنشانی شد", "info"); }
      catch (e) { toast(e.message, "error"); }
    });

    // ---- Poll loop ----
    if (_afPollTimer) clearInterval(_afPollTimer);
    async function poll() {
      let s;
      try { s = await API.get("/api/autofetch/status"); }
      catch (e) { return; }

      // Status badge
      statusText.className = "badge " + (s.running ? "ok" : (s.error ? "bad" : "idle"));
      statusText.textContent = s.running ? "در حال اجرا"
        : (s.error ? "خطا" : (s.finished_at ? "تکمیل شد" : "آماده"));

      startBtn.disabled = s.running;
      stopBtn.disabled = !s.running;

      // Progress
      const pct = s.total ? Math.min(100, Math.round(s.processed / s.total * 100)) : 0;
      progressFill.style.width = pct + "%";
      $("#af-progress-text").textContent = `${s.processed} / ${s.total}`;

      // Log (append new lines only)
      if (s.log && s.log.length) {
        // If lastTs is null or we missed entries, re-render everything once
        const newEntries = !_afLastTs ? s.log :
          s.log.filter(l => l.t > _afLastTs || true);
        // Simpler: re-render visible portion
        if (logBox.firstChild && logBox.firstChild.className === "faint") clear(logBox);
        // Render last 200 entries
        clear(logBox);
        for (const line of s.log.slice(-200)) {
          const div = el("div", {
            class: "log-line " + (line.phase === "error" || line.phase === "fatal" ? "error"
              : line.phase === "done" ? "done" : ""),
          });
          div.appendChild(el("span", { class: "ph", text: `[${line.phase}]` }));
          div.appendChild(el("span", { class: "msg", text: " " + line.msg }));
          div.appendChild(el("span", { class: "ts", text: fmtTime(line.t) }));
          logBox.appendChild(div);
        }
        logBox.scrollTop = logBox.scrollHeight;
        _afLastTs = s.log[s.log.length - 1].t;
      }

      // Queue
      renderQueue(queueGrid, s.queue || []);
    }
    poll();
    _afPollTimer = setInterval(poll, 2000);

    // Clean up when leaving the page
    const unbind = () => {
      if (_afPollTimer) { clearInterval(_afPollTimer); _afPollTimer = null; }
      window.removeEventListener("hashchange", unbind);
    };
    window.addEventListener("hashchange", unbind);
  }

  function renderQueue(grid, queue) {
    if (!queue.length) {
      if (!grid.childElementCount || grid.firstChild.className !== "empty") {
        clear(grid);
        grid.appendChild(el("div", { class: "empty", style: "grid-column:1/-1;",
          text: "هنوز مادی در صف نیست — شروع کنید." }));
      }
      return;
    }
    clear(grid);
    for (const mod of queue) {
      grid.appendChild(reviewCard(mod, /*fromQueue*/true));
    }
  }

  function reviewCard(mod, fromQueue) {
    const card = el("div", { class: "review-card" });
    const cover = mod.cover
      ? el("img", { class: "cover", src: mod.cover, alt: mod.nameFa || mod.name,
        onerror() { this.style.display = "none"; } })
      : el("div", { class: "cover", style: "display:grid;place-items:center;color:var(--text-faint);",
          text: "بدون کاور" });

    const body = el("div", { class: "body" });
    body.appendChild(el("h3", { text: mod.nameFa || mod.name }));
    if (mod.tagline) body.appendChild(el("div", { class: "tagline", text: mod.tagline }));
    if (mod.aiGenerated) body.appendChild(el("span", { class: "tag-ai", text: "AI" }));

    const desc = el("div", { class: "desc" });
    desc.innerHTML = (mod.description || mod.desc || "").slice(0, 400);
    body.appendChild(desc);

    // Meta chips
    const chips = el("div", { class: "chips" });
    if (mod.category) chips.appendChild(el("span", { class: "chip", text: mod.category }));
    if (mod.version) chips.appendChild(el("span", { class: "chip", text: "v" + mod.version }));
    if (mod.author) chips.appendChild(el("span", { class: "chip", text: mod.author }));
    (mod.keywords || []).slice(0, 4).forEach(k =>
      chips.appendChild(el("span", { class: "chip", text: k })));
    body.appendChild(chips);

    const actions = el("div", { class: "actions" });
    actions.appendChild(el("button", {
      class: "btn btn-sm btn-primary", text: "✓ تأیید و ذخیره",
      onclick: () => approveMod(mod),
    }));
    actions.appendChild(el("button", {
      class: "btn btn-sm", text: "✎ ویرایش",
      onclick: () => openEditModal(mod),
    }));
    if (fromQueue) {
      actions.appendChild(el("button", {
        class: "btn btn-sm btn-danger", text: "✕ رد",
        onclick: () => rejectMod(mod.id || mod.slug),
      }));
    }

    card.appendChild(cover);
    card.appendChild(body);
    card.appendChild(actions);
    return card;
  }

  async function approveMod(mod) {
    try {
      const r = await API.post("/api/mods/approve", { mod: mod, push: true });
      if (r.push && !r.push.ok) {
        toast(`ذخیره شد ولی GitHub خطا داد: ${r.push.error}`, "error");
      } else {
        toast(`«${mod.nameFa || mod.name}» ذخیره شد ✓`, "info");
      }
    } catch (e) { toast(e.message, "error"); }
  }
  async function rejectMod(id) {
    if (!id) return;
    try { await API.post(`/api/mods/${id}/reject`, {}); toast("رد شد", "info"); }
    catch (e) { toast(e.message, "error"); }
  }

  function openEditModal(mod) {
    openModal("ویرایش ماد", body => {
      const form = el("div", {});
      const fields = [
        ["nameFa", "نام فارسی", "text"],
        ["tagline", "تگ‌لاین", "text"],
        ["category", "دسته‌بندی", "text"],
        ["version", "نسخه", "text"],
        ["author", "سازنده", "text"],
        ["cover", "آدرس کاور", "url"],
        ["download", "دستورالعمل نصب", "text"],
      ];
      const inputs = {};
      for (const [key, label, type] of fields) {
        const i = el("input", { type, value: mod[key] || "" });
        inputs[key] = i;
        form.appendChild(el("label", { class: "field" },
          el("span", { text: label }), i));
      }
      const descTa = el("textarea", {});
      descTa.value = mod.description || mod.desc || "";
      form.appendChild(el("label", { class: "field" },
        el("span", { text: "توضیحات (مارک‌داون)" }), descTa));

      const kwInput = el("input", { type: "text",
        value: (mod.keywords || []).join(", ") });
      form.appendChild(el("label", { class: "field" },
        el("span", { text: "کلمات کلیدی (با ویرگول جدا کنید)" }), kwInput));

      body.appendChild(form);

      const actions = el("div", { class: "row", style: "justify-content:flex-end; margin-top:16px;" });
      actions.appendChild(el("button", { class: "btn btn-ghost", text: "انصراف", onclick: closeModal }));
      actions.appendChild(el("button", { class: "btn btn-primary", text: "ذخیره و تأیید", onclick: async () => {
        const updated = Object.assign({}, mod);
        for (const [k] of fields) updated[k] = inputs[k].value.trim();
        updated.description = descTa.value;
        updated.keywords = kwInput.value.split(",").map(s => s.trim()).filter(Boolean);
        closeModal();
        await approveMod(updated);
      }}));
      body.appendChild(actions);
    });
  }

  // ------------------------------------------------------------------
  // Page: Single URL Crawl
  // ------------------------------------------------------------------
  function renderCrawl(root) {
    const card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "section-title" }, "دریافت یک ماد از MCPEDL"));
    card.appendChild(el("p", { class: "muted mb-16" },
      "آدرس کامل صفحه ماد را از mcpedl.com وارد کنید."));
    const urlInput = el("input", {
      type: "url", placeholder: "https://mcpedl.com/example-mod/",
      style: "direction:ltr; text-align:left;",
    });
    card.appendChild(el("label", { class: "field" },
      el("span", { text: "آدرس MCPEDL" }), urlInput));

    const row = el("div", { class: "row" });
    const crawlBtn = el("button", { class: "btn btn-primary", text: "◐ دریافت و تحلیل" });
    row.appendChild(crawlBtn);
    card.appendChild(row);

    const resultWrap = el("div", { class: "mt-24" });
    card.appendChild(resultWrap);

    crawlBtn.addEventListener("click", async () => {
      const url = urlInput.value.trim();
      if (!url) { toast("آدرس را وارد کنید", "error"); return; }
      clear(resultWrap);
      resultWrap.appendChild(el("div", { class: "loading" }, "در حال دریافت صفحه و تحلیل AI …"));
      try {
        const r = await API.post("/api/crawl", { url });
        clear(resultWrap);
        if (!r.mod) throw new Error("پاسخ نامعتبر");
        resultWrap.appendChild(el("div", { class: "section-title" }, "نتیجه بازبینی"));
        const grid = el("div", { class: "review-grid" });
        grid.appendChild(reviewCard(r.mod, /*fromQueue*/false));
        resultWrap.appendChild(grid);
        if (r.ai && !r.ai._ai_used) {
          resultWrap.appendChild(el("div", { class: "muted mt-16", style: "text-align:center;" },
            "⚠ محتوای AI استفاده نشد — حالت خاموش روی داده‌های خام"));
        }
      } catch (e) {
        clear(resultWrap);
        resultWrap.appendChild(el("div", { class: "card" },
          el("strong", { text: "خطا" }),
          el("p", { class: "muted mt-8", text: e.message })));
      }
    });
    root.appendChild(card);
  }

  // ------------------------------------------------------------------
  // Page: Mods
  // ------------------------------------------------------------------
  async function renderMods(root) {
    root.appendChild(el("div", { class: "loading" }, "در حال بارگذاری…"));

    let data;
    try { data = await API.get("/api/mods"); }
    catch (e) {
      clear(root);
      root.appendChild(el("div", { class: "card" },
        el("h3", { text: "خطا" }),
        el("p", { class: "muted" }, e.message)));
      return;
    }
    const allMods = data.mods || [];

    // ---- Top controls ----
    const top = el("div", { class: "card mb-24" });
    top.appendChild(el("div", { class: "section-title" }, `مدیریت مادها (${allMods.length})`));
    const row = el("div", { class: "row" });
    const search = el("input", {
      type: "text", placeholder: "جستجوی نام، سازنده، کلمه کلیدی…",
      style: "flex:1; direction:ltr;",
    });
    const pushBtn = el("button", { class: "btn", text: "⇪ ارسال به GitHub" });
    row.appendChild(search);
    row.appendChild(pushBtn);
    top.appendChild(row);
    root.appendChild(top);

    // ---- Table ----
    const wrap = el("div", { class: "table-wrap" });
    const tableScroll = el("div", { style: "max-height:62vh; overflow:auto;" });
    const tbl = el("table", { class: "tbl" });
    tbl.appendChild(el("thead", {},
      el("tr", {},
        el("th", { text: "کاور" }),
        el("th", { text: "نام" }),
        el("th", { text: "دسته" }),
        el("th", { text: "نسخه" }),
        el("th", { text: "AI" }),
        el("th", { text: "عملیات" }),
      )));
    const tbody = el("tbody", {});
    tbl.appendChild(tbody);
    tableScroll.appendChild(tbl);
    wrap.appendChild(tableScroll);
    root.appendChild(wrap);

    function renderRows(list) {
      clear(tbody);
      if (!list.length) {
        const tr = el("tr", {});
        tr.appendChild(el("td", { colspan: 6, style: "text-align:center;" },
          el("div", { class: "empty", text: "مادی یافت نشد" })));
        tbody.appendChild(tr);
        return;
      }
      for (const m of list) {
        const tr = el("tr", {});
        // Cover
        const coverCell = el("td", {});
        const coverWrap = el("div", { class: "cell-cover" });
        if (m.cover) {
          coverWrap.appendChild(el("img", { src: m.cover, alt: "",
            onerror() { this.style.visibility = "hidden"; } }));
        }
        coverWrap.appendChild(el("strong", { text: m.nameFa || m.name || m.id }));
        coverCell.appendChild(coverWrap);
        tr.appendChild(coverCell);
        // Category
        tr.appendChild(el("td", { text: m.category || "—" }));
        // Version
        tr.appendChild(el("td", { class: "mono", text: m.version || "—" }));
        // AI
        tr.appendChild(el("td", {},
          m.aiGenerated ? el("span", { class: "tag-ai", text: "AI" })
            : el("span", { class: "faint", text: "—" })));
        // Actions
        const act = el("td", {});
        act.appendChild(el("button", {
          class: "btn btn-sm", text: "✎",
          onclick: () => openEditModal(m),
        }));
        act.appendChild(el("button", {
          class: "btn btn-sm btn-danger", text: "✕",
          style: "margin-right:6px;",
          onclick: () => deleteMod(m.id || m.slug, m.nameFa || m.name, () => renderRows(filterList())),
        }));
        tr.appendChild(act);
        tbody.appendChild(tr);
      }
    }

    function filterList() {
      const q = search.value.trim().toLowerCase();
      if (!q) return allMods;
      return allMods.filter(m => {
        return [m.name, m.nameFa, m.author, m.category, m.id,
          ...(m.keywords || [])].some(v => v && String(v).toLowerCase().includes(q));
      });
    }

    search.addEventListener("input", () => renderRows(filterList()));
    renderRows(allMods);

    pushBtn.addEventListener("click", async () => {
      pushBtn.disabled = true;
      pushBtn.textContent = "در حال ارسال…";
      try {
        const r = await API.post("/api/mods/save-all", {});
        if (r.ok) toast(`ارسال به GitHub شد ✓ (${r.commit_sha || ""})`, "info");
        else toast("خطا در ارسال: " + (r.error || ""), "error");
      } catch (e) { toast(e.message, "error"); }
      pushBtn.disabled = false;
      pushBtn.textContent = "⇪ ارسال به GitHub";
    });
  }

  async function deleteMod(id, name, after) {
    if (!confirm(`حذف «${name}»؟ این عمل قابل بازگشت نیست (محلی).`)) return;
    try { await API.del(`/api/mods/${id}`); toast("حذف شد", "info"); if (after) after(); }
    catch (e) { toast(e.message, "error"); }
  }

  // ------------------------------------------------------------------
  // Page: Settings
  // ------------------------------------------------------------------
  async function renderSettings(root) {
    root.appendChild(el("div", { class: "loading" }, "در حال بارگذاری…"));

    let data;
    try { data = await API.get("/api/settings"); }
    catch (e) { clear(root); root.appendChild(el("div", { class: "card" }, e.message)); return; }

    const s = data.settings || {};
    clear(root);

    // ---- Env file info ----
    root.appendChild(el("div", { class: "card mb-24" },
      el("div", { class: "section-title" }, "فایل پیکربندی"),
      el("div", { class: "row" },
        el("span", { class: "muted", text: "مسیر:" }),
        el("code", { class: "mono", text: data.env_path })),
      el("div", { class: "mt-8 row" },
        el("span", { class: "muted", text: "وضعیت:" }),
        data.env_exists
          ? el("span", { class: "badge ok", text: "موجود" })
          : el("span", { class: "badge bad", text: "مفقود — ایجاد می‌شود" })),
    ));

    // ---- Token form ----
    const card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "section-title" }, "توکن‌ها و مسیرها"));
    const inputs = {};
    const fields = [
      ["AGNES_API_KEY", "کلید Agnes AI", "password"],
      ["AGNES_BASE_URL", "آدرس پایه Agnes", "url"],
      ["AGNES_MODEL", "مدل Agnes", "text"],
      ["GITHUB_TOKEN", "توکن GitHub", "password"],
      ["GITHUB_USER", "کاربر GitHub", "text"],
      ["GITHUB_REPO", "ریپو GitHub", "text"],
      ["GITHUB_BRANCH", "شاخه GitHub", "text"],
      ["HF_TOKEN", "توکن HuggingFace", "password"],
      ["ASTRO_DATA_PATH", "مسیر داده Astro", "text"],
      ["MODS_JSON_PATH", "مسیر mods.json", "text"],
    ];
    for (const [key, label, type] of fields) {
      const i = el("input", { type, value: s[key] || "" });
      // show full secret on focus
      i.addEventListener("focus", () => { if (i.type === "password") i.type = "text"; });
      i.addEventListener("blur", () => {
        if (["AGNES_API_KEY", "GITHUB_TOKEN", "HF_TOKEN"].includes(key))
          i.type = "password";
      });
      inputs[key] = i;
      card.appendChild(el("label", { class: "field" },
        el("span", { text: `${label} (${key})` }), i));
    }

    const row = el("div", { class: "row", style: "justify-content:flex-end; margin-top:16px;" });
    const saveBtn = el("button", { class: "btn btn-primary", text: "💾 ذخیره" });
    row.appendChild(saveBtn);
    card.appendChild(row);
    root.appendChild(card);

    saveBtn.addEventListener("click", async () => {
      const body = {};
      for (const [k] of fields) body[k] = inputs[k].value.trim();
      saveBtn.disabled = true;
      saveBtn.textContent = "در حال ذخیره…";
      try {
        await API.put("/api/settings", body);
        toast("تنظیمات ذخیره شد ✓", "info");
      } catch (e) { toast(e.message, "error"); }
      saveBtn.disabled = false;
      saveBtn.textContent = "💾 ذخیره";
    });
  }

  // ------------------------------------------------------------------
  // Server badge (always-on health check)
  // ------------------------------------------------------------------
  async function serverHealthLoop() {
    const badge = $("#server-badge");
    while (true) {
      try {
        const r = await fetch("/api/health");
        if (r.ok) {
          badge.className = "server-badge ok";
          badge.textContent = "● سرور آنلاین";
        } else throw 0;
      } catch {
        badge.className = "server-badge bad";
        badge.textContent = "● سرور آفلاین";
      }
      await new Promise(r => setTimeout(r, 8000));
    }
  }
  document.addEventListener("DOMContentLoaded", serverHealthLoop);

  // Expose a tiny API for debugging in the webview console
  window.MineBed = { API, toast, openModal, closeModal };
})();
