#!/usr/bin/env python3
"""Download real Minecraft textures for newly-added blocks.

For each block JSON in src/data/blocks/*.json that has no corresponding
texture in public/textures/blocks/{id}.png, fetches the real Minecraft
texture from the InventivetalentDev minecraft-assets GitHub repo
(version 1.21.11) and saves it locally.

If a file 404s we move on silently.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKS_DIR = ROOT / "src" / "data" / "blocks"
TEX_DIR = ROOT / "public" / "textures" / "blocks"

ASSETS_BASE = ("https://raw.githubusercontent.com/InventivetalentDev/"
               "minecraft-assets/1.21.11/assets/minecraft/textures/block/")

UA = "iran-minecraft-wiki/1.0 (github.com/IRAN-MINECRAFT-WIKI/website)"

# id → texture filename (snake_case) with special mappings
SPECIAL_TEX_MAP = {
    # block-of-X → block_of_X
    "diamond-block": "diamond_block",
    "iron-block": "iron_block",
    "gold-block": "gold_block",
    "emerald-block": "emerald_block",
    "coal-block": "coal_block",
    "copper-block": "copper_block",
    "netherite-block": "netherite_block",
    "amethyst-block": "amethyst_block",
    "lapis-block": "lapis_block",
    "raw-iron-block": "raw_iron_block",
    "raw-copper-block": "raw_copper_block",
    "raw-gold-block": "raw_gold_block",
    "bamboo-block": "bamboo_block",
    "stripped-bamboo-block": "stripped_bamboo_block",
    "resin-block": "resin_block",
    # saplings
    "oak-sapling": "oak_sapling",
    "spruce-sapling": "spruce_sapling",
    "birch-sapling": "birch_sapling",
    "jungle-sapling": "jungle_sapling",
    "acacia-sapling": "acacia_sapling",
    "dark-oak-sapling": "dark_oak_sapling",
    "cherry-sapling": "cherry_sapling",
    "pale-oak-sapling": "pale_oak_sapling",
    # doors
    "iron-door": "iron_door",
    "iron-trapdoor": "iron_trapdoor",
    # plants / natural
    "cornflower": "cornflower",
    "sunflower": "sunflower_top",
    "rose-bush": "rose_bush_top",
    "dead-bush": "dead_bush",
    "bush": "bush",
    "wildflowers": "wildflowers",
    "cactus-flower": "cactus_flower",
    "firefly-bush": "firefly_bush",
    "leaf-litter": "leaf_litter",
    "powder-snow": "powder_snow",
    "spore-blossom": "spore_blossom",
    "torchflower": "torchflower",
    "torchflower-seeds": "torchflower_crop_stage3",  # final-stage crop
    "wheat-seeds": "wheat_stage7",  # final-stage crop
    "nether-wart": "nether_wart_stage2",  # final-stage crop
    "resin-clump": "resin_clump",
    # grass variants
    "short-grass": "short_grass",
    "tall-grass": "tall_grass_top",
    "short-dry-grass": "short_dry_grass",
    "tall-dry-grass": "tall_dry_grass_top",
    # snow / ice
    "chiseled-packed-ice": "chiseled_packed_ice",
    "packed-ice-bricks": "packed_ice_bricks",
    "packed-ice-brick-slab": "packed_ice_brick_slab_top",
    "packed-ice-brick-stairs": "packed_ice_brick_stairs",
    "packed-ice-brick-wall": "packed_ice_brick_wall_post",
    "snow-bricks": "snow_bricks",
    "snow-brick-slab": "snow_brick_slab_top",
    "snow-brick-stairs": "snow_brick_stairs",
    "snow-brick-wall": "snow_brick_wall_post",
    # mechanism / utility
    "heavy-core": "heavy_core",
    "monster-spawner": "spawner",
    "ominous-trial-spawner": "trial_spawner_ominous",
    "ominous-vault": "vault_ominous",
    "ominous-banner": "gray_banner",  # generic stand-in
    "glow-item-frame": "glow_item_frame",
    "redstone-torch": "redstone_torch",
    "string": "tripwire",
    "bubble-column": "bubble_column_up",
    "petrified-oak-slab": "petrified_oak_slab_top",
    # technical blocks
    "fire": "fire_0",
    "end-portal": "end_portal",
    "end-gateway": "end_gateway",
    "nether-portal": "nether_portal",
}


def id_to_tex_name(bid: str) -> str:
    if bid in SPECIAL_TEX_MAP:
        return SPECIAL_TEX_MAP[bid]
    return bid.replace("-", "_")


def fetch(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            if r.status != 200:
                return False
            data = r.read()
        dest.write_bytes(data)
        return True
    except Exception as e:
        return False


def main() -> int:
    TEX_DIR.mkdir(parents=True, exist_ok=True)

    # Get list of newly-added block ids (from the summary file written by
    # add_missing_blocks.py).
    summary_path = Path("/tmp/added_blocks_summary.json")
    if not summary_path.exists():
        # Fall back: process every block file that doesn't have a texture.
        new_ids = [
            fp.stem for fp in BLOCKS_DIR.glob("*.json")
            if fp.stem != "index"
            and not (TEX_DIR / f"{fp.stem}.png").exists()
        ]
    else:
        with open(summary_path) as f:
            summary = json.load(f)
        new_ids = summary["added"]

    print(f">> checking textures for {len(new_ids)} new blocks")
    downloaded = 0
    failed = []
    for bid in new_ids:
        dest = TEX_DIR / f"{bid}.png"
        if dest.exists():
            continue
        tex_name = id_to_tex_name(bid)
        url = ASSETS_BASE + tex_name + ".png"
        if fetch(url, dest):
            downloaded += 1
            print(f"   + {bid}.png  ←  {tex_name}.png")
        else:
            failed.append(bid)
            # Try alternate names (without _top/_post suffixes).
            alt_urls = []
            for suffix in ("_top", "_side", "_post", "_front", "_bottom", "_0"):
                if tex_name.endswith(suffix):
                    alt = tex_name[: -len(suffix)]
                    alt_urls.append(ASSETS_BASE + alt + ".png")
            for alt in alt_urls:
                if fetch(alt, dest):
                    downloaded += 1
                    print(f"   + {bid}.png  ←  fallback {alt.split('/')[-1]}")
                    failed.remove(bid)
                    break

    print(f"\n>> downloaded {downloaded} textures")
    if failed:
        print(f"   failed ({len(failed)}): {failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
