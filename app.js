/* ============================================================
   MineBed Farsi — اسکریپت مشترک
   ============================================================ */

/* ============================================================
   ۱) ابزارهای عمومی
   ============================================================ */
function rng(seed) {
  let s = seed >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}
function makeCanvas(size = 16) {
  const c = document.createElement('canvas');
  c.width = c.height = size; return c;
}
function escapeHtml(s = '') {
  return String(s).replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}
function getParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}
function showToastMsg(text, isError = false) {
  const el = document.createElement('div');
  el.className = 'toast-msg';
  el.textContent = text;
  if (isError) { el.style.background = 'var(--redstone)'; el.style.borderColor = '#8a1a1a'; }
  document.body.appendChild(el);
  setTimeout(() => {
    el.style.transition = 'opacity 0.3s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 300);
  }, 3000);
}

/* ============================================================
   ۲) تکسچرهای پیکسلی
   ============================================================ */
function texDirt(seed = 1337) {
  const c = makeCanvas(), ctx = c.getContext('2d'), r = rng(seed);
  ctx.fillStyle = '#79553a'; ctx.fillRect(0, 0, 16, 16);
  const darks = ['#5b3f29', '#664a30', '#4a3220'];
  const lights = ['#8c6346', '#9b7050', '#8a6240'];
  for (let i = 0; i < 110; i++) {
    ctx.fillStyle = (r() > 0.5) ? darks[(r()*3)|0] : lights[(r()*3)|0];
    ctx.fillRect((r()*16)|0, (r()*16)|0, 1, 1);
  }
  return c.toDataURL();
}
function texGrassTop(seed = 2024) {
  const c = makeCanvas(), ctx = c.getContext('2d'), r = rng(seed);
  ctx.fillStyle = '#5d9d3c'; ctx.fillRect(0, 0, 16, 16);
  const darks = ['#4f8c2f', '#457c27', '#3d6c1f'];
  const lights = ['#6aac46', '#78b855', '#6fae4c'];
  for (let i = 0; i < 130; i++) {
    ctx.fillStyle = (r() > 0.5) ? darks[(r()*3)|0] : lights[(r()*3)|0];
    ctx.fillRect((r()*16)|0, (r()*16)|0, 1, 1);
  }
  return c.toDataURL();
}
function texGrassSide(seed = 555) {
  const c = makeCanvas(), ctx = c.getContext('2d'), r = rng(seed);
  ctx.fillStyle = '#79553a'; ctx.fillRect(0, 0, 16, 16);
  const darks = ['#5b3f29', '#664a30', '#4a3220'];
  const lights = ['#8c6346', '#9b7050', '#8a6240'];
  for (let i = 0; i < 110; i++) {
    ctx.fillStyle = (r() > 0.5) ? darks[(r()*3)|0] : lights[(r()*3)|0];
    ctx.fillRect((r()*16)|0, (r()*16)|0, 1, 1);
  }
  const greens = ['#5d9d3c', '#4f8c2f', '#6aac46', '#5a9a38', '#67a844'];
  for (let y = 0; y < 3; y++)
    for (let x = 0; x < 16; x++) {
      ctx.fillStyle = greens[(r()*5)|0];
      ctx.fillRect(x, y, 1, 1);
    }
  for (let x = 0; x < 16; x++)
    if (r() > 0.35) {
      ctx.fillStyle = greens[(r()*5)|0];
      ctx.fillRect(x, 3, 1, 1);
    }
  return c.toDataURL();
}
function texStone(seed = 777) {
  const c = makeCanvas(), ctx = c.getContext('2d'), r = rng(seed);
  ctx.fillStyle = '#7f7f7f'; ctx.fillRect(0, 0, 16, 16);
  const darks = ['#6b6b6b', '#606060', '#5a5a5a'];
  const lights = ['#8a8a8a', '#949494', '#9b9b9b'];
  for (let i = 0; i < 120; i++) {
    ctx.fillStyle = (r() > 0.55) ? darks[(r()*3)|0] : lights[(r()*3)|0];
    ctx.fillRect((r()*16)|0, (r()*16)|0, 1, 1);
  }
  ctx.fillStyle = '#5a5a5a';
  ctx.fillRect(2, 5, 3, 1); ctx.fillRect(10, 9, 4, 1); ctx.fillRect(4, 12, 5, 1);
  return c.toDataURL();
}
function texBrick(seed = 333) {
  const c = makeCanvas(), ctx = c.getContext('2d'), r = rng(seed);
  ctx.fillStyle = '#8b3a2a'; ctx.fillRect(0, 0, 16, 16);
  const darks = ['#6f2a1d', '#5d2418', '#7a3225'];
  const lights = ['#a04838', '#a85545'];
  for (let i = 0; i < 80; i++) {
    ctx.fillStyle = (r() > 0.5) ? darks[(r()*3)|0] : lights[(r()*2)|0];
    ctx.fillRect((r()*16)|0, (r()*16)|0, 1, 1);
  }
  ctx.fillStyle = '#3d2519';
  for (let y = 0; y < 16; y += 4) ctx.fillRect(0, y, 16, 1);
  for (let y = 0; y < 16; y += 4) {
    const offset = (y / 4) % 2 === 0 ? 0 : 4;
    for (let x = offset; x < 16; x += 8) ctx.fillRect(x, y, 1, 4);
  }
  return c.toDataURL();
}
function texDiamond(seed = 111) {
  const c = makeCanvas(), ctx = c.getContext('2d'), r = rng(seed);
  ctx.fillStyle = '#7f7f7f'; ctx.fillRect(0, 0, 16, 16);
  const darks = ['#6b6b6b', '#606060', '#5a5a5a'];
  const lights = ['#8a8a8a', '#949494'];
  for (let i = 0; i < 100; i++) {
    ctx.fillStyle = (r() > 0.5) ? darks[(r()*3)|0] : lights[(r()*2)|0];
    ctx.fillRect((r()*16)|0, (r()*16)|0, 1, 1);
  }
  const dia = ['#4aedd9', '#a8fff5', '#2ec4b6'];
  const spots = [[2,3],[3,3],[2,4],[11,3],[12,3],[12,4],[5,7],[6,7],[6,8],[5,8],[10,10],[11,10],[11,11],[3,12],[4,12],[3,13],[8,13],[9,13]];
  spots.forEach(([x, y]) => {
    ctx.fillStyle = dia[(r()*3)|0];
    ctx.fillRect(x, y, 1, 1);
  });
  return c.toDataURL();
}
function texLeaves(seed = 888) {
  const c = makeCanvas(), ctx = c.getContext('2d'), r = rng(seed);
  ctx.fillStyle = '#2d5a1a'; ctx.fillRect(0, 0, 16, 16);
  const darks = ['#1d3f10', '#254d14'];
  const lights = ['#3d7a24', '#4a8f2c'];
  for (let i = 0; i < 150; i++) {
    ctx.fillStyle = (r() > 0.5) ? darks[(r()*2)|0] : lights[(r()*2)|0];
    ctx.fillRect((r()*16)|0, (r()*16)|0, 1, 1);
  }
  return c.toDataURL();
}
function texGold(seed = 444) {
  const c = makeCanvas(), ctx = c.getContext('2d'), r = rng(seed);
  ctx.fillStyle = '#7f7f7f'; ctx.fillRect(0, 0, 16, 16);
  const darks = ['#6b6b6b', '#606060', '#5a5a5a'];
  const lights = ['#8a8a8a', '#949494'];
  for (let i = 0; i < 100; i++) {
    ctx.fillStyle = (r() > 0.5) ? darks[(r()*3)|0] : lights[(r()*2)|0];
    ctx.fillRect((r()*16)|0, (r()*16)|0, 1, 1);
  }
  const gold = ['#fcb32b', '#ffe5a8', '#d4941f'];
  const spots = [[2,3],[3,3],[2,4],[11,3],[12,3],[12,4],[5,7],[6,7],[6,8],[5,8],[10,10],[11,10],[11,11],[3,12],[4,12],[3,13],[8,13],[9,13]];
  spots.forEach(([x, y]) => {
    ctx.fillStyle = gold[(r()*3)|0];
    ctx.fillRect(x, y, 1, 1);
  });
  return c.toDataURL();
}

