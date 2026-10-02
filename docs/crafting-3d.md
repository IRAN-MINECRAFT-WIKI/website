# Crafting 3D — Interactive Crafting Table

> 🚧 **This document is a placeholder.** The full content will be filled in by the parent agent when the 3D crafting viewer ships. This file is committed now so the docs index has a stable link.

## What this is

The Crafting 3D viewer is a planned interactive component that renders a Minecraft crafting table as a 3D model the user can rotate, zoom, and click. Each item slot in the grid is a real 3D cube with the item's texture on its faces; clicking a slot opens the same recipe panel that the existing 2D crafting grid already supports.

## Status

- **Today**: the 2D crafting table at `/crafting` is the working interactive crafting viewer. It is built from `website/src/pages/crafting.astro` + the `CraftingGrid` / `InventorySlot` components, reading recipes from `website/src/data/crafting-recipes.json`.
- **Planned (this doc's subject)**: a 3D upgrade — same data, same interactions, but rendered with `skinview3d` / `three.js` so the table looks like an in-world Minecraft block rather than a flat UI.

## Why 3D?

- Engagement: a rotating 3D model is more visually interesting than a 2D grid.
- Accessibility: showing the table from multiple angles can help users understand the spatial relationships in complex recipes (e.g. shaped vs shapeless).
- Showcases the project's existing 3D capability (the `/3d` page uses `three.js` for the Steve viewer — the crafting table can reuse the same code path).

## Architecture sketch (to be detailed by parent agent)

```
website/src/components/CraftingGrid3D.astro   ← new component, replaces CraftingGrid on /crafting when ?view=3d
website/src/data/crafting-recipes.json        ← unchanged, same data source
website/src/pages/crafting.astro               ← adds a 2D/3D toggle button at the top
public/textures/items/*.png                   ← reused for the 3D item faces
public/textures/blocks/crafting-table-*.png    ← reused for the table body
```

## Open questions (resolve before implementing)

1. **Page weight**: the 3D viewer requires loading `three.js` (~150KB gzipped). Currently `/crafting` ships at ~80KB total. Adding 3D doubles the page weight. Lazy-load the 3D viewer only when the user clicks the toggle, or default to 2D and load 3D on demand.
2. **Mobile performance**: low-end Android phones struggle with three.js. Provide a "force 2D" mode for `navigator.hardwareConcurrency <= 4` or `navigator.deviceMemory < 4`.
3. **Texture UV mapping**: Minecraft item textures are 16×16 PNGs. Mapping them onto a 3D cube's face is straightforward (use the texture as a `THREE.MeshStandardMaterial.map`), but inventory items that should appear "flat" (like swords / pickaxes) need a billboarded plane rather than a cube.
4. **Camera control**: OrbitControls is the obvious choice, but the default zoom range is wrong for a single-block table. Tune to `minDistance: 5, maxDistance: 25, initialDistance: 12`.
5. **Sound design**: add the satisfying "click" sound on slot placement (8-bit WAV file from Minecraft assets, <5KB).

## To be filled by the parent agent

- [ ] Final component path + name
- [ ] 2D vs 3D toggle UX
- [ ] Mobile performance budget + the threshold used
- [ ] Texture atlas approach (one big atlas vs many small PNGs)
- [ ] Camera defaults
- [ ] Animation timings
- [ ] Accessibility fallback (screen reader description of the 3D scene)
- [ ] Screenshot paths in `/home/z/my-project/screenshots-crafting-3d/`
- [ ] VLM verification results

## Related files

| File / Path                                             | Role                                                  |
| ------------------------------------------------------- | ----------------------------------------------------- |
| `website/src/pages/crafting.astro`                       | The /crafting page — the 2D table today.              |
| `website/src/components/CraftingGrid.astro`              | 2D crafting grid component.                          |
| `website/src/components/InventorySlot.astro`             | One slot in the 2D grid.                              |
| `website/src/data/crafting-recipes.json`                | Recipe data (shaped, shapeless, etc.).                |
| `website/src/components/Cube3D.astro`                    | Existing 3D cube component (used on `/3d`).            |
| `public/textures/items/*.png`                           | Item textures for the 3D cube faces.                  |
| `public/textures/blocks/crafting-table-*.png`            | Crafting-table side/top/bottom textures.              |
