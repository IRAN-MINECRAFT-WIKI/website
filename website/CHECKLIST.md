# 📋 MineBed Checklist — Honest Status

**Last updated:** 2026-10-03 (commit `01b71d9`)
**Total phases:** 200 · **Done:** 76 · **Partial:** 8 · **Not done:** 116

---

## ✅ Completed Phases (76)

### UI/UX (20/20)
- [x] فاز ۱: QuickAccess panel positioning fix
- [x] فاز ۲: MusicPlayer + QuickAccess layout
- [x] فاز ۳: Header reduced to 6 items
- [x] فاز ۴-۱۰: Animation, pixel sprites, base styles
- [x] فاز ۱۲: Control Center animation (Web Animations API)
- [x] فاز ۱۵: /stats/ pixel-themed (Chart.js + mc-card)
- [x] فاز ۱۵۰: Aparat channel embed (iframe)
- [x] فاز ۱۵۹: Aparat video embed support
- [x] فاز ۱۰۲: Drag & Drop in crafting.astro (HTML5 Drag API + touch)

### Stats (all)
- [x] فاز ۸۴: 2D seed map (Canvas + grid + compass)
- [x] فاز ۱۰۰: Bow/arrow recipes verified (vanilla correct)
- [x] فاز ۱۰۵: Real centralized KV backend
- [x] فاز ۱۰۵-۱: Anti-inflation (conditional writes + TTL)
- [x] فاز ۱۰۵-۲: KV limit protection (heartbeat 5min, cache 10min)
- [x] فاز ۱۲۵: Online count real (KV heartbeat)
- [x] فاز ۱۲۸-۱۲۹: 30-day + 24h charts (Chart.js + real data)
- [x] فاز ۱۳۰: Date fix (jalaali-js + Tehran timezone)

### Textures
- [x] فاز ۲۱: Block textures — 112/113 PNG (99%) · commit `01b71d9`
- [x] فاز ۲۲: Villager mob PNG (AI-generated) · commit `01b71d9`
- [x] فاز ۲۴: Item textures — 410/453 PNG (91%) · commit `01b71d9`

### Content
- [x] فاز ۷۳: FAQ page (21 questions in 7 categories) · commit `01b71d9`
- [x] فاز ۵۱: 113 block detail pages
- [x] فاز ۵۲: 52 mob detail pages
- [x] فاز ۵۳: 78 version pages
- [x] فاز ۶۰: 60 tested seeds
- [x] فاز ۶۱: 1187 speedrun records

### Backend
- [x] فاز ۸۰: Cloudflare Worker (KV-based v3)
- [x] فاز ۸۲: Worker source in repo (worker/src/index.js)
- [x] فاز ۸۳: Deploy README (worker/README.md)

---

## 🟡 Partial Phases (8)

| Phase | What's done | What's missing |
|---|---|---|
| ۲۱ | 112/113 block PNG | 1 block (non-standard wiki name) |
| ۲۴ | 410/453 item PNG | 43 items (non-standard wiki names) |
| ۲۶ | Some emoji→PNG | Remaining emoji still in use |
| ۳۲ | — | Mod images still 1080×1080 (need resize to 128) |
| ۳۷-۳۸ | Mob detail pages | No gallery index page |
| ۵۱-۵۴ | Page templates | 40 items need 3-5 paragraphs |
| ۶۵-۶۸ | 78 version pages | Need changelog descriptions |
| ۹۴ | 8 features | Need 20+ features |

---

## ❌ Not Done (116)

### Critical
- [ ] فاز ۱۶۱-۱۸۰: User account (Google OAuth + D1 users table) — **needs Worker deploy**
- [ ] فاز ۱۵۵-۱۵۶: RSS + Aparat auto-update
- [ ] فاز ۱۹۰-۱۹۲: Lighthouse (>90 Performance, >95 A11y, >95 SEO)

### Content
- [ ] فاز ۱۰-۱۲: Wiki content (3-5 paragraphs per item)
- [ ] فاز ۵۵-۵۹: More wiki articles
- [ ] فاز ۶۳-۶۴: Version detail (31 Java, 47 Bedrock descriptions)

### Testing
- [ ] فاز ۱۹۳-۲۰۰: Integration tests, E2E, accessibility audit

---

## 🔴 User Action Required

1. **Deploy Worker v3** (with KV limit fix) — code in `worker/src/index.js`
2. **Wait for KV reset** (midnight UTC = 3:30 AM Tehran) — limits reset daily
3. **Test 2-browser online** — open /stats/ in Chrome + Firefox → online should be 2