/* ============================================================
   ۳) مکعب سه‌بعدی
   ============================================================ */
const BLOCK_STYLES = [
  { name: 'چمن',   side: texGrassSide(555),  top: texGrassTop(2024), bottom: texDirt(1337),
    palette: ['#5d9d3c', '#4f8c2f', '#6aac46', '#79553a', '#8c6346'] },
  { name: 'خاک',   side: texDirt(1337),     top: texDirt(1337),     bottom: texDirt(1337),
    palette: ['#79553a', '#5b3f29', '#8c6346', '#9b7050', '#664a30'] },
  { name: 'سنگ',   side: texStone(777),     top: texStone(777),     bottom: texStone(777),
    palette: ['#7f7f7f', '#6b6b6b', '#8a8a8a', '#5a5a5a', '#949494'] },
  { name: 'آجر',   side: texBrick(333),     top: texBrick(333),     bottom: texBrick(333),
    palette: ['#8b3a2a', '#6f2a1d', '#a04838', '#3d2519', '#a85545'] },
  { name: 'طلا',   side: texGold(444),      top: texGold(444),      bottom: texGold(444),
    palette: ['#fcb32b', '#ffe5a8', '#d4941f', '#7f7f7f', '#8a8a8a'] },
  { name: 'الماس', side: texDiamond(111),   top: texDiamond(111),   bottom: texDiamond(111),
    palette: ['#4aedd9', '#2ec4b6', '#a8fff5', '#7f7f7f', '#949494'] },
  { name: 'برگ',   side: texLeaves(888),    top: texLeaves(888),    bottom: texLeaves(888),
    palette: ['#2d5a1a', '#3d7a24', '#4a8f2c', '#1d3f10', '#254d14'] }
];
let currentBlockIndex = 0;

function buildCube() {
  const stage = document.getElementById('cubeStage');
  if (!stage) return;
  if (stage.querySelector('.mc-cube')) return; // قبلاً ساخته شده
  stage.insertAdjacentHTML('afterbegin', `
    <div class="mc-cube" id="mcCube" title="کلیک کن تا بلوک عوض شه">
      <div class="face front"  data-face="side"></div>
      <div class="face back"   data-face="side"></div>
      <div class="face right"  data-face="side"></div>
      <div class="face left"   data-face="side"></div>
      <div class="face top"    data-face="top"></div>
      <div class="face bottom" data-face="bottom"></div>
    </div>`);

  const cube = document.getElementById('mcCube');
  const cubeNameEl = document.getElementById('cubeName');

  function applyBlock(index) {
    const b = BLOCK_STYLES[index];
    cube.querySelectorAll('.face').forEach(face => {
      const type = face.dataset.face;
      face.style.backgroundImage = `url(${b[type]})`;
    });
    if (cubeNameEl) cubeNameEl.textContent = 'بلوک ' + b.name;
  }

  applyBlock(currentBlockIndex);

  cube.addEventListener('click', (e) => {
    e.stopPropagation();
    currentBlockIndex = (currentBlockIndex + 1) % BLOCK_STYLES.length;
    applyBlock(currentBlockIndex);

    cube.classList.add('hit');
    setTimeout(() => cube.classList.remove('hit'), 250);

    const rect = cube.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    burstParticles(cx, cy, BLOCK_STYLES[currentBlockIndex].palette, 22, 110);
  });
}

