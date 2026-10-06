#!/usr/bin/env python3
"""Find block JSON files with empty intro arrays; sort by importance."""
import json
from pathlib import Path

BLOCKS_DIR = Path("/home/z/imc-website/website/src/data/blocks")

# Priority list — well-known blocks first
PRIORITY = [
    # Building blocks / classics
    "dirt", "coarse-dirt", "grass-block", "mycelium", "podzol", "sand", "red-sand",
    "gravel", "clay", "snow-block", "ice", "packed-ice", "blue-ice",
    "oak-log", "spruce-log", "birch-log", "jungle-log", "acacia-log",
    "dark-oak-log", "mangrove-log", "cherry-log", "pale-oak-log",
    "oak-planks", "spruce-planks", "birch-planks", "jungle-planks",
    "acacia-planks", "dark-oak-planks", "mangrove-planks", "cherry-planks",
    "oak-leaves", "spruce-leaves", "birch-leaves", "jungle-leaves",
    "acacia-leaves", "dark-oak-leaves", "mangrove-leaves", "cherry-leaves",
    "glass", "glass-pane", "tinted-glass",
    "oak-wood", "spruce-wood", "birch-wood", "jungle-wood",
    "acacia-wood", "dark-oak-wood", "mangrove-wood",
    "bricks", "bookshelf", "black-wool", "white-wool", "wool",
    # Stones / minerals
    "cobblestone", "mossy-cobblestone", "smooth-stone", "stone-bricks",
    "mossy-stone-bricks", "cracked-stone-bricks", "chiseled-stone-bricks",
    "granite", "diorite", "andesite", "polished-granite", "polished-diorite",
    "polished-andesite", "deepslate", "cobbled-deepslate", "deepslate-bricks",
    "deepslate-tiles", "tuff", "calcite", "dripstone-block", "pointed-dripstone",
    "bedrock", "obsidian", "crying-obsidian", "netherrack", "end-stone",
    "glowstone", "sea-lantern", "soul-sand", "soul-soil", "magma-block",
    "basalt", "smooth-basalt", "blackstone", "basalt-delta-ash",
    # Ores
    "coal-ore", "iron-ore", "gold-ore", "redstone-ore", "lapis-ore",
    "diamond-ore", "emerald-ore", "nether-gold-ore", "nether-quartz-ore",
    "ancient-debris", "deepslate-coal-ore", "deepslate-iron-ore",
    "deepslate-gold-ore", "deepslate-redstone-ore", "deepslate-diamond-ore",
    "deepslate-emerald-ore", "deepslate-lapis-ore",
    # Storage blocks
    "coal-block", "iron-block", "gold-block", "diamond-block", "emerald-block",
    "lapis-block", "redstone-block", "netherite-block", "hay-block",
    "honey-block", "honeycomb-block", "slime-block",
    # Liquids & nature
    "water", "lava", "fire", "soul-fire", "cactus", "bamboo", "sugar-cane",
    "pumpkin", "carved-pumpkin", "melon", "wheat", "hay-block",
    "vines", "glow-lichen", "moss-block", "moss-carpet", "spore-blossom",
    # Industrial / redstone
    "furnace", "blast-furnace", "smoker", "crafting-table",
    "chest", "trapped-chest", "ender-chest", "shulker-box", "barrel",
    "hopper", "dropper", "piston", "daylight-detector",
    "redstone-wire", "redstone-torch", "redstone-block", "redstone-lamp",
    "stone-pressure-plate", "oak-pressure-plate", "stone-button",
    "oak-button", "tripwire-hook", "tripwire", "target",
    "iron-door", "iron-trapdoor", "iron-bars",
    "tnt", "note-block", "jukebox", "enchanting-table",
    "anvil", "chipped-anvil", "damaged-anvil", "brewing-stand", "cauldron",
    "composter", "loom", "cartography-table", "grindstone", "stonecutter",
    "fletching-table", "smithing-table", "smoker",
    # Slabs/stairs/walls/fences (mostly common ones)
    "oak-slab", "stone-slab", "cobblestone-slab", "stone-brick-slab",
    "oak-stairs", "stone-stairs", "cobblestone-stairs", "stone-brick-stairs",
    "oak-fence", "nether-brick-fence",
    # Decor / utility
    "ladder", "torch", "lantern", "soul-torch", "soul-lantern",
    "painting", "item-frame", "flower-pot", "armor-stand",
    "oak-door", "oak-trapdoor", "oak-fence-gate",
    "bed", "cake", "flower-pot",
    # Plants / flowers
    "dandelion", "poppy", "blue-orchid", "allium", "azure-bluet",
    "red-tulip", "orange-tulip", "white-tulip", "pink-tulip",
    "oxeye-daisy", "cornflower", "lily-of-the-valley", "wither-rose",
    "sunflower", "lilac", "rose-bush", "peony", "tall-grass",
    "fern", "grass", "dead-bush", "sugar-cane",
    # Nether stuff
    "nether-bricks", "nether-brick-fence", "nether-brick-stairs",
    "glowstone", "nether-portal", "lava", "obsidian",
    "crimson-planks", "warped-planks", "crimson-stem", "warped-stem",
    "crimson-nylium", "warped-nylium", "shroomlight", "crimson-fungus",
    "warped-fungus", "weeping-vines", "twisting-vines", "nether-sprouts",
    # End stuff
    "end-stone", "end-stone-bricks", "purpur-block", "purpur-pillar",
    "end-rod", "end-portal-frame", "end-portal", "end-gateway",
    # Sandstone variants
    "sandstone", "red-sandstone", "smooth-sandstone", "smooth-red-sandstone",
    "cut-sandstone", "cut-red-sandstone", "chiseled-sandstone",
    "chiseled-red-sandstone",
    # Wood stuff
    "oak-leaves", "oak-log", "oak-sapling", "oak-planks",
    # Concrete / terracotta
    "terracotta", "white-terracotta", "orange-terracotta",
    "white-concrete", "orange-concrete", "white-concrete-powder",
    "white-wool", "white-carpet", "white-stained-glass",
    # More misc
    "dirt-path", "farmland", "lectern", "loom", "blast-furnace",
    "respawn-anchor", "lodestone", "target", "honey-block",
    "scaffolding", "beehive", "bee-nest",
    # Rails
    "rail", "powered-rail", "detector-rail", "activator-rail",
]

files = sorted(BLOCKS_DIR.glob("*.json"))
empties = []
all_data = {}
for f in files:
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERR {f.name}: {e}")
        continue
    bid = data.get("id") or f.stem
    intro = data.get("intro")
    if not intro or (isinstance(intro, list) and len(intro) == 0):
        empties.append(bid)
    all_data[bid] = data

# Sort: priority first (by index in PRIORITY list), rest alphabetical
def sort_key(b):
    if b in PRIORITY:
        return (0, PRIORITY.index(b))
    return (1, b)

empties_sorted = sorted(empties, key=sort_key)
print(f"Total blocks: {len(files)}")
print(f"Blocks with empty intro: {len(empties)}")
print("\nTop 120 (priority first):")
for i, b in enumerate(empties_sorted[:120], 1):
    print(f"  {i:3d}. {b}")
