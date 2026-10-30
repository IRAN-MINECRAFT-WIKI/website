/*
 * Seed Finder Web Worker (module worker).
 * Protocol:
 *   in : {cmd:'find', opts:{count, structIds[], biomeIds[], biomeRadiusBlocks, maxDistBlocks, maxChecked, versionLabel, seedStr}}
 *        {cmd:'stop'}
 *   out: {type:'progress', checked, found}
 *        {type:'done', results:[{seed, spawn:{x,z}, hits:[{id,x,z,dist}], biomeAtSpawn}]}
 */
import { SeedMapEngine } from './engine.js';

let enginePromise = null;
function getEngine() {
  if (!enginePromise) enginePromise = SeedMapEngine.create();
  return enginePromise;
}

let running = false;

self.onmessage = async (ev) => {
  const msg = ev.data || {};
  if (msg.cmd === 'stop') { running = false; return; }
  if (msg.cmd !== 'find') return;
  running = true;
  try {
    await runFind(msg.opts || {});
  } catch (e) {
    postMessage({ type: 'done', results: [] });
  }
};

const tick = () => new Promise((r) => setTimeout(r, 0));

function clampRange(center, span, cap) {
  // region-index range around `center`, capped to `cap` per axis
  let a = Math.floor((center - span) / 1), b = Math.floor((center + span) / 1);
  if (b - a + 1 > cap) {
    const mid = Math.floor((a + b) / 2);
    a = mid - (cap >> 1);
    b = a + cap - 1;
  }
  return [a, b];
}

function nearestStructure(engine, st, spawn, maxDist) {
  const step = 16 * st.rs;
  let rx0 = Math.floor((spawn.x - maxDist) / step);
  let rx1 = Math.floor((spawn.x + maxDist) / step);
  let rz0 = Math.floor((spawn.z - maxDist) / step);
  let rz1 = Math.floor((spawn.z + maxDist) / step);
  const cap = 40; // per axis, keeps tiny-region structures (rs=1) affordable
  if (rx1 - rx0 + 1 > cap) { const mid = (rx0 + rx1) >> 1; rx0 = mid - (cap >> 1); rx1 = rx0 + cap - 1; }
  if (rz1 - rz0 + 1 > cap) { const mid = (rz0 + rz1) >> 1; rz0 = mid - (cap >> 1); rz1 = rz0 + cap - 1; }
  const found = engine.getStructures([st.id], rx0, rz0, rx1, rz1);
  let best = null;
  for (const f of found) {
    const d = Math.hypot(f.x - spawn.x, f.z - spawn.z);
    if (d <= maxDist && (!best || d < best.dist)) {
      best = { id: f.id, x: f.x, z: f.z, dist: Math.round(d) };
    }
  }
  return best;
}

function biomeAtPoint(engine, x, z) {
  try { return engine.biomeAt(x, z); } catch (e) { return -1; }
}

function biomeInRange(engine, spawn, radius, targetIds) {
  if (radius <= 0) {
    const b = biomeAtPoint(engine, spawn.x, spawn.z);
    return targetIds.indexOf(b) !== -1 ? b : null;
  }
  const step = Math.max(32, Math.ceil(radius / 8));
  for (let z = spawn.z - radius; z <= spawn.z + radius; z += step) {
    for (let x = spawn.x - radius; x <= spawn.x + radius; x += step) {
      const b = biomeAtPoint(engine, x, z);
      if (b >= 0 && targetIds.indexOf(b) !== -1) return b;
    }
  }
  // also probe the exact spawn point
  const bc = biomeAtPoint(engine, spawn.x, spawn.z);
  return targetIds.indexOf(bc) !== -1 ? bc : null;
}

async function runFind(opts) {
  const engine = await getEngine();
  try { engine.setVersion(opts.versionLabel || engine.version); } catch (e) { /* keep default */ }

  const count = Math.max(1, Math.min(20, opts.count | 0 || 3));
  const maxChecked = Math.max(1, opts.maxChecked | 0 || 200000);
  const structIds = Array.isArray(opts.structIds) ? opts.structIds.slice(0, 6) : [];
  const biomeIds = Array.isArray(opts.biomeIds) ? opts.biomeIds.map(Number).filter((n) => n >= 0) : [];
  const maxDist = Math.max(0, opts.maxDistBlocks | 0 || 800);
  const radius = Math.max(0, opts.biomeRadiusBlocks | 0 || 0);

  const structs = structIds
    .map((id) => {
      const meta = (engine.structures || []).find((s) => s.id === id);
      return meta ? { id, rs: meta.regionSize || 1 } : null;
    })
    .filter(Boolean);

  const results = [];
  let checked = 0;
  let lastPost = Date.now();

  while (running && results.length < count && checked < maxChecked) {
    const seedStr = engine.randomSeed();
    engine.setSeed(seedStr);
    checked++;

    const spawn = engine.getSpawn();
    if (spawn) {
      let ok = true;
      const hits = [];
      for (const st of structs) {
        const best = nearestStructure(engine, st, spawn, maxDist);
        if (!best) { ok = false; break; }
        hits.push(best);
      }
      let biomeAtSpawn = null;
      if (ok && biomeIds.length) {
        const found = biomeInRange(engine, spawn, radius, biomeIds);
        if (found == null) ok = false;
        else biomeAtSpawn = found;
      }
      if (ok) {
        if (biomeAtSpawn == null) biomeAtSpawn = biomeAtPoint(engine, spawn.x, spawn.z);
        results.push({ seed: seedStr, spawn, hits, biomeAtSpawn });
        if (results.length >= count) break;
      }
    }

    if (Date.now() - lastPost > 300) {
      lastPost = Date.now();
      postMessage({ type: 'progress', checked, found: results.length });
      await tick();
    } else if ((checked & 255) === 0) {
      await tick(); // let stop messages through
    }
  }

  postMessage({ type: 'progress', checked, found: results.length });
  postMessage({ type: 'done', results });
}