/* ============================================================
   ۴) افکت ذرات و دنباله موس
   ============================================================ */
function initFxLayer() {
  if (!document.getElementById('fxLayer')) {
    const layer = document.createElement('div');
    layer.id = 'fxLayer';
    document.body.insertBefore(layer, document.body.firstChild);
  }
}

function burstParticles(x, y, colors, count = 15, power = 90) {
  const fxLayer = document.getElementById('fxLayer');
  if (!fxLayer) return;
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size = 6 + Math.random() * 6;
    p.style.width = size + 'px';
    p.style.height = size + 'px';
    p.style.background = colors[(Math.random() * colors.length) | 0];
    p.style.left = (x - size / 2) + 'px';
    p.style.top = (y - size / 2) + 'px';

    const angle = Math.random() * Math.PI * 2;
    const dist = power * (0.5 + Math.random() * 0.9);
    p.style.setProperty('--tx', Math.cos(angle) * dist + 'px');
    p.style.setProperty('--ty', (Math.sin(angle) * dist + 60) + 'px');
    p.style.animationDuration = (0.6 + Math.random() * 0.4) + 's';

    fxLayer.appendChild(p);
    setTimeout(() => p.remove(), 1000);
  }
}

let globalEffectsBound = false;
function initGlobalEffects() {
  initFxLayer();
  if (globalEffectsBound) return;
  globalEffectsBound = true;

  document.addEventListener('click', (e) => {
    if (e.target.closest('#mcCube')) return;
    if (e.target.closest('.bg-music-player')) return;
    if (e.target.closest('.to-top')) return;
    if (e.target.closest('a')) return;
    if (e.target.closest('.mc-btn')) return;
    if (e.target.closest('.chip')) return;
    if (e.target.closest('.mod-card')) return;
    if (e.target.closest('button')) return;
    const palette = ['#5fa838', '#7cc84a', '#4aedd9', '#fcb32b', '#79553a'];
    burstParticles(e.clientX, e.clientY, palette, 10, 60);
  });

  const trailColors = ['#7cc84a', '#4aedd9', '#fcb32b', '#5fa838', '#a855f7'];
  let lastTrailTime = 0;
  document.addEventListener('mousemove', (e) => {
    const now = performance.now();
    if (now - lastTrailTime < 40) return;
    lastTrailTime = now;
    const fxLayer = document.getElementById('fxLayer');
    if (!fxLayer) return;
    const p = document.createElement('div');
    p.className = 'trail-particle';
    const size = 4 + Math.random() * 5;
    p.style.width = size + 'px';
    p.style.height = size + 'px';
    p.style.background = trailColors[(Math.random() * trailColors.length) | 0];
    p.style.left = (e.clientX - size / 2 + (Math.random() - 0.5) * 8) + 'px';
    p.style.top = (e.clientY - size / 2 + (Math.random() - 0.5) * 8) + 'px';
    fxLayer.appendChild(p);
    setTimeout(() => p.remove(), 950);
  });
}

/* ============================================================
   ۵) بلوک‌های شناور هیرو
   ============================================================ */
function initHeroBlocks() {
  const box = document.getElementById('heroBlocks');
  if (!box) return;
  if (box.children.length > 0) return; // قبلاً ساخته شده
  for (let i = 0; i < 16; i++) {
    const span = document.createElement('span');
    span.style.left = Math.random() * 100 + '%';
    span.style.animationDuration = (10 + Math.random() * 14) + 's';
    span.style.animationDelay = (Math.random() * 12) + 's';
    const s = 18 + Math.random() * 26;
    span.style.width = span.style.height = s + 'px';
    box.appendChild(span);
  }
}

/* ============================================================
   ۶) موسیقی پس‌زمینه — از music.json لود می‌شه
   ============================================================ */
let MUSIC_TRACKS = [];
let currentTrackIndex = 0;
let musicInitialized = false;

async function loadMusicFromJson() {
  try {
    const res = await fetch('music.json?t=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) throw new Error('music.json not found');
    const data = await res.json();
    MUSIC_TRACKS = data.tracks || [];
  } catch (err) {
    console.warn('خطا در بارگذاری music.json:', err);
    MUSIC_TRACKS = [{
      title: 'CRAFT UNIVERSO - MINECRAFT FUNK',
      src: 'https://cdn.imgurl.ir/uploads/p071172_CRAFT_UNIVERSO_-_MINECRAFT_FUNK_Ultra_Slowed_320.mp3'
    }];
  }
}

function initMusic() {
  const audio = document.getElementById('bgAudio');
  const playPauseBtn = document.getElementById('playPauseBtn');
  const nextBtn = document.getElementById('nextBtn');
  const musicTitle = document.getElementById('musicTitle');
  if (!audio || !playPauseBtn) return;

  // اگه قبلاً مقداردهی شده، فقط UI رو آپدیت کن
  if (musicInitialized) {
    if (musicTitle && MUSIC_TRACKS[currentTrackIndex]) {
      musicTitle.textContent = MUSIC_TRACKS[currentTrackIndex].title;
    }
    return;
  }

  if (!MUSIC_TRACKS.length) return;
  musicInitialized = true;

  let isPlaying = false;

  function loadTrack(index, autoplay = false) {
    currentTrackIndex = index;
    const track = MUSIC_TRACKS[index];
    if (!track) return;
    if (musicTitle) musicTitle.textContent = track.title;
    audio.src = track.src;
    audio.volume = 0.35;
    audio.loop = MUSIC_TRACKS.length === 1;
    if (autoplay) tryPlay();
  }

  function tryPlay() {
    const p = audio.play();
    if (p !== undefined) {
      p.then(() => { isPlaying = true; playPauseBtn.textContent = '❚❚'; })
       .catch(() => { isPlaying = false; playPauseBtn.textContent = '▶'; });
    }
  }
  function pause() {
    audio.pause();
    isPlaying = false;
    playPauseBtn.textContent = '▶';
  }

  audio.addEventListener('canplaythrough', () => {
    setTimeout(() => tryPlay(), 300);
  }, { once: true });

  const startOnInteract = () => {
    if (!isPlaying) tryPlay();
    document.removeEventListener('click', startOnInteract);
    document.removeEventListener('touchstart', startOnInteract);
  };
  document.addEventListener('click', startOnInteract, { once: true });
  document.addEventListener('touchstart', startOnInteract, { once: true });

  playPauseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (isPlaying) pause(); else tryPlay();
  });

  if (nextBtn) {
    nextBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (MUSIC_TRACKS.length <= 1) {
        audio.currentTime = 0;
        if (!isPlaying) tryPlay();
      } else {
        const next = (currentTrackIndex + 1) % MUSIC_TRACKS.length;
        loadTrack(next, true);
      }
    });
  }

  audio.addEventListener('ended', () => {
    if (MUSIC_TRACKS.length > 1) {
      const next = (currentTrackIndex + 1) % MUSIC_TRACKS.length;
      loadTrack(next, true);
    }
  });

  audio.addEventListener('play', () => { isPlaying = true; playPauseBtn.textContent = '❚❚'; });
  audio.addEventListener('pause', () => { isPlaying = false; playPauseBtn.textContent = '▶'; });

  loadTrack(0, false);
}

