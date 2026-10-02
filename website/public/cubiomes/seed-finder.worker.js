// Browser Web Worker for seed finding
// Uses mc-seedlocator (Cubiomes WASM) loaded from same directory
importScripts('./locator.js');

self.onmessage = async (e) => {
  const { seed, features, x, z } = e.data;
  try {
    const params = {
      tileSize: 16,
      searchWidth: 8,
      edition: 'Java',
      javaVersion: 10200,
      tileScale: 0.25,
      dimension: 'overworld',
      biomeHeight: 'worldSurface',
    };
    const result = await getAreaResult(String(seed), [x || 0, z || 0], features, params);
    self.postMessage({ ok: true, seed, features, result });
  } catch (err) {
    self.postMessage({ ok: false, seed, error: err.message });
  }
};
