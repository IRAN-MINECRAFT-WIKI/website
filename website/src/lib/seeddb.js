// src/lib/seeddb.js
// IndexedDB wrapper for user-saved Minecraft seeds.
//
// Why IndexedDB (not localStorage):
//   • Seeds can have many features + coords — payload per record ~1-3KB.
//   • localStorage has a 5MB ceiling shared with every other key on the
//     origin (music prefs, comments drafts, etc.). A few hundred saved
//     seeds can blow past that limit.
//   • IndexedDB is async, indexes by id+createdAt, survives forever.
//
// This module is browser-only. It is imported from <script> tags inside
// /seeds/create.astro and /seeds/my.astro — never in module frontmatter
// (so Astro's SSG build never tries to run it server-side).

const DB_NAME = 'minebed-seeds';
const DB_VERSION = 1;
const STORE_NAME = 'seeds';

let _dbPromise = null;

/**
 * Open (or create) the IndexedDB database.
 * Cached promise so subsequent callers share the same connection.
 */
export function openDB() {
  if (typeof indexedDB === 'undefined') {
    return Promise.reject(new Error('IndexedDB not supported in this browser'));
  }
  if (_dbPromise) return _dbPromise;

  _dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);

    req.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        store.createIndex('createdAt', 'createdAt', { unique: false });
        store.createIndex('version', 'version', { unique: false });
        store.createIndex('platform', 'platform', { unique: false });
      }
    };

    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error || new Error('Failed to open seed DB'));
  });

  return _dbPromise;
}

/**
 * Save a seed record. Overwrites if same `id` already exists.
 * @param {Object} seed — must have `id`; should also have createdAt.
 * @returns {Promise<string>} id of the saved seed
 */
export async function addSeed(seed) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    // Ensure required fields
    const record = {
      ...seed,
      id: seed.id || (crypto.randomUUID ? crypto.randomUUID() : makeFallbackId()),
      createdAt: seed.createdAt || Date.now(),
    };
    const req = store.put(record);
    req.onsuccess = () => resolve(record.id);
    req.onerror = () => reject(req.error || new Error('Failed to save seed'));
  });
}

/**
 * Return all saved seeds, newest-first.
 * @returns {Promise<Array>}
 */
export async function getAllSeeds() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const idx = store.index('createdAt');
    const req = idx.openCursor(null, 'prev'); // newest first
    const results = [];
    req.onsuccess = () => {
      const cursor = req.result;
      if (cursor) {
        results.push(cursor.value);
        cursor.continue();
      } else {
        resolve(results);
      }
    };
    req.onerror = () => reject(req.error || new Error('Failed to read seeds'));
  });
}

/**
 * Delete a seed by its id.
 * @param {string} id
 * @returns {Promise<void>}
 */
export async function deleteSeed(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.delete(id);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error || new Error('Failed to delete seed'));
  });
}

/**
 * Count saved seeds (without loading the full payload of each).
 * @returns {Promise<number>}
 */
export async function countSeeds() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const req = store.count();
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error || new Error('Failed to count seeds'));
  });
}

function makeFallbackId() {
  return (
    'seed-' +
    Date.now().toString(36) +
    '-' +
    Math.random().toString(36).slice(2, 10)
  );
}