/* ============================================================
   ۷) دکمه بازگشت به بالا
   ============================================================ */
function initToTop() {
  const toTop = document.getElementById('toTop');
  if (!toTop) return;
  if (toTop.dataset.bound === '1') return;
  toTop.dataset.bound = '1';
  window.addEventListener('scroll', () => {
    toTop.classList.toggle('show', window.scrollY > 500);
  });
  toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* ============================================================
   ۸) منوی موبایل
   ============================================================ */
function initMobileMenu() {
  const menuToggle = document.getElementById('menuToggle');
  const mainNav = document.getElementById('mainNav');
  if (menuToggle && mainNav && !menuToggle.dataset.bound) {
    menuToggle.dataset.bound = '1';
    menuToggle.addEventListener('click', () => mainNav.classList.toggle('open'));
    mainNav.addEventListener('click', e => {
      if (e.target.tagName === 'A') mainNav.classList.remove('open');
    });
  }
}

/* ============================================================
   ۹) پیش‌لودر
   ============================================================ */
function initPreloader() {
  window.addEventListener('load', () => {
    setTimeout(() => {
      const preloader = document.getElementById('preloader');
      if (preloader) preloader.classList.add('done');
    }, 1200);
  });
}

/* ============================================================
   ۱۰) بارگذاری مادها (صفحه اصلی)
   ============================================================ */
let MODS = [];
const CAT_NAMES = {
  gameplay: 'گیم‌پلی', graphics: 'گرافیک', maps: 'مپ',
  mobs: 'موجودات', decoration: 'دکوراسیون', world: 'دنیا', utility: 'ابزار'
};
const CATS = [
  { id: 'all', label: 'همه' },
  { id: 'gameplay', label: 'گیم‌پلی' },
  { id: 'graphics', label: 'گرافیک' },
  { id: 'maps', label: 'مپ' },
  { id: 'mobs', label: 'موجودات' },
  { id: 'decoration', label: 'دکوراسیون' },
  { id: 'world', label: 'دنیا' },
  { id: 'utility', label: 'ابزار' }
];
let currentCat = 'all';
let currentSearch = '';

function modCard(m) {
  const fallback = `<span class="fallback">${m.icon || '📦'}</span>`;
  const img = m.cover ? `<img src="${m.cover}" alt="${escapeHtml(m.name)}" loading="lazy" onerror="this.remove()">` : '';
  const badges = `
    <div class="mod-badges">
      <div>
        ${m.isNew ? '<span class="badge new">جدید</span>' : ''}
        ${m.featured && !m.isNew ? '<span class="badge featured">ویژه</span>' : ''}
      </div>
      <span class="badge version">${m.version || ''}</span>
    </div>`;
  return `
    <article class="mod-card" data-id="${m.id}" onclick="navigateTo('mod.html?id=${encodeURIComponent(m.id)}')">
      <div class="mod-thumb">${fallback}${img}${badges}</div>
      <div class="mod-body">
        <div class="mod-cat">${m.catName || ''}</div>
        <h3 class="mod-title">${m.nameFa || m.name}</h3>
        <p class="mod-tagline">${m.tagline || ''}</p>
        <div class="mod-meta"><span>💾 ${m.size || '-'}</span><span>⬇️ ${m.downloads || '0'}</span></div>
        <div class="mod-actions">
          <a href="mod.html?id=${encodeURIComponent(m.id)}" class="mc-btn small" onclick="event.preventDefault();navigateTo('mod.html?id=${encodeURIComponent(m.id)}');event.stopPropagation()">👁️ مشاهده</a>
        </div>
      </div>
    </article>`;
}

