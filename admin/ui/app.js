/* =========================================================================
   MineBed Admin — main front-end logic (v1.1.0 — fully audited & expanded).

   Highlights vs v1.0.0:
     • Auth flow: probe /api/auth/status; if auth_enabled, show login screen
       and store the admin token in localStorage. Every API call attaches
       ``Authorization: Bearer <token>`` automatically.
     • Settings page no longer overwrites secrets with masked placeholders
       (the backend skips any submitted value that contains ``*``).
     • Mods list: keywords search treats the field as a space-separated
       string (the website's Mod type), not as an array.
     • Mods list: inline cell editing (click-to-edit on name, tagline,
       version, size, author) with a single PATCH /api/mods/{id}/field.
     • Mods list: bulk operations (select multiple rows → feature /
       unfeature / set-new / unset-new / set-category / bulk delete).
     • New Stats page with breakdowns by category, version, and service
       health (downloads count, AI usage over time, etc.).
     • New Logs page: tails admin server log + autofetch log in real time
       (polling every 2s; also supports an SSE stream endpoint).
     • Auto-Fetch poll loop: removed broken dedup logic; properly cleans
       up its interval on page change.
     • Server-health loop: now properly stoppable on logout.
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
      if (typeof c === "string" || typeof c === "number")
        node.appendChild(document.createTextNode(String(c)));
      else node.appendChild(c);
    }
    return node;
  }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); return node; }

  function fmtTime(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    if (isNaN(d)) return String(iso);
    return d.toLocaleTimeString("fa-IR",
      { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, c => (
      { "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]
    ));
  }

  // ------------------------------------------------------------------
  // Auth state
  // ------------------------------------------------------------------
  const TOKEN_KEY = "minebed_admin_token";
  function getToken() { return localStorage.getItem(TOKEN_KEY) || ""; }
  function setToken(t) {
    if (t) localStorage.setItem(TOKEN_KEY, t);
    else localStorage.removeItem(TOKEN_KEY);
  }

  function authHeader() {
    const t = getToken();
    return t ? { "Authorization": "Bearer " + t } : {};
  }

  // ------------------------------------------------------------------
  // API client (now attaches the auth header to every call)
  // ------------------------------------------------------------------
  async function apiFetch(path, opts) {
    opts = opts || {};
    const headers = Object.assign(
      { "Content-Type": "application/json" },
      authHeader(),
      opts.headers || {},
    );
    const r = await fetch(path, Object.assign({}, opts, { headers }));
    const text = await r.text();
    let data; try { data = JSON.parse(text); } catch { data = { raw: text }; }
    if (r.status === 401) {
      // Token bad/expired — clear and force re-login
      setToken("");
      showLogin();
      throw new Error((data && data.error) || "Unauthorized — لطفاً دوباره وارد شوید");
    }
    if (!r.ok) {
      const msg = (data && (data.error || data.detail || data.raw))
        || `${opts.method || "GET"} ${path} → ${r.status}`;
      throw new Error(msg);
    }
    return data;
  }

  const API = {
    get(path) { return apiFetch(path, { method: "GET" }); },
    post(path, body) {
      return apiFetch(path, {
        method: "POST",
        body: JSON.stringify(body || {}),
      });
    },
    put(path, body) {
      return apiFetch(path, {
        method: "PUT",
        body: JSON.stringify(body || {}),
      });
    },
    patch(path, body) {
      return apiFetch(path, {
        method: "PATCH",
        body: JSON.stringify(body || {}),
      });
    },
    del(path) {
      return apiFetch(path, { method: "DELETE" });
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

  // ------------------------------------------------------------------
  // Login screen
  // ------------------------------------------------------------------
  function showApp() {
    $("#login-screen").classList.add("hidden");
    $("#app").classList.remove("hidden");
  }
  function showLogin() {
    $("#app").classList.add("hidden");
    $("#login-screen").classList.remove("hidden");
    const tok = $("#login-token");
    if (tok) tok.focus();
  }

  async function probeAuthAndBoot() {
    let st;
    try { st = await API.get("/api/auth/status"); }
    catch (e) { showLogin(); return; }

    if (!st.auth_enabled) {
      // open mode — no login required
      setToken("");
      showApp();
      render();
      startServerHealthLoop();
      return;
    }

    // Auth required — do we have a stored token?  Validate it.
    const t = getToken();
    if (t) {
      try {
        // Hit /api/dashboard to validate the token
        await API.get("/api/dashboard");
        showApp();
        render();
        startServerHealthLoop();
        return;
      } catch {
        setToken("");
        // fall through to login
      }
    }
    showLogin();
  }

  function bindLoginScreen() {
    const form = $("#login-form");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const tok = $("#login-token").value.trim();
      const errBox = $("#login-error");
      errBox.classList.add("hidden");
      errBox.textContent = "";
      if (!tok) {
        errBox.textContent = "رمز را وارد کنید";
        errBox.classList.remove("hidden");
        return;
      }
      const btn = $("#login-submit");
      btn.disabled = true;
      btn.textContent = "در حال ورود…";
      try {
        const r = await API.post("/api/auth/login", { token: tok });
        if (!r.ok) throw new Error(r.error || "ناموفق");
        setToken(tok);
        showApp();
        render();
        startServerHealthLoop();
      } catch (e) {
        errBox.textContent = e.message || "خطا در ورود";
        errBox.classList.remove("hidden");
      } finally {
        btn.disabled = false;
        btn.textContent = "ورود";
      }
    });

    const logoutBtn = $("#logout-btn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        setToken("");
        if (_healthTimer) { clearInterval(_healthTimer); _healthTimer = null; }
        showLogin();
      });
    }
  }

  // ------------------------------------------------------------------
  // Router
  // ------------------------------------------------------------------
  const PAGES = {
    dashboard: { title: "داشبورد", render: renderDashboard },
    autofetch: { title: "دریافت خودکار", render: renderAutofetch },
    crawl:     { title: "دریافت تکی", render: renderCrawl },
    mods:      { title: "مادها", render: renderMods },
    stats:     { title: "آمار", render: renderStats },
    logs:      { title: "لاگ‌ها", render: renderLogs },
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
    stats.appendChild(statCard("نسخه‌ها", data.versions_count, "فایل versions.json"));
    stats.appendChild(statCard("وضعیت Auto-Fetch",
      data.autofetch_running ? "در حال اجرا" : "آماده",
      data.autofetch_running ? "در حال پردازش" : "سیستم بیکار",
      data.autofetch_running ? "ok" : "idle"));
    root.appendChild(stats);

    // ---- Services ----
    const services = el("div", { class: "card mb-24" });
    services.appendChild(el("div", { class: "section-title" }, "وضعیت سرویس‌ها"));
    const sGrid = el("div", { class: "grid grid-3" });
    sGrid.appendChild(serviceBox("Agnes AI", data.services.agnes));
    sGrid.appendChild(serviceBox("GitHub", data.services.github));
    sGrid.appendChild(serviceBox("HuggingFace", data.services.huggingface));
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
    row.appendChild(el("a", {
      class: "btn", href: "#/stats", text: "▤ آمار",
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
      el("div", { class: "stat-value", text: String(value) }),
      sub ? el("div", { class: "stat-sub", text: sub }) : null,
    );
  }
  function serviceBox(name, info) {
    info = info || { ok: false, detail: { error: "نامشخص" } };
    const detail = info.detail || info;  // huggingface returns {configured, repo}
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
    if (name === "HuggingFace") {
      return d.configured ? `ریپو: ${d.repo || "—"}` : "پیکربندی نشده";
    }
    return JSON.stringify(d).slice(0, 120);
  }

  // ------------------------------------------------------------------
  // Page: Auto-Fetch
  // ------------------------------------------------------------------
  let _afPollTimer = null;

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
      try { await API.post("/api/autofetch/reset", {});
        clear(logBox); clear(queueGrid);
        logBox.appendChild(el("div", { class: "faint", text: "منتظر شروع…" }));
        toast("بازنشانی شد", "info");
      } catch (e) { toast(e.message, "error"); }
    });

    // ---- Poll loop (simplified — full re-render each tick) ----
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

      // Log — re-render the last 200 entries every tick (simple & correct).
      // Previous version had dead dedup code (filter with `|| true`).
      if (s.log && s.log.length) {
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
      } else if (!logBox.childElementCount) {
        logBox.appendChild(el("div", { class: "faint", text: "منتظر شروع…" }));
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
    desc.textContent = (mod.description || mod.desc || "").slice(0, 400);
    desc.style.whiteSpace = "pre-wrap";
    desc.style.wordBreak = "break-word";
    body.appendChild(desc);

    // Meta chips — keywords is a SPACE-SEPARATED STRING per the website's
    // Mod type (NOT an array).  Normalize both for safety.
    const keywordsArr = (() => {
      const kw = mod.keywords;
      if (Array.isArray(kw)) return kw;
      if (typeof kw === "string") return kw.split(/\s+/).filter(Boolean);
      return [];
    })();

    const chips = el("div", { class: "chips" });
    if (mod.catName || mod.category) {
      chips.appendChild(el("span", { class: "chip",
        text: mod.catName || mod.category }));
    }
    if (mod.version) chips.appendChild(el("span", { class: "chip", text: "v" + mod.version }));
    if (mod.author) chips.appendChild(el("span", { class: "chip", text: mod.author }));
    keywordsArr.slice(0, 4).forEach(k =>
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

  // ------------------------------------------------------------------
  // Edit modal — now updates catName when category changes (so the
  // website's category labels stay in sync).
  // ------------------------------------------------------------------
  const CAT_NAME_MAP = {
    gameplay: "گیم\u200cپلی",
    graphics: "گرافیک",
    maps: "مپ",
    mobs: "موجودات",
    decoration: "دکوراسیون",
    world: "دنیا",
    utility: "ابزار",
  };

  function openEditModal(mod) {
    openModal("ویرایش ماد", body => {
      const form = el("div", {});
      const fields = [
        ["nameFa", "نام فارسی", "text"],
        ["name", "نام انگلیسی", "text"],
        ["tagline", "تگ‌لاین", "text"],
        ["category", "دسته", "text"],
        ["version", "نسخه ماینکرفت", "text"],
        ["author", "سازنده", "text"],
        ["cover", "آدرس کاور (URL)", "url"],
        ["downloadUrl", "آدرس دانلود (URL)", "url"],
        ["size", "حجم فایل", "text"],
        ["updated", "تاریخ آپدیت (YYYY-MM-DD)", "text"],
      ];
      const inputs = {};
      for (const [key, label, type] of fields) {
        const i = el("input", { type, value: mod[key] || "",
          style: type === "url" || key === "version" || key === "updated"
            ? "direction:ltr; text-align:left;" : "" });
        inputs[key] = i;
        form.appendChild(el("label", { class: "field" },
          el("span", { text: label }), i));
      }

      // Category dropdown (better UX than free-text)
      const catSelect = el("select", {});
      for (const [id, name] of Object.entries(CAT_NAME_MAP)) {
        const o = el("option", { value: id, text: `${name} (${id})` });
        if (mod.category === id) o.setAttribute("selected", "");
        catSelect.appendChild(o);
      }
      inputs.category.replaceWith(catSelect);
      inputs.category = catSelect;

      const descTa = el("textarea", { rows: "6" });
      descTa.value = mod.description || mod.desc || "";
      form.appendChild(el("label", { class: "field" },
        el("span", { text: "توضیحات (مارک‌داون)" }), descTa));

      // keywords is a space-separated string (website's Mod type)
      const kwStr = Array.isArray(mod.keywords)
        ? mod.keywords.join(" ")
        : (mod.keywords || "");
      const kwInput = el("input", { type: "text", value: kwStr,
        style: "direction:ltr; text-align:left;" });
      form.appendChild(el("label", { class: "field" },
        el("span", { text: "کلمات کلیدی (با فاصله جدا کنید)" }),
        kwInput));

      // Featured / New flags
      const flagsRow = el("div", { class: "row",
        style: "gap:16px; margin-top:8px;" });
      const featCb = el("input", { type: "checkbox" });
      if (mod.featured) featCb.setAttribute("checked", "");
      const newCb = el("input", { type: "checkbox" });
      if (mod.isNew) newCb.setAttribute("checked", "");
      flagsRow.appendChild(el("label", { class: "field",
        style: "flex-direction:row; align-items:center; gap:6px; margin:0;" },
        featCb, el("span", { text: "ویژه (featured)" })));
      flagsRow.appendChild(el("label", { class: "field",
        style: "flex-direction:row; align-items:center; gap:6px; margin:0;" },
        newCb, el("span", { text: "جدید (isNew)" })));
      form.appendChild(flagsRow);

      body.appendChild(form);

      const actions = el("div", { class: "row",
        style: "justify-content:flex-end; margin-top:16px;" });
      actions.appendChild(el("button", { class: "btn btn-ghost",
        text: "انصراف", onclick: closeModal }));
      actions.appendChild(el("button", { class: "btn btn-primary",
        text: "💾 ذخیره و ارسال",
        onclick: async () => {
          const updated = Object.assign({}, mod);
          for (const [k] of fields) {
            updated[k] = inputs[k].value.trim();
          }
          // Update catName from category (always — never trust stale data)
          updated.catName = CAT_NAME_MAP[updated.category] || updated.category;
          updated.description = descTa.value;
          updated.desc = descTa.value;
          updated.keywords = kwInput.value.trim();
          updated.featured = featCb.checked;
          updated.isNew = newCb.checked;
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
      resultWrap.appendChild(el("div", { class: "loading" },
        "در حال دریافت صفحه و تحلیل AI …"));
      crawlBtn.disabled = true;
      try {
        const r = await API.post("/api/crawl", { url });
        clear(resultWrap);
        if (!r.mod) throw new Error("پاسخ نامعتبر");
        resultWrap.appendChild(el("div", { class: "section-title" }, "نتیجه بازبینی"));
        const grid = el("div", { class: "review-grid" });
        grid.appendChild(reviewCard(r.mod, /*fromQueue*/false));
        resultWrap.appendChild(grid);
        if (r.ai && !r.ai._ai_used) {
          resultWrap.appendChild(el("div", {
            class: "muted mt-16", style: "text-align:center;" },
            "⚠ محتوای AI استفاده نشد — حالت خاموش روی داده‌های خام"));
        }
      } catch (e) {
        clear(resultWrap);
        resultWrap.appendChild(el("div", { class: "card" },
          el("strong", { text: "خطا" }),
          el("p", { class: "muted mt-8", text: e.message })));
      } finally {
        crawlBtn.disabled = false;
      }
    });
    root.appendChild(card);
  }

  // ------------------------------------------------------------------
  // Page: Mods — now with INLINE editing + BULK operations
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
    top.appendChild(el("div", { class: "section-title" },
      `مدیریت مادها (${allMods.length})`));
    const row = el("div", { class: "row" });
    const search = el("input", {
      type: "text", placeholder: "جستجوی نام، سازنده، کلمه کلیدی…",
      style: "flex:1; direction:ltr;",
    });
    const pushBtn = el("button", { class: "btn", text: "⇪ ارسال به GitHub" });
    row.appendChild(search);
    row.appendChild(pushBtn);
    top.appendChild(row);

    // ---- Bulk action bar (shown when rows are selected) ----
    const bulkBar = el("div", { class: "bulk-bar hidden" });
    const bulkInfo = el("span", { class: "mono", text: "0 انتخاب شده" });
    const bulkFeat = el("button", { class: "btn btn-sm", text: "★ ویژه کن" });
    const bulkUnfeat = el("button", { class: "btn btn-sm", text: "☆ غیر ویژه" });
    const bulkNew = el("button", { class: "btn btn-sm", text: "＋ جدید کن" });
    const bulkUnnew = el("button", { class: "btn btn-sm", text: "－ قدیمی" });
    const bulkCat = el("select", { class: "btn btn-sm", style: "padding:5px 10px;" });
    bulkCat.appendChild(el("option", { value: "", text: "→ تغییر دسته" }));
    for (const [id, name] of Object.entries(CAT_NAME_MAP)) {
      bulkCat.appendChild(el("option", { value: id, text: `${name} (${id})` }));
    }
    const bulkDel = el("button", { class: "btn btn-sm btn-danger", text: "✕ حذف" });
    bulkBar.append(bulkInfo, bulkFeat, bulkUnfeat, bulkNew, bulkUnnew,
      bulkCat, bulkDel);
    top.appendChild(bulkBar);
    root.appendChild(top);

    // ---- Table ----
    const wrap = el("div", { class: "table-wrap" });
    const tableScroll = el("div", { style: "max-height:62vh; overflow:auto;" });
    const tbl = el("table", { class: "tbl" });
    tbl.appendChild(el("thead", {},
      el("tr", {},
        el("th", { style: "width:32px;" },
          el("input", { type: "checkbox", id: "bulk-select-all" })),
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

    const selected = new Set();
    function updateBulkBar() {
      const n = selected.size;
      if (n > 0) bulkBar.classList.remove("hidden");
      else bulkBar.classList.add("hidden");
      bulkInfo.textContent = `${n} انتخاب شده`;
    }

    function renderRows(list) {
      clear(tbody);
      if (!list.length) {
        const tr = el("tr", {});
        tr.appendChild(el("td", { colspan: 7, style: "text-align:center;" },
          el("div", { class: "empty", text: "مادی یافت نشد" })));
        tbody.appendChild(tr);
        return;
      }
      for (const m of list) {
        const mid = m.id || m.slug;
        const tr = el("tr", {});
        // Checkbox
        const cbCell = el("td", {});
        const cb = el("input", { type: "checkbox" });
        cb.checked = selected.has(mid);
        cb.addEventListener("change", () => {
          if (cb.checked) selected.add(mid);
          else selected.delete(mid);
          updateBulkBar();
        });
        cbCell.appendChild(cb);
        tr.appendChild(cbCell);
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
        // Category (inline-editable via dropdown)
        const catCell = el("td", {});
        const catSel = el("select", {
          class: "inline-edit",
          style: "padding:3px 8px; font-size:12px;",
          onchange: async (e) => {
            const v = e.target.value;
            try {
              await API.patch(`/api/mods/${mid}/field`,
                { field: "category", value: v, push: false });
              m.category = v;
              m.catName = CAT_NAME_MAP[v] || v;
              toast(`دسته «${m.nameFa}» → ${CAT_NAME_MAP[v]}`, "info");
            } catch (err) { toast(err.message, "error"); e.target.value = m.category; }
          },
        });
        for (const [id, name] of Object.entries(CAT_NAME_MAP)) {
          const o = el("option", { value: id, text: name });
          if (m.category === id) o.setAttribute("selected", "");
          catSel.appendChild(o);
        }
        catCell.appendChild(catSel);
        tr.appendChild(catCell);
        // Version (inline-editable on dblclick)
        tr.appendChild(inlineEditCell(m, "version", mid, "mono"));
        // AI
        tr.appendChild(el("td", {},
          m.aiGenerated ? el("span", { class: "tag-ai", text: "AI" })
            : el("span", { class: "faint", text: "—" })));
        // Actions
        const act = el("td", {});
        const editBtn = el("button", { class: "btn btn-sm", text: "✎" });
        editBtn.addEventListener("click", () => openEditModal(m));
        act.appendChild(editBtn);
        const delBtn = el("button", {
          class: "btn btn-sm btn-danger", text: "✕",
          style: "margin-right:6px;",
        });
        delBtn.addEventListener("click", () =>
          deleteMod(m.id || m.slug, m.nameFa || m.name,
            () => renderRows(filterList())));
        act.appendChild(delBtn);
        tr.appendChild(act);
        tbody.appendChild(tr);
      }
    }

    function inlineEditCell(mod, field, mid, extraClass) {
      const td = el("td", { class: extraClass || "" });
      const span = el("span", { text: mod[field] || "—",
        title: "برای ویرایش دوبار کلیک کنید" });
      td.appendChild(span);
      td.addEventListener("dblclick", () => {
        const inp = el("input", { type: "text", value: mod[field] || "",
          style: "width:100%; padding:3px 6px;" });
        clear(td);
        td.appendChild(inp);
        inp.focus();
        inp.select();
        const commit = async () => {
          const v = inp.value.trim();
          if (v === (mod[field] || "")) {
            clear(td); td.appendChild(span); return;
          }
          try {
            await API.patch(`/api/mods/${mid}/field`,
              { field, value: v, push: false });
            mod[field] = v;
            span.textContent = v || "—";
            toast(`«${field}» ذخیره شد`, "info");
          } catch (e) {
            toast(e.message, "error");
          }
          clear(td); td.appendChild(span);
        };
        inp.addEventListener("blur", commit);
        inp.addEventListener("keydown", (e) => {
          if (e.key === "Enter") inp.blur();
          else if (e.key === "Escape") { clear(td); td.appendChild(span); }
        });
      });
      return td;
    }

    // BUGFIX: keywords is a SPACE-SEPARATED STRING per the website's
    // Mod type.  The old code did `...(m.keywords || [])` which spreads
    // a string into individual characters — search didn't work at all
    // for keyword queries.  Now we explicitly normalize to an array.
    function filterList() {
      const q = search.value.trim().toLowerCase();
      if (!q) return allMods;
      return allMods.filter(m => {
        const kwArr = Array.isArray(m.keywords)
          ? m.keywords
          : (typeof m.keywords === "string"
              ? m.keywords.split(/\s+/).filter(Boolean)
              : []);
        return [m.name, m.nameFa, m.author, m.category, m.catName, m.id,
          ...kwArr].some(v => v && String(v).toLowerCase().includes(q));
      });
    }

    search.addEventListener("input", () => renderRows(filterList()));
    renderRows(allMods);

    // ---- Select-all checkbox ----
    const selectAll = $("#bulk-select-all");
    if (selectAll) {
      selectAll.addEventListener("change", () => {
        const visible = filterList();
        if (selectAll.checked) {
          visible.forEach(m => selected.add(m.id || m.slug));
        } else {
          visible.forEach(m => selected.delete(m.id || m.slug));
        }
        renderRows(visible);
        updateBulkBar();
      });
    }

    // ---- Bulk action handlers ----
    async function bulkDo(action, value) {
      const ids = Array.from(selected);
      if (!ids.length) return;
      if (action === "delete" &&
          !confirm(`${ids.length} ماد حذف شود؟ (محلی — قابل بازگشت با push نیست)`)) return;
      try {
        const r = await API.post("/api/mods/bulk", { action, ids, value, push: false });
        toast(`${r.affected} ماد ${action} شد${r.push ? " ✓" : ""}`, "info");
        selected.clear();
        // reload list
        const fresh = await API.get("/api/mods");
        allMods.length = 0;
        allMods.push(...(fresh.mods || []));
        renderRows(filterList());
        updateBulkBar();
      } catch (e) { toast(e.message, "error"); }
    }
    bulkFeat.addEventListener("click", () => bulkDo("feature"));
    bulkUnfeat.addEventListener("click", () => bulkDo("unfeature"));
    bulkNew.addEventListener("click", () => bulkDo("setNew"));
    bulkUnnew.addEventListener("click", () => bulkDo("unsetNew"));
    bulkCat.addEventListener("change", (e) => {
      if (e.target.value) bulkDo("setCategory", e.target.value);
      e.target.value = "";
    });
    bulkDel.addEventListener("click", () => bulkDo("delete"));

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
  // Page: Stats — downloads, AI usage, breakdowns
  // ------------------------------------------------------------------
  let _statsTimer = null;
  async function renderStats(root) {
    root.appendChild(el("div", { class: "loading" }, "در حال بارگذاری…"));

    async function loadAndDraw() {
      let data;
      try { data = await API.get("/api/stats"); }
      catch (e) {
        clear(root);
        root.appendChild(el("div", { class: "card" },
          el("h3", { text: "خطا" }),
          el("p", { class: "muted" }, e.message)));
        return;
      }
      clear(root);

      const t = data.totals;
      const grid = el("div", { class: "stat-grid" });
      grid.appendChild(statCard("مادها", t.mods, "کل مادها در سایت"));
      grid.appendChild(statCard("مادهای AI", t.ai_mods, "تولیدشده با Agnes AI"));
      grid.appendChild(statCard("ویژه‌ها", t.featured, "مادهای featured"));
      grid.appendChild(statCard("جدیدها", t.new, "مادهای isNew"));
      grid.appendChild(statCard("سیدها", t.seeds, "فایل seeds.json"));
      grid.appendChild(statCard("نسخه‌ها", t.versions, "فایل versions.json"));
      grid.appendChild(statCard("مجموع دانلودها", t.total_downloads,
        "از فیلد downloads (هر ماد)"));
      root.appendChild(grid);

      // ---- Category breakdown ----
      const catCard = el("div", { class: "card mb-24" });
      catCard.appendChild(el("div", { class: "section-title" }, "تفکیک بر اساس دسته"));
      const catBars = el("div", { class: "bar-list" });
      const maxCat = Math.max(1, ...Object.values(data.by_category));
      for (const [cat, n] of Object.entries(data.by_category).sort((a,b) => b[1]-a[1])) {
        const name = CAT_NAME_MAP[cat] || cat;
        const pct = Math.round(n / maxCat * 100);
        catBars.appendChild(el("div", { class: "bar-row" },
          el("span", { class: "bar-label", text: `${name} (${cat})` }),
          el("div", { class: "bar-track" },
            el("div", { class: "bar-fill",
              style: `width:${pct}%;` })),
          el("span", { class: "bar-val mono", text: String(n) }),
        ));
      }
      catCard.appendChild(catBars);
      root.appendChild(catCard);

      // ---- Version breakdown ----
      const verCard = el("div", { class: "card mb-24" });
      verCard.appendChild(el("div", { class: "section-title" }, "تفکیک بر اساس نسخه"));
      const verBars = el("div", { class: "bar-list" });
      const maxVer = Math.max(1, ...Object.values(data.by_version));
      for (const [v, n] of Object.entries(data.by_version).sort((a,b) => b[1]-a[1])) {
        const pct = Math.round(n / maxVer * 100);
        verBars.appendChild(el("div", { class: "bar-row" },
          el("span", { class: "bar-label mono", text: v || "—" }),
          el("div", { class: "bar-track" },
            el("div", { class: "bar-fill",
              style: `width:${pct}%;` })),
          el("span", { class: "bar-val mono", text: String(n) }),
        ));
      }
      verCard.appendChild(verBars);
      root.appendChild(verCard);

      // ---- Service status ----
      const svcCard = el("div", { class: "card" });
      svcCard.appendChild(el("div", { class: "section-title" }, "وضعیت سرویس‌ها"));
      const svcGrid = el("div", { class: "grid grid-3" });
      svcGrid.appendChild(serviceBox("Agnes AI", data.services.agnes));
      svcGrid.appendChild(serviceBox("GitHub", data.services.github));
      svcGrid.appendChild(serviceBox("HuggingFace", data.services.huggingface));
      svcCard.appendChild(svcGrid);
      root.appendChild(svcCard);

      root.appendChild(el("div", { class: "muted mt-16", style: "text-align:center;" },
        `آخرین به‌روزرسانی: ${data.ts}`));
    }

    await loadAndDraw();
    if (_statsTimer) clearInterval(_statsTimer);
    _statsTimer = setInterval(loadAndDraw, 30000);
    const unbind = () => {
      if (_statsTimer) { clearInterval(_statsTimer); _statsTimer = null; }
      window.removeEventListener("hashchange", unbind);
    };
    window.addEventListener("hashchange", unbind);
  }

  // ------------------------------------------------------------------
  // Page: Logs — tail of admin server log + autofetch worker log
  // ------------------------------------------------------------------
  let _logsTimer = null;
  function renderLogs(root) {
    const card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "section-title" }, "لاگ سرور ادمین"));
    const controls = el("div", { class: "row mb-16" });
    const linesInput = el("input", { type: "number", value: "300", min: "50",
      max: "2000", style: "width:100px;" });
    controls.appendChild(el("label", { class: "field",
      style: "margin:0; flex:0 0 auto;" },
      el("span", { text: "تعداد خط" }), linesInput));
    const refreshBtn = el("button", { class: "btn btn-sm", text: "↻ تازه" });
    const autoCb = el("input", { type: "checkbox", checked: "" });
    const autoLbl = el("label", { class: "field",
      style: "margin:0; flex-direction:row; align-items:center; gap:6px;" },
      autoCb, el("span", { text: "auto-refresh (2s)" }));
    controls.append(refreshBtn, autoLbl);
    card.appendChild(controls);

    const logBox = el("div", { class: "log-box", style: "height:60vh;" });
    logBox.appendChild(el("div", { class: "faint", text: "در حال بارگذاری…" }));
    card.appendChild(logBox);
    root.appendChild(card);

    async function load() {
      const n = parseInt(linesInput.value, 10) || 300;
      let data;
      try { data = await API.get(`/api/logs?lines=${n}`); }
      catch (e) { clear(logBox); logBox.appendChild(el("div", { class: "error" },
        "خطا در دریافت لاگ: " + e.message)); return; }
      clear(logBox);
      if (!data.lines.length) {
        logBox.appendChild(el("div", { class: "faint",
          text: "(لاگ خالی است — اگر سرور را با minebed-desktop.py اجرا کرده‌اید، " +
                "log در admin/minebed-desktop.log نوشته می‌شود)" }));
        return;
      }
      for (const ln of data.lines) {
        const div = el("div", { class: "log-line" });
        // Highlight common error patterns
        const cls = /error|fatal|exception|traceback/i.test(ln) ? "error"
          : /warn/i.test(ln) ? "done"
          : "";
        if (cls) div.className += " " + cls;
        div.textContent = ln;
        logBox.appendChild(div);
      }
      logBox.scrollTop = logBox.scrollHeight;
    }

    refreshBtn.addEventListener("click", load);
    load();

    if (_logsTimer) clearInterval(_logsTimer);
    function syncTimer() {
      if (autoCb.checked) {
        if (!_logsTimer) {
          _logsTimer = setInterval(load, 2000);
        }
      } else {
        if (_logsTimer) { clearInterval(_logsTimer); _logsTimer = null; }
      }
    }
    autoCb.addEventListener("change", syncTimer);
    syncTimer();

    const unbind = () => {
      if (_logsTimer) { clearInterval(_logsTimer); _logsTimer = null; }
      window.removeEventListener("hashchange", unbind);
    };
    window.addEventListener("hashchange", unbind);
  }

  // ------------------------------------------------------------------
  // Page: Settings — now includes ADMIN_SECRET and HF_REPO_ID,
  // and never sends masked values back to the server.
  // ------------------------------------------------------------------
  async function renderSettings(root) {
    root.appendChild(el("div", { class: "loading" }, "در حال بارگذاری…"));

    let data;
    try { data = await API.get("/api/settings"); }
    catch (e) {
      clear(root);
      root.appendChild(el("div", { class: "card" }, e.message));
      return;
    }

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
      ["HF_REPO_ID", "ریپو HuggingFace", "text"],
      ["ADMIN_SECRET", "رمز ادمین (برای ورود)", "password"],
      ["ASTRO_DATA_PATH", "مسیر داده Astro", "text"],
      ["MODS_JSON_PATH", "مسیر mods.json", "text"],
    ];
    for (const [key, label, type] of fields) {
      const i = el("input", { type, value: s[key] || "" });
      // show full secret on focus
      i.addEventListener("focus", () => { if (i.type === "password") i.type = "text"; });
      i.addEventListener("blur", () => {
        if (["AGNES_API_KEY", "GITHUB_TOKEN", "HF_TOKEN", "ADMIN_SECRET"].includes(key))
          i.type = "password";
      });
      inputs[key] = i;
      card.appendChild(el("label", { class: "field" },
        el("span", { text: `${label} (${key})` }), i));
    }

    // Helper note
    card.appendChild(el("div", { class: "muted mt-8",
      style: "font-size:11px; line-height:1.6;" },
      "ℹ برای توکن‌های نمایش داده‌شده با ***، اگر مقدار را تغییر ندهید " +
      "سرور مقدار فعلی را حفظ می‌کند. فقط اگر می‌خواهید توکن را عوض کنید " +
      "مقدار جدید را بنویسید."));

    const row = el("div", { class: "row",
      style: "justify-content:flex-end; margin-top:16px;" });
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
        const r = await API.put("/api/settings", body);
        // refresh inputs to show new masked values
        for (const [k] of fields) {
          if (r.settings && r.settings[k] != null) inputs[k].value = r.settings[k];
        }
        toast("تنظیمات ذخیره شد ✓", "info");
      } catch (e) { toast(e.message, "error"); }
      saveBtn.disabled = false;
      saveBtn.textContent = "💾 ذخیره";
    });
  }

  // ------------------------------------------------------------------
  // Server badge (always-on health check) — now stoppable
  // ------------------------------------------------------------------
  let _healthTimer = null;
  async function serverHealthLoop() {
    const badge = $("#server-badge");
    if (!badge) return;
    async function tick() {
      try {
        const r = await fetch("/api/health");
        if (r.ok) {
          const d = await r.json();
          badge.className = "server-badge ok";
          badge.textContent = "● سرور آنلاین" +
            (d.auth_enabled ? " • رمز" : " • باز");
        } else throw 0;
      } catch {
        badge.className = "server-badge bad";
        badge.textContent = "● سرور آفلاین";
      }
    }
    tick();
    _healthTimer = setInterval(tick, 8000);
  }
  function startServerHealthLoop() {
    if (_healthTimer) return;
    serverHealthLoop();
  }

  // ------------------------------------------------------------------
  // Init
  // ------------------------------------------------------------------
  document.addEventListener("DOMContentLoaded", () => {
    $("#modal-close").addEventListener("click", closeModal);
    $(".modal-backdrop").addEventListener("click", closeModal);
    document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });
    bindLoginScreen();
    probeAuthAndBoot();
  });

  // Expose a tiny API for debugging in the webview console
  window.MineBed = { API, toast, openModal, closeModal, getToken, setToken };
})();
