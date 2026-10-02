// Seed Finder Worker — uses mc-seedlocator (Cubiomes WASM)
// Runs in a Web Worker so the main thread doesn't freeze.
import { getAreaResult } from 'mc-seedlocator';

const params = {
  tileSize: 16,
  searchWidth: 8,
  edition: 'Java',
  javaVersion: 10200,
  tileScale: 0.25,
  dimension: 'overworld',
  biomeHeight: 'worldSurface',
};

self.onmessage = async (e) => {
  const { seed, features, x = 0, z = 0 } = e.data;
  try {
    const result = await getAreaResult(String(seed), [x, z], features, params);
    self.postMessage({ ok: true, seed, features, result });
  } catch (err) {
    self.postMessage({ ok: false, seed, error: err.message });
  }
};