function renderFeatured() {
  const grid = document.getElementById('featuredGrid');
  if (!grid) return;
  const list = MODS.filter(m => m.featured).slice(0, 3);
  if (!list.length) {
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-3);">
      هنوز افزونه‌ی ویژه‌ای ثبت نشده
    </div>`;
    return;
  }
  let html = '';
  list.forEach((m, i) => {
    html += modCard(m);
    if (i === 1) {
      html += `
        <div style="grid-column:1/-1;background:var(--panel);border:2px dashed var(--line);padding:18px;min-height:120px;display:flex;align-items:center;justify-content:center;position:relative;">
          <span style="position:absolute;top:6px;right:10px;font-family:var(--pixel);font-size:9px;color:var(--text-3);letter-spacing:2px;">AD</span>
          <div id="mediaad-nwmnG"></div>
        </div>`;
    }
  });
  grid.innerHTML = html;
}

function renderMods() {
  const grid = document.getElementById('modsGrid');
  if (!grid) return;
  const list = MODS.filter(m => {
    if (currentCat !== 'all' && m.category !== currentCat) return false;
    if (currentSearch) {
      const hay = (
        m.name + ' ' + (m.nameFa || '') + ' ' + (m.keywords || '') + ' ' +
        (m.tagline || '') + ' ' + (m.desc || '')
      ).toLowerCase();
      if (!hay.includes(currentSearch)) return false;
    }
    return true;
  });
  if (!list.length) {
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:60px 20px;color:var(--text-2);">
      <div style="font-size:60px;margin-bottom:14px;opacity:0.35;">🕳️</div>
      <h3 style="color:#fff;margin-bottom:8px;">چیزی پیدا نشد</h3>
      <p>فیلتر یا جستجو رو تغییر بده</p>
    </div>`;
    return;
  }
  let html = '';
  list.forEach((m, i) => {
    html += modCard(m);
    if ((i + 1) % 3 === 0 && i < list.length - 1) {
      html += `
        <div style="grid-column:1/-1;background:var(--panel);border:2px dashed var(--line);padding:18px;min-height:120px;display:flex;align-items:center;justify-content:center;position:relative;">
          <span style="position:absolute;top:6px;right:10px;font-family:var(--pixel);font-size:9px;color:var(--text-3);letter-spacing:2px;">AD</span>
          <div id="mediaad-nwmnG"></div>
        </div>`;
    }
  });
  grid.innerHTML = html;
}

function filterCat(id) {
  currentCat = id;
  const chipRow = document.getElementById('chipRow');
  if (chipRow) {
    chipRow.querySelectorAll('.chip').forEach(c => c.classList.toggle('active', c.dataset.cat === id));
  }
  renderMods();
  const modsEl = document.getElementById('mods');
  if (modsEl) modsEl.scrollIntoView({ behavior: 'smooth' });
}
window.filterCat = filterCat;

function animateCount() {
  document.querySelectorAll('[data-count]').forEach(el => {
    if (el.dataset.fetch || el.dataset.animated === '1') return;
    el.dataset.animated = '1';
    const target = +el.dataset.count;
    let cur = 0;
    const step = Math.max(1, Math.ceil(target / 60));
    const id = setInterval(() => {
      cur += step;
      if (cur >= target) { el.textContent = target; clearInterval(id); }
      else el.textContent = cur;
    }, 28);
  });
}

async function initLiveStats() {
  try {
    const res = await fetch('mods.json?t=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) return;
    const data = await res.json();
    const mods = data.mods || [];
    const featured = mods.filter(m => m.featured).length;
    document.querySelectorAll('[data-fetch="mods"]').forEach(el => {
      el.dataset.count = mods.length;
    });
    document.querySelectorAll('[data-fetch="featured"]').forEach(el => {
      el.dataset.count = featured;
    });
    // Animate after setting values
    animateCount();
  } catch (e) {}
}

function initChips() {
  const chipRow = document.getElementById('chipRow');
  if (!chipRow || chipRow.dataset.bound === '1') return;
  chipRow.dataset.bound = '1';
  chipRow.innerHTML = CATS.map(c =>
    `<button class="chip${c.id === 'all' ? ' active' : ''}" data-cat="${c.id}">${c.label}</button>`
  ).join('');
  chipRow.addEventListener('click', e => {
    const btn = e.target.closest('.chip');
    if (!btn) return;
    currentCat = btn.dataset.cat;
    chipRow.querySelectorAll('.chip').forEach(c => c.classList.toggle('active', c === btn));
    renderMods();
  });
}

function initSearch() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput || searchInput.dataset.bound === '1') return;
  searchInput.dataset.bound = '1';
  let searchTimeout;
  searchInput.addEventListener('input', e => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentSearch = e.target.value.trim().toLowerCase();
      renderMods();
    }, 200);
  });
}

async function loadModsFromJson() {
  try {
    const res = await fetch('mods.json?t=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) throw new Error('mods.json not found');
    const data = await res.json();
    MODS = data.mods || [];
  } catch (err) {
    console.warn('خطا در بارگذاری mods.json:', err);
    MODS = [];
  }
  renderFeatured();
  renderMods();
  animateCount();
  initLiveStats();
}

function initIndexPage() {
  initChips();
  initSearch();
  loadModsFromJson();
}

/* ============================================================
   ۱۱) صفحه ماد
   ============================================================ */
const CORS_PROXIES = [
  url => url,
  url => `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`,
  url => `https://corsproxy.io/?url=${encodeURIComponent(url)}`,
  url => `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`
];

async function forceDownload(event, url, filename) {
  if (event) { event.preventDefault(); event.stopPropagation(); }
  if (!url || url === '#' || url === '') {
    showToastMsg('❌ لینک دانلود موجود نیست', true); return;
  }
  if (!filename) {
    try { filename = decodeURIComponent(url.split('/').pop().split('?')[0]) || 'mod.mcpack'; }
    catch { filename = 'mod.mcpack'; }
  }
  await showCountdown(2);
  showToastMsg('⏳ در حال دانلود...');
  for (let i = 0; i < CORS_PROXIES.length; i++) {
    try {
      const res = await fetch(CORS_PROXIES[i](url), { cache: 'no-store', mode: 'cors' });
      if (!res.ok) continue;
      const blob = await res.blob();
      if (blob.size < 500) continue;
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl; a.download = filename;
      a.style.display = 'none';
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 2000);
      showToastMsg('✅ دانلود شروع شد');
      return;
    } catch (err) { console.log('پروکسی ' + i + ' نشد'); }
  }
  showToastMsg('⚠️ سرور مقصد اجازه دانلود مستقیم نمی‌ده');
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.style.display = 'none';
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
}
window.forceDownload = forceDownload;

function showCountdown(seconds) {
  return new Promise(resolve => {
    let count = seconds;
    const overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,0.85);backdrop-filter:blur(6px);display:flex;align-items:center;justify-content:center;font-family:var(--font);color:#fff;';
    overlay.innerHTML = `
      <div style="background:var(--panel);border:3px solid var(--line);padding:40px 60px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.6);min-width:280px;max-width:90vw;">
        <div style="font-family:var(--pixel);font-size:12px;color:var(--grass);letter-spacing:2px;margin-bottom:20px;">⏳ دانلود</div>
        <div id="countdownNum" style="font-family:var(--pixel);font-size:64px;color:var(--diamond);text-shadow:0 0 30px rgba(74,237,217,0.6),3px 3px 0 #000;margin-bottom:16px;line-height:1;">${count}</div>
        <div style="font-size:14px;color:var(--text-2);">کلیک دوم برای دانلود...</div>
        <div style="margin-top:20px;width:100%;height:6px;background:var(--bg-2);border:2px solid var(--line);overflow:hidden;">
          <div id="countdownBar" style="height:100%;width:0%;background:linear-gradient(90deg,var(--grass-3),var(--grass-2));transition:width ${seconds}s linear;"></div>
        </div>
      </div>`;
    document.body.appendChild(overlay);
    document.body.classList.add('no-scroll');
    const numEl = overlay.querySelector('#countdownNum');
    const barEl = overlay.querySelector('#countdownBar');
    requestAnimationFrame(() => { barEl.style.width = '100%'; });
    const timer = setInterval(() => {
      count--;
      if (count > 0) {
        numEl.textContent = count;
        numEl.style.animation = 'none';
        void numEl.offsetWidth;
        numEl.style.animation = 'countPulse 0.5s ease';
      } else {
        clearInterval(timer);
        overlay.remove();
        document.body.classList.remove('no-scroll');
        resolve();
      }
    }, 1000);
  });
}

function copyPageLink() {
  navigator.clipboard.writeText(window.location.href).then(() => {
    showToastMsg('🔗 لینک کپی شد');
  }).catch(() => showToastMsg('❌ کپی نشد', true));
}
window.copyPageLink = copyPageLink;

function openImage(url) {
  const overlay = document.createElement('div');
  overlay.id = 'imageOverlay';
  const img = document.createElement('img');
  img.src = url; img.alt = 'تصویر';
  overlay.appendChild(img);
  overlay.onclick = () => overlay.remove();
  document.body.appendChild(overlay);
}
window.openImage = openImage;

function injectJsonLd(mod) {
  const old = document.querySelector('script[data-jsonld="mod"]');
  if (old) old.remove();
  const data = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": mod.name,
    "description": mod.tagline || mod.desc || '',
    "image": mod.cover || '',
    "applicationCategory": "GameApplication",
    "operatingSystem": "Android, iOS, Windows",
    "offers": { "@type": "Offer", "price": "0", "priceCurrency": "IRR" },
    "author": { "@type": "Organization", "name": mod.author || 'MineBed Farsi' }
  };
  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.dataset.jsonld = 'mod';
  script.textContent = JSON.stringify(data);
  document.head.appendChild(script);
}

function renderModPage(mod, allMods) {
  const pageTitle = `${mod.name} | دانلود افزونه ماینکرفت بدراک`;
  const pageDesc = mod.tagline || `${mod.name} را برای ماینکرفت بدراک دانلود کن`;
  document.title = pageTitle;
  const metaDesc = document.querySelector('meta[name="description"]');
  if (metaDesc) metaDesc.setAttribute('content', pageDesc);
  const canonicalLink = document.getElementById('canonicalLink');
  if (canonicalLink) canonicalLink.setAttribute('href', window.location.href);

  injectJsonLd(mod);

  const related = allMods
    .filter(m => m.id !== mod.id && m.category === mod.category)
    .slice(0, 4);

  const relatedHTML = related.length ? `
    <div class="section-block">
      <h2>افزونه‌های مرتبط</h2>
      <div class="related-grid">
        ${related.map(r => `
          <a href="mod.html?id=${encodeURIComponent(r.id)}" class="related-card" onclick="event.preventDefault();navigateTo('mod.html?id=${encodeURIComponent(r.id)}')">
            <div class="related-thumb">
              ${r.icon || '📦'}
              ${r.cover ? `<img src="${r.cover}" alt="${escapeHtml(r.name)}" loading="lazy" onerror="this.remove()">` : ''}
            </div>
            <h4>${escapeHtml(r.nameFa || r.name)}</h4>
            <div class="cat">${r.catName || CAT_NAMES[r.category] || ''}</div>
          </a>
        `).join('')}
      </div>
    </div>
  ` : '';

  const galleryHTML = (mod.gallery && mod.gallery.length) ? `
    <div class="section-block">
      <h2>📸 گالری تصاویر</h2>
      <div class="gallery-grid">
        ${mod.gallery.map(url => `
          <div class="shot" onclick="openImage('${url}')">
            <img src="${url}" alt="${escapeHtml(mod.name)}" loading="lazy" onerror="this.parentElement.remove()">
          </div>
        `).join('')}
      </div>
    </div>
  ` : '';

  const descHTML = mod.desc ? `
    <div class="section-block">
      <h2>📝 توضیحات کامل</h2>
      ${mod.desc.split('\n').filter(p => p.trim()).map(p => `<p>${escapeHtml(p)}</p>`).join('')}
    </div>
  ` : '';

  const catName = mod.catName || CAT_NAMES[mod.category] || '';
  const safeName = (mod.name || 'mod').replace(/'/g, "\\'");
  const safeUrl = (mod.downloadUrl || '').replace(/'/g, "\\'");

  const html = `
    <nav class="breadcrumb">
      <a href="index.html">خانه</a>
      <span class="sep">›</span>
      <a href="index.html#mods">افزونه‌ها</a>
      <span class="sep">›</span>
      <a href="index.html#mods">${catName}</a>
      <span class="sep">›</span>
      <span class="current">${escapeHtml(mod.nameFa || mod.name)}</span>
    </nav>

    <div class="mod-hero">
      <div class="mod-art">
        <span class="fallback">${mod.icon || '📦'}</span>
        ${mod.cover ? `<img src="${mod.cover}" alt="${escapeHtml(mod.name)}" onerror="this.remove()">` : ''}
      </div>
      <div class="mod-info">
        <span class="mod-cat-tag">${catName}</span>
        <h1>${escapeHtml(mod.nameFa || mod.name)}</h1>
        ${mod.nameFa ? `<div style="font-size:12px;color:var(--text-3);margin-bottom:14px;">${escapeHtml(mod.name)}</div>` : ''}
        <p class="mod-tagline-lg">${escapeHtml(mod.tagline || '')}</p>

        <div class="badges-row">
          ${mod.isNew ? '<span class="badge-pill new">🆕 جدید</span>' : ''}
          ${mod.featured ? '<span class="badge-pill featured">⭐ ویژه</span>' : ''}
          <span class="badge-pill version">📦 نسخه ${mod.version || '-'}</span>
        </div>

        <div class="spec-grid">
          <div class="spec"><div class="k">📦 نسخه</div><div class="v">${mod.version || '-'}</div></div>
          <div class="spec"><div class="k">💾 حجم</div><div class="v">${mod.size || '-'}</div></div>
          <div class="spec"><div class="k">👤 سازنده</div><div class="v">${mod.author || '-'}</div></div>
          <div class="spec"><div class="k">📅 آپدیت</div><div class="v">${mod.updated || '-'}</div></div>
        </div>

        <div class="download-actions">
          <button class="mc-btn download-btn" onclick="forceDownload(event, '${safeUrl}', '${safeName}.mcpack')">
            ⬇️ دانلود افزونه
          </button>
          <button class="mc-btn ghost" onclick="copyPageLink()">🔗 کپی لینک</button>
        </div>
      </div>
    </div>

    <div class="ad-inline">
      <div id="mediaad-nwmnG"></div>
    </div>

    ${descHTML}

    <div class="ad-inline" style="border-color:var(--gold);">
      <div id="mediaad-JRBY2"></div>
    </div>

    ${galleryHTML}

    <div class="ad-inline">
      <div id="mediaad-nwmnG"></div>
    </div>

    ${relatedHTML}
  `;

  const pageContent = document.getElementById('pageContent');
  if (pageContent) pageContent.innerHTML = html;
}

function renderError(message) {
  document.title = 'افزونه پیدا نشد | MineBed Farsi';
  const pageContent = document.getElementById('pageContent');
  if (pageContent) {
    pageContent.innerHTML = `
      <div class="error-page">
        <div class="emoji">🔍</div>
        <h1>${message}</h1>
        <p>ممکنه آدرس اشتباه باشه یا این افزونه حذف شده باشه</p>
        <a href="index.html" class="mc-btn">← بازگشت به صفحه اصلی</a>
      </div>
    `;
  }
}

async function initModPage() {
  const id = getParam('id');
  if (!id) { renderError('شناسه افزونه مشخص نشده'); return; }
  try {
    if (!MODS.length) {
      const res = await fetch('mods.json?t=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) throw new Error('خطا در بارگذاری فایل داده');
      const data = await res.json();
      MODS = data.mods || [];
    }
    const mod = MODS.find(m => m.id === id);
    if (!mod) { renderError('این افزونه پیدا نشد'); return; }
    renderModPage(mod, MODS);
  } catch (err) {
    console.error(err);
    renderError('خطا در بارگذاری صفحه');
  }
}

/* ============================================================
   ۱۲) راهنمای نصب
   ============================================================ */
function initGuidePage() {
  const tabs = document.querySelectorAll('.platform-tab');
  const contents = document.querySelectorAll('.guide-content');
  tabs.forEach(tab => {
    if (tab.dataset.bound === '1') return;
    tab.dataset.bound = '1';
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));
      tab.classList.add('active');
      const platform = tab.dataset.platform;
      const content = document.getElementById(platform);
      if (content) content.classList.add('active');
    });
  });
}

/* ============================================================
   ۱۳) درباره ما
   ============================================================ */
function initAboutPage() {
  const faqList = document.getElementById('faqList');
  if (!faqList || faqList.dataset.bound === '1') return;
  faqList.dataset.bound = '1';
  const FAQ = [
    { q: 'افزونه‌ها رایگان هستن؟', a: 'بله، همه‌ی افزونه‌های این سایت رایگان هستن. هیچ فایل پولی بدون اجازه‌ی سازنده منتشر نمی‌شه.' },
    { q: 'چرا بعضی افزونه‌ها از سایت‌های دیگه لود می‌شن؟', a: 'برای اینکه سرعت سایت بالا بمونه و هزینه‌ی پهنای باند ما کم بشه، فایل‌های حجیم روی سرورهای میزبانی فایل خارجی قرار می‌گیرن.' },
    { q: 'افزونه‌ها رو چطور نصب کنم؟', a: 'برو به صفحه‌ی «آموزش نصب» و پلتفرمت رو انتخاب کن. تمام مراحل با تصویر توضیح داده شده.' },
    { q: 'اگه افزونه کار نکرد چی؟', a: 'احتمالاً نسخه‌ی بازیت با افزونه سازگار نیست. توضیحات افزونه رو چک کن. اگه باز مشکل داشتی، به ما اطلاع بده.' },
    { q: 'می‌تونم افزونه‌ی خودم رو بفرستم؟', a: 'حتماً. از طریق ایمیل یا تلگرام بفرست. اگه کیفیتش خوب باشه و تست پس بده، منتشرش می‌کنیم.' },
    { q: 'آیا سایتتون امنه؟', a: 'بله. همه‌ی فایل‌ها قبل از انتشار تست می‌شن. ما از سرویس‌های معتبر ایرانی مثل تپسل برای تبلیغات استفاده می‌کنیم و به حریم خصوصی کاربران احترام می‌ذاریم.' }
  ];
  faqList.innerHTML = FAQ.map(item => `
    <div class="faq-item">
      <h4>❓ ${item.q}</h4>
      <p>${item.a}</p>
    </div>
  `).join('');
}

/* ============================================================
   ۱۴) ناوبری SPA (بدون رفتن به لینک جدید)
   ============================================================ */
let isNavigating = false;

function isInternalLink(href) {
  if (!href) return false;
  if (href.startsWith('#')) return false;
  if (href.startsWith('http://') || href.startsWith('https://')) return false;
  if (href.startsWith('mailto:') || href.startsWith('tel:')) return false;
  if (href.endsWith('.json') || href.endsWith('.xml') || href.endsWith('.txt')) return false;
  return true;
}

function updateActiveNav(url) {
  const nav = document.getElementById('mainNav');
  if (!nav) return;
  const path = url.split('?')[0].split('#')[0];
  nav.querySelectorAll('a').forEach(a => {
    const href = a.getAttribute('href') || '';
    const hrefPath = href.split('?')[0].split('#')[0];
    a.classList.toggle('active', hrefPath === path);
  });
}

function reInitPage() {
  // افکت‌های ثابت
  buildCube();
  initHeroBlocks();
  initToTop();
  initMobileMenu();
  initGuidePage();

  // صفحه‌های خاص
  if (document.getElementById('modsGrid')) initIndexPage();
  if (document.getElementById('pageContent')) initModPage();
  if (document.getElementById('faqList')) initAboutPage();

  // موزیک — UI رو آپدیت کن بدون تغییر پخش
  const musicTitle = document.getElementById('musicTitle');
  if (musicTitle && MUSIC_TRACKS[currentTrackIndex]) {
    musicTitle.textContent = MUSIC_TRACKS[currentTrackIndex].title;
  }
}

async function navigateTo(url, push = true) {
  if (isNavigating) return;
  isNavigating = true;

  // Show preloader immediately
  const preloader = document.getElementById('preloader');
  if (preloader) preloader.classList.remove('done');

  try {
    // اسکرول به بالا
    window.scrollTo({ top: 0, behavior: 'auto' });

    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch: ' + url);
    const html = await res.text();

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    // عنوان
    document.title = doc.title;

    // متا
    const newDesc = doc.querySelector('meta[name="description"]');
    const curDesc = document.querySelector('meta[name="description"]');
    if (newDesc && curDesc) curDesc.setAttribute('content', newDesc.getAttribute('content') || '');

    // محتوای main — فقط محتوای main رو عوض کن (پلیر و هدر ثابت می‌مونن)
    const newMain = doc.querySelector('main');
    const currentMain = document.querySelector('main');
    if (newMain && currentMain) {
      currentMain.innerHTML = newMain.innerHTML;
    }

    // ناوبری فعال
    updateActiveNav(url);

    // مقداردهی مجدد صفحه
    reInitPage();

    // Hide preloader
    if (preloader) preloader.classList.add('done');

    if (push) {
      history.pushState({ url }, '', url);
    }
  } catch (err) {
    console.error('خطا در ناوبری:', err);
    // Fallback to full page load
    window.location.href = url;
  } finally {
    isNavigating = false;
  }
}
window.navigateTo = navigateTo;

function initSPARouter() {
  if (document.body.dataset.spaBound === '1') return;
  document.body.dataset.spaBound = '1';

  document.addEventListener('click', (e) => {
    const link = e.target.closest('a');
    if (!link) return;
    if (link.target === '_blank') return;
    if (link.hasAttribute('download')) return;

    const href = link.getAttribute('href');
    if (!isInternalLink(href)) return;

    // اگه توی پنل ادمین یا جایی که نباید SPA بشه
    if (document.body.dataset.noSpa === '1') return;

    e.preventDefault();
    navigateTo(href, true);
  });

  window.addEventListener('popstate', (e) => {
    if (e.state && e.state.url) {
      navigateTo(e.state.url, false);
    } else {
      navigateTo(window.location.pathname, false);
    }
  });
}

/* ============================================================
   ۱۵) راه‌اندازی خودکار
   ============================================================ */
document.addEventListener('DOMContentLoaded', async () => {
  // اول موزیک‌ها رو لود کن
  await loadMusicFromJson();

  // بعد راه‌اندازی کن
  initMobileMenu();
  initToTop();
  initPreloader();
  initMusic();
  initGlobalEffects();
  buildCube();
  initHeroBlocks();
  initSPARouter();

  // صفحه‌های خاص
  if (document.getElementById('modsGrid')) initIndexPage();
  if (document.getElementById('pageContent')) initModPage();
  if (document.querySelector('.platform-tabs')) initGuidePage();
  if (document.getElementById('faqList')) initAboutPage();
});
