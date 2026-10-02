#!/usr/bin/env python3
"""
gen_recipes.py — Expand MineBed crafting-recipes.json from 33 → 300+ recipes.

⚠️  ONE-SHOT GENERATOR — DO NOT RE-RUN BLINDLY.  ⚠️

This script loads the current crafting-recipes.json, treats its existing recipes
as the "base 33" (assigning category + icon to each by ID lookup), then APPENDS
~270 hard-coded new recipes. If you re-run it after the first run, the "base"
will be 300 recipes and almost every NEW_RECIPES entry will be a duplicate,
filtered out — leaving you with 300 recipes but most having lost their category
and icon (defaulted to misc + 📦).

To regenerate from scratch:
  1. `git checkout website/src/data/crafting-recipes.json`  (restore 33-recipe original)
  2. `python3 scripts/gen_recipes.py`                       (re-expand to 300)

Output: /home/z/work/imc-website/website/src/data/crafting-recipes.json
Schema (compatible with existing /crafting page):
{
  "recipes": [
    {
      "id": "unique-id",
      "nameFa": "Persian name",
      "nameEn": "English Name",
      "aliases": ["..."],
      "category": "combat|tools|building|redstone|food|brewing|misc",
      "grid": [[null/item, null/item, null/item], [...], [...]],
      "output": { "item": "id", "count": N, "type": "block"? },
      "icon": "emoji-fallback",
      "wikiSlug": "crafting-recipes",
      "shapeless": false,
      "description": "Persian description"
    },
    ...
  ],
  "itemIcons": { "item-name": "emoji", ... }   # for grid slot icon fallback
}
"""

import json
import os
import sys
from collections import OrderedDict

OUTPUT_PATH = "/home/z/work/imc-website/website/src/data/crafting-recipes.json"
EXISTING_PATH = OUTPUT_PATH  # we modify in-place

# Safety check: refuse to run if the file already has > 50 recipes (re-run guard).
if os.path.exists(EXISTING_PATH):
    with open(EXISTING_PATH, "r", encoding="utf-8") as f:
        _existing_check = json.load(f)
    _existing_count = len(_existing_check.get("recipes", []))
    if _existing_count > 50 and "--force" not in sys.argv:
        print(f"ERROR: {EXISTING_PATH} already has {_existing_count} recipes.")
        print("This script is a one-shot expander. To regenerate:")
        print("  1. git checkout website/src/data/crafting-recipes.json  (restore 33)")
        print("  2. python3 scripts/gen_recipes.py")
        print("Or pass --force to override this guard (will corrupt the JSON).")
        sys.exit(1)

# ─── Categories ───────────────────────────────────────────────────────────────
COMBAT = "combat"
TOOLS = "tools"
BUILDING = "building"
REDSTONE = "redstone"
FOOD = "food"
BREWING = "brewing"
MISC = "misc"

WIKI = "crafting-recipes"

# ─── Item-icon emoji map (for grid slot fallback when PNG missing) ──────────
# Used by crafting.astro client JS as fallback when an item's PNG fails to load.
# Keys are kebab-case item IDs matching what we use in the `grid` arrays.
ITEM_ICONS = {
    # ─── base materials ───
    "stick": "🪵",
    "string": "🧵",
    "feather": "🪶",
    "flint": "🪨",
    "leather": "🟫",
    "paper": "📄",
    "book": "📘",
    "book-and-quill": "🖋️",
    "sugar": "🍬",
    "wheat": "🌾",
    "wheat-seeds": "🌱",
    "sugar-cane": "🎋",
    "apple": "🍎",
    "carrot": "🥕",
    "potato": "🥔",
    "baked-potato": "🍠",
    "beetroot": "🫐",
    "melon-slice": "🍉",
    "melon-seeds": "🌱",
    "pumpkin": "🎃",
    "pumpkin-seeds": "🌱",
    "cocoa-beans": "🟤",
    "brown-mushroom": "🍄",
    "red-mushroom": "🍄",
    "egg": "🥚",
    "bowl": "🥣",
    "milk-bucket": "🥛",
    "honey-bottle": "🍯",
    "honeycomb": "🐝",
    "honey-block": "🍯",
    "rabbit": "🐇",
    "cooked-rabbit": "🍖",
    "slimeball": "🟢",
    "clay": "🧱",
    "brick-item": "🧱",
    "sand": "🏜️",
    "red-sand": "🏜️",
    "gravel": "🪨",
    "snowball": "❄️",
    "bone-meal": "🦴",
    "bone": "🦴",
    "dye": "🎨",
    "white-dye": "⚪",
    "red-dye": "🔴",
    "blue-dye": "🔵",
    "green-dye": "🟢",
    "yellow-dye": "🟡",
    "black-dye": "⚫",
    "orange-dye": "🟠",
    "purple-dye": "🟣",
    "ink-sac": "🦑",
    # ─── ingots / gems ───
    "iron-ingot": "🔩",
    "gold-ingot": "🟨",
    "copper-ingot": "🟧",
    "netherite-ingot": "⬛",
    "diamond": "💎",
    "emerald": "💚",
    "coal": "⚫",
    "charcoal": "⚫",
    "lapis-lazuli": "🔵",
    "quartz": "🔮",
    "nether-quartz": "🔮",
    "gold-nugget": "🟡",
    "iron-nugget": "🔩",
    "prismarine-shard": "💠",
    "prismarine-crystals": "✨",
    # ─── mob drops ───
    "blaze-rod": "🔥",
    "blaze-powder": "🔥",
    "spider-eye": "👁️",
    "fermented-spider-eye": "👁️",
    "ghast-tear": "💧",
    "ender-pearl": "🔮",
    "ender-eye": "👁️",
    "nether-star": "⭐",
    "shulker-shell": "🐚",
    "nautilus-shell": "🐚",
    "heart-of-the-sea": "💗",
    "scute": "🐢",
    "turtle-shell": "🐢",
    "magma-cream": "🔥",
    "popped-chorus-fruit": "🌸",
    "chorus-fruit": "🌸",
    "dragon-breath": "🐉",
    "nether-wart": "🌱",
    "nether-wart-block": "🌱",
    # ─── planks / wood ───
    "oak-planks": "🪵",
    "spruce-planks": "🪵",
    "birch-planks": "🪵",
    "jungle-planks": "🪵",
    "acacia-planks": "🪵",
    "dark-oak-planks": "🪵",
    "oak-log": "🪵",
    "spruce-log": "🪵",
    "birch-log": "🪵",
    "oak-slab": "▬",
    "spruce-slab": "▬",
    "birch-slab": "▬",
    "smooth-stone-slab": "▬",
    "cobblestone-slab": "▬",
    "stone-brick-slab": "▬",
    # ─── stone ───
    "stone": "🪨",
    "cobblestone": "🪨",
    "mossy-cobblestone": "🪨",
    "stone-bricks": "🧱",
    "mossy-stone-bricks": "🧱",
    "cracked-stone-bricks": "🧱",
    "chiseled-stone-bricks": "🧱",
    "end-stone": "🟨",
    "end-stone-bricks": "🧱",
    "andesite": "🪨",
    "diorite": "🪨",
    "granite": "🪨",
    "polished-andesite": "🪨",
    "polished-diorite": "🪨",
    "polished-granite": "🪨",
    "sandstone": "🟫",
    "red-sandstone": "🟧",
    "cut-sandstone": "🟫",
    "chiseled-sandstone": "🟫",
    "quartz-block": "⬜",
    "quartz-pillar": "⬜",
    "purpur-block": "🟣",
    "purpur-pillar": "🟣",
    "bricks": "🧱",
    "nether-bricks": "🟥",
    "blackstone": "⬛",
    "basalt": "⬛",
    # ─── redstone ───
    "redstone": "🔴",
    "redstone-block": "🔴",
    "redstone-torch": "🔦",
    "redstone-lamp": "💡",
    "lever": "🎚️",
    "repeater": "🔁",
    "comparator": "⚖️",
    "observer": "👁️",
    "piston": "🔧",
    "sticky-piston": "🔧",
    "dispenser": "🔫",
    "dropper": "📤",
    "hopper": "⬇️",
    "daylight-detector": "☀️",
    "note-block": "🎵",
    "tripwire-hook": "🪝",
    "target": "🎯",
    "rail": "🛤️",
    "powered-rail": "🛤️",
    "detector-rail": "🛤️",
    "activator-rail": "🛤️",
    "lightning-rod": "⚡",
    "tripwire-hook-item": "🪝",
    # ─── storage / utility ───
    "chest": "📦",
    "ender-chest": "📦",
    "trapped-chest": "📦",
    "crafting-table": "🛠️",
    "furnace": "🔥",
    "blast-furnace": "🔥",
    "smoker": "🔥",
    "brewing-stand": "⚗️",
    "cauldron": "🪣",
    "enchanting-table": "📚",
    "anvil": "🔨",
    "beacon": "🁢",
    "conduit": "🌀",
    "sea-lantern": "💡",
    "glowstone": "✨",
    "lantern": "🏮",
    "soul-lantern": "🏮",
    "torch": "🔦",
    "soul-torch": "🔦",
    "campfire": "🔥",
    "soul-campfire": "🔥",
    "bucket": "🪣",
    "water-bucket": "🪣",
    "lava-bucket": "🪣",
    "milk-bucket": "🥛",
    "item-frame": "🖼️",
    "flower-pot": "🪴",
    "jukebox": "🎵",
    "barrel": "🛢️",
    "end-crystal": "💎",
    "respawn-anchor": "🌑",
    "lodestone": "🧭",
    "armor-stand": "🧍",
    "lectern": "📚",
    "loom": "🧵",
    "cartography-table": "🗺️",
    "fletching-table": "🏹",
    "smithing-table": "🔨",
    "grindstone": "🪨",
    "stonecutter": "🪚",
    "bookshelf": "📚",
    "ladder": "🪜",
    "boat": "🚣",
    "spruce-boat": "🚣",
    "birch-boat": "🚣",
    "bed": "🛏️",
    "red-bed": "🛏️",
    "white-bed": "🛏️",
    "blue-bed": "🛏️",
    "green-bed": "🛏️",
    "yellow-bed": "🛏️",
    "red-wool-bed": "🛏️",
    "blue-wool-bed": "🛏️",
    "green-wool-bed": "🛏️",
    "yellow-wool-bed": "🛏️",
    "painting": "🖼️",
    "banner": "🚩",
    "white-banner": "🚩",
    "shield": "🛡️",
    "fishing-rod": "🎣",
    "shears": "✂️",
    "flint-and-steel": "🔥",
    "compass": "🧭",
    "clock": "🕐",
    "map": "🗺️",
    "empty-map": "🗺️",
    "firework-rocket": "🎆",
    "firework-star": "✨",
    "lead": "🪢",
    "spyglass": "🔭",
    "name-tag": "🏷️",
    "saddle": "🐴",
    # ─── wool / carpet / glass / terracotta ───
    "wool": "🧶",
    "white-wool": "🧶",
    "red-wool": "🟥",
    "blue-wool": "🟦",
    "green-wool": "🟩",
    "yellow-wool": "🟨",
    "black-wool": "⬛",
    "orange-wool": "🟧",
    "carpet": "🟥",
    "white-carpet": "⬜",
    "red-carpet": "🟥",
    "blue-carpet": "🟦",
    "green-carpet": "🟩",
    "yellow-carpet": "🟨",
    "glass": "🪟",
    "glass-pane": "🪟",
    "white-stained-glass": "🪟",
    "red-stained-glass": "🪟",
    "blue-stained-glass": "🪟",
    "green-stained-glass": "🪟",
    "yellow-stained-glass": "🪟",
    "white-stained-glass-pane": "🪟",
    "red-stained-glass-pane": "🪟",
    "blue-stained-glass-pane": "🪟",
    "green-stained-glass-pane": "🪟",
    "yellow-stained-glass-pane": "🪟",
    "terracotta": "🟫",
    "white-terracotta": "⬜",
    "red-terracotta": "🟥",
    "blue-terracotta": "🟦",
    "green-terracotta": "🟩",
    "yellow-terracotta": "🟨",
    "white-glazed-terracotta": "🟧",
    "white-concrete-powder": "⬜",
    "red-concrete-powder": "🟥",
    "blue-concrete-powder": "🟦",
    "green-concrete-powder": "🟩",
    "yellow-concrete-powder": "🟨",
    # ─── pressure plates / buttons ───
    "wooden-pressure-plate": "🔛",
    "stone-pressure-plate": "🔛",
    "oak-pressure-plate": "🔛",
    "spruce-pressure-plate": "🔛",
    "birch-pressure-plate": "🔛",
    "wooden-button": "🔘",
    "stone-button": "🔘",
    "oak-button": "🔘",
    "spruce-button": "🔘",
    "birch-button": "🔘",
    # ─── doors / trapdoors / signs / fences / walls ───
    "wooden-door": "🚪",
    "oak-door": "🚪",
    "spruce-door": "🚪",
    "birch-door": "🚪",
    "wooden-trapdoor": "🔲",
    "oak-trapdoor": "🔲",
    "spruce-trapdoor": "🔲",
    "birch-trapdoor": "🔲",
    "sign": "🪧",
    "oak-sign": "🪧",
    "spruce-sign": "🪧",
    "birch-sign": "🪧",
    "fence": "🚧",
    "oak-fence": "🚧",
    "spruce-fence": "🚧",
    "birch-fence": "🚧",
    "fence-gate": "🚪",
    "oak-fence-gate": "🚪",
    "spruce-fence-gate": "🚪",
    "birch-fence-gate": "🚪",
    "wall": "🧱",
    "cobblestone-wall": "🧱",
    "mossy-cobblestone-wall": "🧱",
    "brick-wall": "🧱",
    "sandstone-wall": "🧱",
    "red-sandstone-wall": "🧱",
    "end-stone-brick-wall": "🧱",
    "iron-bars": "🪟",
    # ─── stairs / slabs ───
    "stairs": "🪜",
    "oak-stairs": "🪜",
    "spruce-stairs": "🪜",
    "birch-stairs": "🪜",
    "brick-stairs": "🪜",
    "stone-stairs": "🪜",
    "cobblestone-stairs": "🪜",
    "stone-brick-stairs": "🪜",
    "sandstone-stairs": "🪜",
    "red-sandstone-stairs": "🪜",
    "quartz-stairs": "🪜",
    "purpur-stairs": "🪜",
    "slab": "▬",
    "oak-slab-block": "▬",
    "spruce-slab-block": "▬",
    "birch-slab-block": "▬",
    "brick-slab": "▬",
    "stone-brick-slab": "▬",
    "sandstone-slab": "▬",
    "quartz-slab": "▬",
    "purpur-slab": "▬",
    "cobblestone-slab-block": "▬",
    "smooth-stone-slab-block": "▬",
    # ─── storage blocks (decompressed from ingots) ───
    "diamond-block": "💎",
    "iron-block": "🔩",
    "gold-block": "🟨",
    "emerald-block": "💚",
    "netherite-block": "⬛",
    "coal-block": "⚫",
    "lapis-block": "🔵",
    "slime-block": "🟢",
    "hay-block": "🌾",
    "snow-block": "❄️",
    "bone-block": "🦴",
    "dried-kelp-block": "🌿",
    "melon-block": "🍉",
    # ─── food items ───
    "bread": "🍞",
    "cookie": "🍪",
    "cake": "🎂",
    "pumpkin-pie": "🥧",
    "golden-apple": "🍎",
    "enchanted-golden-apple": "🍎",
    "mushroom-stew": "🍲",
    "beetroot-soup": "🥣",
    "rabbit-stew": "🍲",
    "suspicious-stew": "🍲",
    # ─── brewing items ───
    "glistering-melon": "✨",
    "glass-bottle": "🍾",
    "tipped-arrow": "🏹",
    "lingering-potion": "⚗️",
    # ─── weapons / tools ───
    "bow": "🏹",
    "crossbow": "🏹",
    "arrow": "🏹",
    "spectral-arrow": "🏹",
    "tnt": "🧨",
    "tnt-block": "🧨",
    # ─── wool colors (grid input) ───
    "white-wool-block": "🧶",
    "red-wool-block": "🟥",
    "blue-wool-block": "🟦",
    "green-wool-block": "🟩",
    "yellow-wool-block": "🟨",
    # ─── misc items ───
    "rabbit-hide": "🐇",
    "vine": "🌿",
    "moss-block": "🌿",
    "crying-obsidian": "🟣",
    "obsidian": "🟪",
    "chiseled-stone-bricks-block": "🧱",
    "wheat-bundle": "🌾",
    "kelp": "🌿",
    "dried-kelp": "🌿",
    "amethyst-shard": "🔮",
    "iron-block-item": "🔩",
    "copper-block": "🟧",
    "smooth-stone": "⬜",
    "crying-obsidian-item": "🟣",
    # ─── empty / null placeholder ───
    "": "",
}

# ─── Helper builders ────────────────────────────────────────────────────────

def R(id_, fa, en, category, grid, output_item, output_count=1, *,
      aliases=None, description="", icon="📦", shapeless=False,
      output_type=None, wiki=WIKI):
    """Build a recipe dict."""
    out = {"item": output_item, "count": output_count}
    if output_type:
        out["type"] = output_type
    return {
        "id": id_,
        "nameFa": fa,
        "nameEn": en,
        "aliases": aliases or [fa, en, id_],
        "category": category,
        "grid": grid,
        "output": out,
        "icon": icon,
        "wikiSlug": wiki,
        "shapeless": shapeless,
        "description": description,
    }


def sword(material_id, output_id, fa, en, icon="🗡️", desc=""):
    return R(output_id, fa, en, COMBAT,
             [[None, material_id, None],
              [None, material_id, None],
              [None, "stick", None]],
             output_id, 1, aliases=[fa, en, output_id], icon=icon,
             description=desc or f"{fa}: ۲ {material_id.replace('-', ' ')} + ۱ چوب. برای مبارزه.")


def pickaxe(material_id, output_id, fa, en, icon="⛏️", desc=""):
    return R(output_id, fa, en, COMBAT,
             [[material_id, material_id, material_id],
              [None, "stick", None],
              [None, "stick", None]],
             output_id, 1, aliases=[fa, en, output_id], icon=icon,
             description=desc or f"{fa}: ۳ {material_id.replace('-', ' ')} + ۲ چوب. برای استخراج.")


def axe(material_id, output_id, fa, en, icon="🪓", desc=""):
    return R(output_id, fa, en, COMBAT,
             [[material_id, material_id, None],
              [material_id, "stick", None],
              [None, "stick", None]],
             output_id, 1, aliases=[fa, en, output_id], icon=icon,
             description=desc or f"{fa}: ۳ {material_id.replace('-', ' ')} + ۲ چوب. برای چیدن چوب.")


def shovel(material_id, output_id, fa, en, icon="🪏", desc=""):
    return R(output_id, fa, en, COMBAT,
             [[None, material_id, None],
              [None, "stick", None],
              [None, "stick", None]],
             output_id, 1, aliases=[fa, en, output_id], icon=icon,
             description=desc or f"{fa}: ۱ {material_id.replace('-', ' ')} + ۲ چوب. برای خاک‌برداری.")


def hoe(material_id, output_id, fa, en, icon="🌾", desc=""):
    return R(output_id, fa, en, COMBAT,
             [[material_id, material_id, None],
              [None, "stick", None],
              [None, "stick", None]],
             output_id, 1, aliases=[fa, en, output_id], icon=icon,
             description=desc or f"{fa}: ۲ {material_id.replace('-', ' ')} + ۲ چوب. برای کشاورزی.")


def helmet(material_id, output_id, fa, en, icon="🪖", desc=""):
    return R(output_id, fa, en, COMBAT,
             [[material_id, material_id, material_id],
              [material_id, None, material_id],
              [None, None, None]],
             output_id, 1, aliases=[fa, en, output_id], icon=icon,
             description=desc or f"{fa}: ۵ {material_id.replace('-', ' ')}. برای محافظت از سر.")


def chestplate(material_id, output_id, fa, en, icon="🦺", desc=""):
    return R(output_id, fa, en, COMBAT,
             [[material_id, None, material_id],
              [material_id, material_id, material_id],
              [material_id, material_id, material_id]],
             output_id, 1, aliases=[fa, en, output_id], icon=icon,
             description=desc or f"{fa}: ۸ {material_id.replace('-', ' ')}. برای محافظت از تن.")


def leggings(material_id, output_id, fa, en, icon="👖", desc=""):
    return R(output_id, fa, en, COMBAT,
             [[material_id, material_id, material_id],
              [material_id, None, material_id],
              [material_id, None, material_id]],
             output_id, 1, aliases=[fa, en, output_id], icon=icon,
             description=desc or f"{fa}: ۷ {material_id.replace('-', ' ')}. برای محافظت از پا.")


def boots(material_id, output_id, fa, en, icon="👢", desc=""):
    return R(output_id, fa, en, COMBAT,
             [[material_id, None, material_id],
              [material_id, None, material_id],
              [None, None, None]],
             output_id, 1, aliases=[fa, en, output_id], icon=icon,
             description=desc or f"{fa}: ۴ {material_id.replace('-', ' ')}. برای محافظت از پا.")


# ─── Build the recipes list ────────────────────────────────────────────────
NEW_RECIPES = []

# ═════════════════════════════════════════════════════════════════════════
# COMBAT — weapons, tools, armor
# ═════════════════════════════════════════════════════════════════════════

# Swords (4 tiers existing + add golden + netherite)
NEW_RECIPES.append(sword("gold-ingot", "golden-sword", "شمشیر طلایی", "Golden Sword",
                         icon="🗡️", desc="شمشیر طلایی: آسیب پایین ولی enchant خوب می‌گیره."))
NEW_RECIPES.append(sword("netherite-ingot", "netherite-sword", "شمشیر نادریتی", "Netherite Sword",
                         icon="🗡️",
                         desc="شمشیر نادریتی: قوی‌ترین سلاح. نیاز به Smithing Table داره (نسخه‌ی الماسی + اینگوت)."))

# Pickaxes (4 tiers existing + add golden + netherite)
NEW_RECIPES.append(pickaxe("gold-ingot", "golden-pickaxe", "کلنگ طلایی", "Golden Pickaxe",
                           icon="⛏️", desc="کلنگ طلایی: سریع ولی دوام پایین."))
NEW_RECIPES.append(pickaxe("netherite-ingot", "netherite-pickaxe", "کلنگ نادریتی", "Netherite Pickaxe",
                           icon="⛏️", desc="کلنگ نادریتی: قوی‌ترین کلنگ. نیاز به Smithing Table."))

# Axes (4 tiers existing + add golden + netherite)
NEW_RECIPES.append(axe("gold-ingot", "golden-axe", "تبر طلایی", "Golden Axe",
                       icon="🪓", desc="تبر طلایی: سریع ولی ضعیف."))
NEW_RECIPES.append(axe("netherite-ingot", "netherite-axe", "تبر نادریتی", "Netherite Axe",
                       icon="🪓", desc="تبر نادریتی: قوی‌ترین تبر. نیاز به Smithing Table."))

# Shovels (existing wooden + iron; add stone, golden, diamond, netherite)
NEW_RECIPES.append(shovel("cobblestone", "stone-shovel", "بیل سنگی", "Stone Shovel",
                           icon="🪏", desc="بیل سنگی: قوی‌تر از چوبی."))
NEW_RECIPES.append(shovel("gold-ingot", "golden-shovel", "بیل طلایی", "Golden Shovel",
                          icon="🪏", desc="بیل طلایی: سریع ولی دوام پایین."))
NEW_RECIPES.append(shovel("diamond", "diamond-shovel", "بیل الماسی", "Diamond Shovel",
                          icon="🪏", desc="بیل الماسی: قوی و دوام‌دار."))
NEW_RECIPES.append(shovel("netherite-ingot", "netherite-shovel", "بیل نادریتی", "Netherite Shovel",
                          icon="🪏", desc="بیل نادریتی: قوی‌ترین بیل. نیاز به Smithing Table."))

# Hoes (all 6)
NEW_RECIPES.append(hoe("oak-planks", "wooden-hoe", "آ胆囊 چوبی", "Wooden Hoe",
                       icon="🌾", desc="آ胆囊 چوبی: برای آماده‌کردن زمین کشاورزی."))
NEW_RECIPES.append(hoe("cobblestone", "stone-hoe", "آ胆囊 سنگی", "Stone Hoe",
                       icon="🌾", desc="آ胆囊 سنگی: قوی‌تر از چوبی."))
NEW_RECIPES.append(hoe("iron-ingot", "iron-hoe", "آ胆囊 آهنی", "Iron Hoe",
                       icon="🌾", desc="آ胆囊 آهنی: استاندارد."))
NEW_RECIPES.append(hoe("gold-ingot", "golden-hoe", "آ胆囊 طلایی", "Golden Hoe",
                       icon="🌾", desc="آ胆囊 طلایی: ضعیف ولی enchant خوب."))
NEW_RECIPES.append(hoe("diamond", "diamond-hoe", "آ胆囊 الماسی", "Diamond Hoe",
                       icon="🌾", desc="آ胆囊 الماسی: دوام عالی."))
NEW_RECIPES.append(hoe("netherite-ingot", "netherite-hoe", "آ胆囊 نادریتی", "Netherite Hoe",
                       icon="🌾", desc="آ胆囊 نادریتی: قوی‌ترین. نیاز به Smithing Table."))

# Ranged
NEW_RECIPES.append(R("crossbow", "کمان-coltوی", "Crossbow",
                     COMBAT,
                     [["stick", None, "string"],
                      ["string", "iron-ingot", "string"],
                      ["stick", None, "string"]],
                     "crossbow", 1,
                     aliases=["کمان coltوی", "crossbow", "کراس‌بو"],
                     icon="🏹",
                     description="کمان coltوی: آسیب بالاتر از کمان معمولی ولی شارژ طولانی‌تر."))

NEW_RECIPES.append(R("spectral-arrow", "تیر نورانی", "Spectral Arrow",
                     COMBAT,
                     [[None, "glowstone-dust", None],
                      [None, "arrow", None],
                      [None, None, None]],
                     "spectral-arrow", 8,
                     aliases=["تیر نورانی", "spectral arrow"],
                     icon="🏹",
                     shapeless=True,
                     description="تیر نورانی (Java فقط): هدف‌ها glow می‌کنن. ۱ glowstone dust + ۱ تیر → ۸ تیر."))

# Defense
NEW_RECIPES.append(R("flint-and-steel", "ولغمه و فولاد", "Flint and Steel",
                     COMBAT,
                     [[None, "iron-ingot", None],
                      [None, "flint", None],
                      [None, None, None]],
                     "flint-and-steel", 1,
                     aliases=["ولغمه و فولاد", "flint and steel", "فولاد و چخماق"],
                     icon="🔥",
                     description="ولغمه و فولاد: برای روشن‌کردن آتش و فعال‌کردن TNT."))

NEW_RECIPES.append(R("shears", "قیچی", "Shears",
                     COMBAT,
                     [[None, "iron-ingot", "iron-ingot"],
                      ["iron-ingot", None, None],
                      [None, None, None]],
                     "shears", 1,
                     aliases=["قیچی", "shears"],
                     icon="✂️",
                     description="قیچی: برای چیدن پشم گوسفند، برگ، تار عنکبوت و قارچ."))

NEW_RECIPES.append(R("fishing-rod", "قلاب ماهی‌گیری", "Fishing Rod",
                     COMBAT,
                     [[None, None, "stick"],
                      [None, "stick", None],
                      ["stick", None, "string"]],
                     "fishing-rod", 1,
                     aliases=["قلاب ماهی‌گیری", "fishing rod", "fishingrod"],
                     icon="🎣",
                     description="قلاب ماهی‌گیری: برای ماهی‌گیری و گیرانداختن ماب‌ها."))

# Armor — Leather set (4)
NEW_RECIPES.append(helmet("leather", "leather-cap", "کلاه چرمی", "Leather Cap",
                          icon="🪖", desc="کلاه چرمی: ضعیف‌ترین زره ولی قابل رنگ‌آمیزی."))
NEW_RECIPES.append(chestplate("leather", "leather-tunic", "زره تن چرمی", "Leather Tunic",
                              icon="🦺", desc="زره تن چرمی: ضعیف ولی قابل رنگ."))
NEW_RECIPES.append(leggings("leather", "leather-pants", "شلوار چرمی", "Leather Pants",
                            icon="👖", desc="شلوار چرمی: قابل رنگ‌آمیزی."))
NEW_RECIPES.append(boots("leather", "leather-boots", "چکمه چرمی", "Leather Boots",
                         icon="👢", desc="چکمه چرمی: قابل رنگ‌آمیزی."))

# Armor — Golden set (4)
NEW_RECIPES.append(helmet("gold-ingot", "golden-helmet", "کلاه طلایی", "Golden Helmet",
                          icon="🪖", desc="کلاه طلایی: ضعیف ولی enchant خوب."))
NEW_RECIPES.append(chestplate("gold-ingot", "golden-chestplate", "زره تن طلایی", "Golden Chestplate",
                              icon="🦺", desc="زره تن طلایی: ضعیف ولی enchant خوب."))
NEW_RECIPES.append(leggings("gold-ingot", "golden-leggings", "شلوار طلایی", "Golden Leggings",
                            icon="👖", desc="شلوار طلایی: ضعیف."))
NEW_RECIPES.append(boots("gold-ingot", "golden-boots", "چکمه طلایی", "Golden Boots",
                         icon="👢", desc="چکمه طلایی: ضعیف."))

# Armor — Diamond set (4)
NEW_RECIPES.append(helmet("diamond", "diamond-helmet", "کلاه الماسی", "Diamond Helmet",
                          icon="🪖", desc="کلاه الماسی: قوی و دوام‌دار."))
NEW_RECIPES.append(chestplate("diamond", "diamond-chestplate", "زره تن الماسی", "Diamond Chestplate",
                              icon="🦺", desc="زره تن الماسی: بهترین زره."))
NEW_RECIPES.append(leggings("diamond", "diamond-leggings", "شلوار الماسی", "Diamond Leggings",
                            icon="👖", desc="شلوار الماسی: قوی."))
NEW_RECIPES.append(boots("diamond", "diamond-boots", "چکمه الماسی", "Diamond Boots",
                         icon="👢", desc="چکمه الماسی: دوام عالی."))

# Armor — Netherite set (4 — requires Smithing Table)
NEW_RECIPES.append(helmet("netherite-ingot", "netherite-helmet", "کلاه نادریتی", "Netherite Helmet",
                          icon="🪖", desc="کلاه نادریتی: نیاز به Smithing Table (الماسی + اینگوت)."))
NEW_RECIPES.append(chestplate("netherite-ingot", "netherite-chestplate", "زره تن نادریتی", "Netherite Chestplate",
                              icon="🦺", desc="زره تن نادریتی: قوی‌ترین زره. Smithing Table."))
NEW_RECIPES.append(leggings("netherite-ingot", "netherite-leggings", "شلوار نادریتی", "Netherite Leggings",
                            icon="👖", desc="شلوار نادریتی: قوی‌ترین. Smithing Table."))
NEW_RECIPES.append(boots("netherite-ingot", "netherite-boots", "چکمه نادریتی", "Netherite Boots",
                         icon="👢", desc="چکمه نادریتی: قوی‌ترین. Smithing Table."))

# Turtle Shell Helmet (special)
NEW_RECIPES.append(R("turtle-helmet", "کلاه لاکشتی", "Turtle Shell",
                     COMBAT,
                     [[None, None, None],
                      ["scute", "scute", "scute"],
                      ["scute", None, "scute"]],
                     "turtle-helmet", 1,
                     aliases=["کلاه لاکشتی", "turtle shell", "turtle helmet"],
                     icon="🐢",
                     description="کلاه لاکشتی: محافظت + افزایش تنفس زیر آب. ۵ scute."))


# ═════════════════════════════════════════════════════════════════════════
# TOOLS — utility items
# ═════════════════════════════════════════════════════════════════════════

NEW_RECIPES.append(R("paper", "کاغذ", "Paper", TOOLS,
                     [[None, None, None],
                      ["sugar-cane", "sugar-cane", "sugar-cane"],
                      [None, None, None]],
                     "paper", 3,
                     aliases=["کاغذ", "paper"],
                     icon="📄",
                     description="کاغذ: ۳ نیشکر → ۳ کاغذ. پایه‌ی ساخت کتاب و نقشه."))

NEW_RECIPES.append(R("book", "کتاب", "Book", TOOLS,
                     [["paper", "paper", None],
                      ["paper", "leather", None],
                      ["paper", "paper", None]],
                     "book", 1,
                     aliases=["کتاب", "book"],
                     icon="📘",
                     description="کتاب: ۳ کاغذ + ۱ چرم. برای bookshelf و enchanting."))

NEW_RECIPES.append(R("book-and-quill", "کتاب و قلم", "Book and Quill", TOOLS,
                     [[None, None, None],
                      [None, "book", None],
                      ["ink-sac", "feather", None]],
                     "book-and-quill", 1,
                     aliases=["کتاب و قلم", "book and quill"],
                     icon="🖋️",
                     shapeless=True,
                     description="کتاب و قلم: ۱ کتاب + ۱ پر + ۱ ink-sac. برای نوشتن."))

NEW_RECIPES.append(R("lectern", "منبر مطالعه", "Lectern", TOOLS,
                     [["oak-slab", "oak-slab", None],
                      ["oak-slab", "oak-slab", None],
                      [None, "bookshelf", None]],
                     "lectern", 1,
                     aliases=["منبر مطالعه", "lectern"],
                     icon="📚",
                     output_type="block",
                     description="منبر: ۴ تخته‌ی نازک + ۱ کتاب‌خانه. برای خواندن کتاب."))

NEW_RECIPES.append(R("compass", "قطب‌نما", "Compass", TOOLS,
                     [[None, "iron-ingot", None],
                      ["iron-ingot", None, "iron-ingot"],
                      [None, "iron-ingot", None]],
                     "compass", 1,
                     aliases=["قطب‌نما", "compass"],
                     icon="🧭",
                     shapeless=False,
                     description="قطب‌نما: ۴ شمش آهن. به نقطه‌ی تولد اشاره می‌کنه."))

NEW_RECIPES.append(R("clock", "ساعت", "Clock", TOOLS,
                     [[None, "gold-ingot", None],
                      ["gold-ingot", "redstone", "gold-ingot"],
                      [None, "gold-ingot", None]],
                     "clock", 1,
                     aliases=["ساعت", "clock"],
                     icon="🕐",
                     description="ساعت: ۴ شمش طلا + ۱ redstone. زمان روز/شب رو نشون می‌ده."))

NEW_RECIPES.append(R("empty-map", "نقشه‌ی خالی", "Empty Map", TOOLS,
                     [[None, None, None],
                      ["paper", "compass", "paper"],
                      [None, None, None]],
                     "map", 1,
                     aliases=["نقشه‌ی خالی", "empty map", "map", "نقشه"],
                     icon="🗺️",
                     description="نقشه‌ی خالی: ۸ کاغذ + ۱ قطب‌نما (وسط).")

)

NEW_RECIPES.append(R("firework-rocket", "موشک آتش‌بازی", "Firework Rocket", TOOLS,
                     [[None, None, None],
                      [None, None, None],
                      ["paper", "gunpowder", None]],
                     "firework-rocket", 3,
                     aliases=["موشک آتش‌بازی", "firework rocket"],
                     icon="🎆",
                     shapeless=True,
                     description="موشک آتش‌بازی: ۱ کاغذ + ۱ باروت → ۳ موشک. افزودن firework-star برای شکل."))

NEW_RECIPES.append(R("firework-star", "ستاره‌ی آتش‌بازی", "Firework Star", TOOLS,
                     [[None, None, None],
                      [None, None, None],
                      ["gunpowder", "dye", None]],
                     "firework-star", 1,
                     aliases=["ستاره‌ی آتش‌بازی", "firework star"],
                     icon="✨",
                     shapeless=True,
                     description="ستاره‌ی آتش‌بازی: ۱ باروت + ۱ رنگ → ۱ ستاره. رنگ انفجار رو تعیین می‌کنه."))

NEW_RECIPES.append(R("cartography-table", "میز نقشه‌کشی", "Cartography Table", TOOLS,
                     [["paper", "paper", None],
                      ["oak-planks", "oak-planks", None],
                      ["oak-planks", "oak-planks", None]],
                     "cartography-table", 1,
                     aliases=["میز نقشه‌کشی", "cartography table"],
                     icon="🗺️",
                     output_type="block",
                     description="میز نقشه‌کشی: ۲ کاغذ + ۴ تخته. برای بزرگ‌کردن و کپی نقشه."))

NEW_RECIPES.append(R("fletching-table", "میز تیرسازی", "Fletching Table", TOOLS,
                     [["flint", "flint", None],
                      ["oak-planks", "oak-planks", None],
                      ["oak-planks", "oak-planks", None]],
                     "fletching-table", 1,
                     aliases=["میز تیرسازی", "fletching table"],
                     icon="🏹",
                     output_type="block",
                     description="میز تیرسازی: ۲ تیشه + ۴ تخته. Village fletcher job block."))

NEW_RECIPES.append(R("smithing-table", "میز آهنگری", "Smithing Table", TOOLS,
                     [["iron-ingot", "iron-ingot", None],
                      ["oak-planks", "oak-planks", None],
                      ["oak-planks", "oak-planks", None]],
                     "smithing-table", 1,
                     aliases=["میز آهنگری", "smithing table"],
                     icon="🔨",
                     output_type="block",
                     description="میز آهنگری: ۲ شمش آهن + ۴ تخته. برای ارتقای نادریتی."))

NEW_RECIPES.append(R("loom", "مکنده", "Loom", TOOLS,
                     [[None, "string", None],
                      ["string", "oak-planks", None],
                      ["oak-planks", "oak-planks", None]],
                     "loom", 1,
                     aliases=["مکنده", "loom"],
                     icon="🧵",
                     output_type="block",
                     description="مکنده: ۲ نخ + ۲ تخته. برای ساخت طرح‌های banner."))

NEW_RECIPES.append(R("grindstone", "سنگ آسیاب", "Grindstone", TOOLS,
                     [["oak-planks", "stick", "oak-planks"],
                      [None, "smooth-stone-slab", None],
                      [None, None, None]],
                     "grindstone", 1,
                     aliases=["سنگ آسیاب", "grindstone"],
                     icon="🪨",
                     output_type="block",
                     description="سنگ آسیاب: ۲ تخته + ۱ چوب + ۱ تخته‌ی سنگی. برای تعمیر و پاک‌کردن enchant."))

NEW_RECIPES.append(R("stonecutter", "سنگ‌بُر", "Stonecutter", TOOLS,
                     [[None, "iron-ingot", None],
                      [None, "stone", None],
                      [None, "stone", None]],
                     "stonecutter", 1,
                     aliases=["سنگ‌بُر", "stonecutter"],
                     icon="🪚",
                     output_type="block",
                     description="سنگ‌بُر: ۱ شمش آهن + ۳ سنگ. برای ساخت stairs/slabs با بازدهی بیشتر."))

NEW_RECIPES.append(R("lead", "طناب", "Lead", TOOLS,
                     [[None, None, None],
                      ["string", "slimeball", "string"],
                      ["string", None, None]],
                     "lead", 2,
                     aliases=["طناب", "lead"],
                     icon="🪢",
                     shapeless=True,
                     description="طناب: ۴ نخ + ۱ slimeball → ۲ طناب. برای قفل‌کردن ماب‌ها."))

NEW_RECIPES.append(R("spyglass", "دوربین", "Spyglass", TOOLS,
                     [[None, "amethyst-shard", None],
                      [None, "copper-ingot", None],
                      [None, "copper-ingot", None]],
                     "spyglass", 1,
                     aliases=["دوربین", "spyglass"],
                     icon="🔭",
                     description="دوربین: ۱ amethyst + ۲ مس. برای زوم‌کردن."))

NEW_RECIPES.append(R("leather-from-rabbit", "چرم از پوست خرگوش", "Leather (from rabbit hide)", TOOLS,
                     [[None, None, None],
                      ["rabbit-hide", "rabbit-hide", None],
                      ["rabbit-hide", "rabbit-hide", None]],
                     "leather", 1,
                     aliases=["چرم از پوست خرگوش", "leather from rabbit"],
                     icon="🟫",
                     shapeless=True,
                     description="چرم: ۴ پوست خرگوش → ۱ چرم. جایگزین چرم از گاو."))

NEW_RECIPES.append(R("bowl", "کاسه", "Bowl", TOOLS,
                     [[None, None, None],
                      ["oak-planks", None, "oak-planks"],
                      ["oak-planks", "oak-planks", "oak-planks"]],
                     "bowl", 4,
                     aliases=["کاسه", "bowl"],
                     icon="🥣",
                     description="کاسه: ۳ تخته → ۴ کاسه. برای خورش."))

NEW_RECIPES.append(R("armor-stand", "استند زره", "Armor Stand", TOOLS,
                     [["stick", None, "stick"],
                      ["stick", "stick", "stick"],
                      ["stick", "smooth-stone-slab", "stick"]],
                     "armor-stand", 1,
                     aliases=["استند زره", "armor stand"],
                     icon="🧍",
                     output_type="block",
                     description="استند زره: ۶ چوب + ۱ تخته‌ی سنگی. برای نمایش زره."))

NEW_RECIPES.append(R("dried-kelp-block", "بلوک جلبک خشک", "Dried Kelp Block", TOOLS,
                     [["dried-kelp", "dried-kelp", "dried-kelp"],
                      ["dried-kelp", "dried-kelp", "dried-kelp"],
                      ["dried-kelp", "dried-kelp", "dried-kelp"]],
                     "dried-kelp-block", 1,
                     aliases=["بلوک جلبک خشک", "dried kelp block"],
                     icon="🌿",
                     output_type="block",
                     description="بلوک جلبک خشک: ۹ جلبک خشک → ۱ بلوک. سوخت کارآمد."))


# ═════════════════════════════════════════════════════════════════════════
# BUILDING — planks, stairs, slabs, fences, walls, doors, etc.
# ═════════════════════════════════════════════════════════════════════════

# ─── Per-wood recipes (oak/spruce/birch) ─────────────────────────────────
WOOD_TYPES = [
    ("oak", "بلوط", "Oak"),
    ("spruce", "نوئل", "Spruce"),
    ("birch", "توس", "Birch"),
]

# Extra wood types — only stairs/slab/fence/door/trapdoor (5 recipes each, +15 = 300+)
EXTRA_WOOD_TYPES = [
    ("jungle", "جنگل", "Jungle"),
    ("acacia", "اقاقیا", "Acacia"),
    ("dark-oak", "بلوط تیره", "Dark Oak"),
]

for wood_id, wood_fa, wood_en in WOOD_TYPES:
    planks = f"{wood_id}-planks"
    stairs = f"{wood_id}-stairs"
    slab = f"{wood_id}-slab"
    fence = f"{wood_id}-fence"
    fence_gate = f"{wood_id}-fence-gate"
    door = f"{wood_id}-door"
    trapdoor = f"{wood_id}-trapdoor"
    pressure_plate = f"{wood_id}-pressure-plate"
    button = f"{wood_id}-button"
    sign = f"{wood_id}-sign"

    # Stairs: 6 planks → 4 stairs
    NEW_RECIPES.append(R(stairs, f"پله‌ی {wood_fa}", f"{wood_en} Stairs", BUILDING,
                         [[planks, None, None],
                          [planks, planks, None],
                          [planks, planks, planks]],
                         stairs, 4, output_type="block",
                         aliases=[f"پله‌ی {wood_fa}", f"{wood_en} Stairs"],
                         icon="🪜",
                         description=f"پله‌ی {wood_fa}: ۶ تخته → ۴ پله."))

    # Slab: 3 planks in row → 6 slabs
    NEW_RECIPES.append(R(slab, f"تخته‌ی نازک {wood_fa}", f"{wood_en} Slab", BUILDING,
                         [[None, None, None],
                          [None, None, None],
                          [planks, planks, planks]],
                         slab, 6, output_type="block",
                         aliases=[f"تخته‌ی نازک {wood_fa}", f"{wood_en} Slab"],
                         icon="▬",
                         description=f"تخته‌ی نازک {wood_fa}: ۳ تخته → ۶ تخته‌ی نازک."))

    # Fence: 4 planks + 2 sticks → 3 fences
    NEW_RECIPES.append(R(fence, f"حصار {wood_fa}", f"{wood_en} Fence", BUILDING,
                         [[planks, "stick", planks],
                          [planks, "stick", planks],
                          [None, None, None]],
                         fence, 3, output_type="block",
                         aliases=[f"حصار {wood_fa}", f"{wood_en} Fence"],
                         icon="🚧",
                         description=f"حصار {wood_fa}: ۴ تخته + ۲ چوب → ۳ حصار."))

    # Fence Gate: 4 planks + 2 sticks → 1 gate (pattern: stick,planks,planks,planks,planks,stick)
    NEW_RECIPES.append(R(fence_gate, f"درب حصار {wood_fa}", f"{wood_en} Fence Gate", BUILDING,
                         [["stick", planks, planks],
                          ["stick", planks, planks],
                          [None, None, None]],
                         fence_gate, 1, output_type="block",
                         aliases=[f"درب حصار {wood_fa}", f"{wood_en} Fence Gate"],
                         icon="🚪",
                         description=f"درب حصار {wood_fa}: ۲ چوب + ۴ تخته → ۱ درب."))

    # Door: 6 planks → 3 doors
    NEW_RECIPES.append(R(door, f"درب {wood_fa}", f"{wood_en} Door", BUILDING,
                         [[planks, planks, None],
                          [planks, planks, None],
                          [planks, planks, None]],
                         door, 3, output_type="block",
                         aliases=[f"درب {wood_fa}", f"{wood_en} Door"],
                         icon="🚪",
                         description=f"درب {wood_fa}: ۶ تخته → ۳ درب."))

    # Trapdoor: 6 planks → 2 trapdoors
    NEW_RECIPES.append(R(trapdoor, f"درب تله {wood_fa}", f"{wood_en} Trapdoor", BUILDING,
                         [[planks, planks, planks],
                          [planks, planks, planks],
                          [None, None, None]],
                         trapdoor, 2, output_type="block",
                         aliases=[f"درب تله {wood_fa}", f"{wood_en} Trapdoor"],
                         icon="🔲",
                         description=f"درب تله {wood_fa}: ۶ تخته → ۲ درب تله."))

    # Pressure Plate: 2 planks in row → 1
    NEW_RECIPES.append(R(pressure_plate, f"صفحه‌ی فشار {wood_fa}", f"{wood_en} Pressure Plate", BUILDING,
                         [[None, None, None],
                          [None, None, None],
                          [planks, planks, None]],
                         pressure_plate, 1, output_type="block",
                         aliases=[f"صفحه‌ی فشار {wood_fa}", f"{wood_en} Pressure Plate"],
                         icon="🔛",
                         description=f"صفحه‌ی فشار {wood_fa}: ۲ تخته → ۱."))

    # Button: 1 plank → 1
    NEW_RECIPES.append(R(button, f"دکمه‌ی {wood_fa}", f"{wood_en} Button", BUILDING,
                         [[None, None, None],
                          [None, None, None],
                          [None, planks, None]],
                         button, 1, output_type="block",
                         aliases=[f"دکمه‌ی {wood_fa}", f"{wood_en} Button"],
                         icon="🔘",
                         shapeless=True,
                         description=f"دکمه‌ی {wood_fa}: ۱ تخته → ۱ دکمه."))

    # Sign: 6 planks + 1 stick → 3 signs
    NEW_RECIPES.append(R(sign, f"تابلو {wood_fa}", f"{wood_en} Sign", BUILDING,
                         [[planks, planks, planks],
                          [planks, planks, planks],
                          [None, "stick", None]],
                         sign, 3, output_type="block",
                         aliases=[f"تابلو {wood_fa}", f"{wood_en} Sign"],
                         icon="🪧",
                         description=f"تابلو {wood_fa}: ۶ تخته + ۱ چوب → ۳ تابلو."))

# Spruce + Birch boats (oak boat already in existing recipes)
NEW_RECIPES.append(R("spruce-boat", "قایق نوئلی", "Spruce Boat", BUILDING,
                     [["spruce-planks", None, "spruce-planks"],
                      ["spruce-planks", "spruce-planks", "spruce-planks"],
                      [None, None, None]],
                     "spruce-boat", 1,
                     aliases=["قایق نوئلی", "spruce boat"],
                     icon="🚣",
                     description="قایق نوئلی: ۵ تخته‌ی نوئل."))
NEW_RECIPES.append(R("birch-boat", "قایق تاسی", "Birch Boat", BUILDING,
                     [["birch-planks", None, "birch-planks"],
                      ["birch-planks", "birch-planks", "birch-planks"],
                      [None, None, None]],
                     "birch-boat", 1,
                     aliases=["قایق تاسی", "birch boat"],
                     icon="🚣",
                     description="قایق تاسی: ۵ تخته‌ی توس."))


# ─── Extra wood types — only stairs/slab/fence/door/trapdoor (5 recipes × 3 = 15 more) ──
for wood_id, wood_fa, wood_en in EXTRA_WOOD_TYPES:
    planks = f"{wood_id}-planks"
    stairs = f"{wood_id}-stairs"
    slab = f"{wood_id}-slab"
    fence = f"{wood_id}-fence"
    door = f"{wood_id}-door"
    trapdoor = f"{wood_id}-trapdoor"

    NEW_RECIPES.append(R(stairs, f"پله‌ی {wood_fa}", f"{wood_en} Stairs", BUILDING,
                         [[planks, None, None],
                          [planks, planks, None],
                          [planks, planks, planks]],
                         stairs, 4, output_type="block",
                         aliases=[f"پله‌ی {wood_fa}", f"{wood_en} Stairs"],
                         icon="🪜",
                         description=f"پله‌ی {wood_fa}: ۶ تخته → ۴ پله."))

    NEW_RECIPES.append(R(slab, f"تخته‌ی نازک {wood_fa}", f"{wood_en} Slab", BUILDING,
                         [[None, None, None],
                          [None, None, None],
                          [planks, planks, planks]],
                         slab, 6, output_type="block",
                         aliases=[f"تخته‌ی نازک {wood_fa}", f"{wood_en} Slab"],
                         icon="▬",
                         description=f"تخته‌ی نازک {wood_fa}: ۳ تخته → ۶ تخته‌ی نازک."))

    NEW_RECIPES.append(R(fence, f"حصار {wood_fa}", f"{wood_en} Fence", BUILDING,
                         [[planks, "stick", planks],
                          [planks, "stick", planks],
                          [None, None, None]],
                         fence, 3, output_type="block",
                         aliases=[f"حصار {wood_fa}", f"{wood_en} Fence"],
                         icon="🚧",
                         description=f"حصار {wood_fa}: ۴ تخته + ۲ چوب → ۳ حصار."))

    NEW_RECIPES.append(R(door, f"درب {wood_fa}", f"{wood_en} Door", BUILDING,
                         [[planks, planks, None],
                          [planks, planks, None],
                          [planks, planks, None]],
                         door, 3, output_type="block",
                         aliases=[f"درب {wood_fa}", f"{wood_en} Door"],
                         icon="🚪",
                         description=f"درب {wood_fa}: ۶ تخته → ۳ درب."))

    NEW_RECIPES.append(R(trapdoor, f"درب تله {wood_fa}", f"{wood_en} Trapdoor", BUILDING,
                         [[planks, planks, planks],
                          [planks, planks, planks],
                          [None, None, None]],
                         trapdoor, 2, output_type="block",
                         aliases=[f"درب تله {wood_fa}", f"{wood_en} Trapdoor"],
                         icon="🔲",
                         description=f"درب تله {wood_fa}: ۶ تخته → ۲ درب تله."))


# ─── Bricks block family ────────────────────────────────────────────────
NEW_RECIPES.append(R("bricks-block", "بلوک آجر", "Bricks", BUILDING,
                     [["brick-item", "brick-item", None],
                      ["brick-item", "brick-item", None],
                      [None, None, None]],
                     "bricks", 1, output_type="block",
                     aliases=["بلوک آجر", "bricks", "آجر"],
                     icon="🧱",
                     description="بلوک آجر: ۴ آجر (brick item) → ۱ بلوک."))

NEW_RECIPES.append(R("brick-stairs", "پله‌ی آجر", "Brick Stairs", BUILDING,
                     [["bricks", None, None],
                      ["bricks", "bricks", None],
                      ["bricks", "bricks", "bricks"]],
                     "brick-stairs", 4, output_type="block",
                     aliases=["پله‌ی آجر", "brick stairs"],
                     icon="🪜",
                     description="پله‌ی آجر: ۶ بلوک آجر → ۴ پله."))

NEW_RECIPES.append(R("brick-slab", "تخته‌ی نازک آجر", "Brick Slab", BUILDING,
                     [[None, None, None],
                      [None, None, None],
                      ["bricks", "bricks", "bricks"]],
                     "brick-slab", 6, output_type="block",
                     aliases=["تخته‌ی نازک آجر", "brick slab"],
                     icon="▬",
                     description="تخته‌ی نازک آجر: ۳ بلوک → ۶ تخته‌ی نازک."))

NEW_RECIPES.append(R("brick-wall", "دیوار آجر", "Brick Wall", BUILDING,
                     [["bricks", "bricks", "bricks"],
                      ["bricks", "bricks", "bricks"],
                      [None, None, None]],
                     "brick-wall", 6, output_type="block",
                     aliases=["دیوار آجر", "brick wall"],
                     icon="🧱",
                     description="دیوار آجر: ۶ بلوک → ۶ دیوار."))

# ─── Stone brick family ────────────────────────────────────────────────
NEW_RECIPES.append(R("stone-bricks-block", "بلوک آجر سنگی", "Stone Bricks", BUILDING,
                     [["stone", "stone", None],
                      ["stone", "stone", None],
                      [None, None, None]],
                     "stone-bricks", 4, output_type="block",
                     aliases=["بلوک آجر سنگی", "stone bricks"],
                     icon="🧱",
                     description="بلوک آجر سنگی: ۴ سنگ → ۴ بلوک."))

NEW_RECIPES.append(R("stone-brick-stairs", "پله‌ی آجر سنگی", "Stone Brick Stairs", BUILDING,
                     [["stone-bricks", None, None],
                      ["stone-bricks", "stone-bricks", None],
                      ["stone-bricks", "stone-bricks", "stone-bricks"]],
                     "stone-brick-stairs", 4, output_type="block",
                     aliases=["پله‌ی آجر سنگی", "stone brick stairs"],
                     icon="🪜",
                     description="پله‌ی آجر سنگی: ۶ بلوک → ۴ پله."))

NEW_RECIPES.append(R("stone-brick-slab", "تخته‌ی نازک آجر سنگی", "Stone Brick Slab", BUILDING,
                     [[None, None, None],
                      [None, None, None],
                      ["stone-bricks", "stone-bricks", "stone-bricks"]],
                     "stone-brick-slab", 6, output_type="block",
                     aliases=["تخته‌ی نازک آجر سنگی", "stone brick slab"],
                     icon="▬",
                     description="تخته‌ی نازک آجر سنگی: ۳ بلوک → ۶."))

NEW_RECIPES.append(R("stone-brick-wall", "دیوار آجر سنگی", "Stone Brick Wall", BUILDING,
                     [["stone-bricks", "stone-bricks", "stone-bricks"],
                      ["stone-bricks", "stone-bricks", "stone-bricks"],
                      [None, None, None]],
                     "stone-brick-wall", 6, output_type="block",
                     aliases=["دیوار آجر سنگی", "stone brick wall"],
                     icon="🧱",
                     description="دیوار آجر سنگی: ۶ بلوک → ۶ دیوار."))

NEW_RECIPES.append(R("mossy-stone-bricks", "آجر سنگی خزه‌دار", "Mossy Stone Bricks", BUILDING,
                     [[None, None, None],
                      [None, None, None],
                      ["stone-bricks", "vine", None]],
                     "mossy-stone-bricks", 1, output_type="block",
                     aliases=["آجر سنگی خزه‌دار", "mossy stone bricks"],
                     icon="🧱",
                     shapeless=True,
                     description="آجر سنگی خزه‌دار: ۱ بلوک + ۱ پیچک. یا ۱ بلوک + ۱ moss-block."))

NEW_RECIPES.append(R("chiseled-stone-bricks", "آجر سنگی کنده‌کاری شده", "Chiseled Stone Bricks", BUILDING,
                     [[None, None, None],
                      ["stone-brick-slab", "stone-brick-slab", None],
                      [None, None, None]],
                     "chiseled-stone-bricks", 1, output_type="block",
                     aliases=["آجر سنگی کنده‌کاری شده", "chiseled stone bricks"],
                     icon="🧱",
                     description="آجر سنگی کنده‌کاری شده: ۲ تخته‌ی نازک آجر سنگی."))

# ─── Sandstone family ────────────────────────────────────────────────
NEW_RECIPES.append(R("sandstone", "سنگ‌ماسه", "Sandstone", BUILDING,
                     [[None, None, None],
                      ["sand", "sand", None],
                      ["sand", "sand", None]],
                     "sandstone", 4, output_type="block",
                     aliases=["سنگ‌ماسه", "sandstone"],
                     icon="🟫",
                     description="سنگ‌ماسه: ۴ شن → ۴ بلوک."))

NEW_RECIPES.append(R("sandstone-stairs", "پله‌ی سنگ‌ماسه", "Sandstone Stairs", BUILDING,
                     [["sandstone", None, None],
                      ["sandstone", "sandstone", None],
                      ["sandstone", "sandstone", "sandstone"]],
                     "sandstone-stairs", 4, output_type="block",
                     aliases=["پله‌ی سنگ‌ماسه", "sandstone stairs"],
                     icon="🪜",
                     description="پله‌ی سنگ‌ماسه: ۶ بلوک → ۴ پله."))

NEW_RECIPES.append(R("sandstone-slab", "تخته‌ی نازک سنگ‌ماسه", "Sandstone Slab", BUILDING,
                     [[None, None, None],
                      [None, None, None],
                      ["sandstone", "sandstone", "sandstone"]],
                     "sandstone-slab", 6, output_type="block",
                     aliases=["تخته‌ی نازک سنگ‌ماسه", "sandstone slab"],
                     icon="▬",
                     description="تخته‌ی نازک سنگ‌ماسه: ۳ بلوک → ۶."))

NEW_RECIPES.append(R("cut-sandstone", "سنگ‌ماسه برش‌خورده", "Cut Sandstone", BUILDING,
                     [[None, None, None],
                      ["sandstone", "sandstone", None],
                      ["sandstone", "sandstone", None]],
                     "cut-sandstone", 4, output_type="block",
                     aliases=["سنگ‌ماسه برش‌خورده", "cut sandstone"],
                     icon="🟫",
                     description="سنگ‌ماسه برش‌خورده: ۴ بلوک → ۴ برش‌خورده."))

NEW_RECIPES.append(R("chiseled-sandstone", "سنگ‌ماسه کنده‌کاری", "Chiseled Sandstone", BUILDING,
                     [[None, None, None],
                      ["cut-sandstone", None, None],
                      ["cut-sandstone", None, None]],
                     "chiseled-sandstone", 1, output_type="block",
                     aliases=["سنگ‌ماسه کنده‌کاری", "chiseled sandstone"],
                     icon="🟫",
                     description="سنگ‌ماسه کنده‌کاری: ۲ cut-sandstone روی هم."))

NEW_RECIPES.append(R("sandstone-wall", "دیوار سنگ‌ماسه", "Sandstone Wall", BUILDING,
                     [["sandstone", "sandstone", "sandstone"],
                      ["sandstone", "sandstone", "sandstone"],
                      [None, None, None]],
                     "sandstone-wall", 6, output_type="block",
                     aliases=["دیوار سنگ‌ماسه", "sandstone wall"],
                     icon="🧱",
                     description="دیوار سنگ‌ماسه: ۶ بلوک → ۶ دیوار."))

NEW_RECIPES.append(R("red-sandstone", "سنگ‌ماسه‌ی قرمز", "Red Sandstone", BUILDING,
                     [[None, None, None],
                      ["red-sand", "red-sand", None],
                      ["red-sand", "red-sand", None]],
                     "red-sandstone", 4, output_type="block",
                     aliases=["سنگ‌ماسه‌ی قرمز", "red sandstone"],
                     icon="🟧",
                     description="سنگ‌ماسه‌ی قرمز: ۴ شن قرمز → ۴ بلوک."))

# ─── Quartz family ────────────────────────────────────────────────────
NEW_RECIPES.append(R("quartz-block", "بلوک کوارتز", "Block of Quartz", BUILDING,
                     [[None, None, None],
                      ["nether-quartz", "nether-quartz", None],
                      ["nether-quartz", "nether-quartz", None]],
                     "quartz-block", 4, output_type="block",
                     aliases=["بلوک کوارتز", "quartz block", "block of quartz"],
                     icon="⬜",
                     description="بلوک کوارتز: ۴ کوارتز ندر → ۴ بلوک."))

NEW_RECIPES.append(R("quartz-stairs", "پله‌ی کوارتز", "Quartz Stairs", BUILDING,
                     [["quartz-block", None, None],
                      ["quartz-block", "quartz-block", None],
                      ["quartz-block", "quartz-block", "quartz-block"]],
                     "quartz-stairs", 4, output_type="block",
                     aliases=["پله‌ی کوارتز", "quartz stairs"],
                     icon="🪜",
                     description="پله‌ی کوارتز: ۶ بلوک → ۴ پله."))

NEW_RECIPES.append(R("quartz-slab", "تخته‌ی نازک کوارتز", "Quartz Slab", BUILDING,
                     [[None, None, None],
                      [None, None, None],
                      ["quartz-block", "quartz-block", "quartz-block"]],
                     "quartz-slab", 6, output_type="block",
                     aliases=["تخته‌ی نازک کوارتز", "quartz slab"],
                     icon="▬",
                     description="تخته‌ی نازک کوارتز: ۳ بلوک → ۶."))

NEW_RECIPES.append(R("quartz-pillar", "ستون کوارتز", "Quartz Pillar", BUILDING,
                     [[None, None, None],
                      ["quartz-block", "quartz-block", None],
                      [None, None, None]],
                     "quartz-pillar", 2, output_type="block",
                     aliases=["ستون کوارتز", "quartz pillar"],
                     icon="⬜",
                     description="ستون کوارتز: ۲ بلوک کنار هم → ۲ ستون."))

# ─── Purpur family ────────────────────────────────────────────────────
NEW_RECIPES.append(R("purpur-block", "بلوک پورپور", "Purpur Block", BUILDING,
                     [[None, None, None],
                      ["popped-chorus-fruit", "popped-chorus-fruit", None],
                      ["popped-chorus-fruit", "popped-chorus-fruit", None]],
                     "purpur-block", 4, output_type="block",
                     aliases=["بلوک پورپور", "purpur block"],
                     icon="🟣",
                     description="بلوک پورپور: ۴ popped chorus fruit → ۴ بلوک. از End."))

NEW_RECIPES.append(R("purpur-stairs", "پله‌ی پورپور", "Purpur Stairs", BUILDING,
                     [["purpur-block", None, None],
                      ["purpur-block", "purpur-block", None],
                      ["purpur-block", "purpur-block", "purpur-block"]],
                     "purpur-stairs", 4, output_type="block",
                     aliases=["پله‌ی پورپور", "purpur stairs"],
                     icon="🪜",
                     description="پله‌ی پورپور: ۶ بلوک → ۴ پله."))

NEW_RECIPES.append(R("purpur-slab", "تخته‌ی نازک پورپور", "Purpur Slab", BUILDING,
                     [[None, None, None],
                      [None, None, None],
                      ["purpur-block", "purpur-block", "purpur-block"]],
                     "purpur-slab", 6, output_type="block",
                     aliases=["تخته‌ی نازک پورپور", "purpur slab"],
                     icon="▬",
                     description="تخته‌ی نازک پورپور: ۳ بلوک → ۶."))

NEW_RECIPES.append(R("purpur-pillar", "ستون پورپور", "Purpur Pillar", BUILDING,
                     [[None, None, None],
                      ["purpur-block", "purpur-block", None],
                      [None, None, None]],
                     "purpur-pillar", 2, output_type="block",
                     aliases=["ستون پورپور", "purpur pillar"],
                     icon="🟣",
                     description="ستون پورپور: ۲ بلوک → ۲ ستون."))

# ─── Glass + Iron bars ────────────────────────────────────────────────
NEW_RECIPES.append(R("glass-pane", "شیشه‌ی حصاری", "Glass Pane", BUILDING,
                     [["glass", "glass", "glass"],
                      ["glass", "glass", "glass"],
                      [None, None, None]],
                     "glass-pane", 16, output_type="block",
                     aliases=["شیشه‌ی حصاری", "glass pane"],
                     icon="🪟",
                     description="شیشه‌ی حصاری: ۶ شیشه → ۱۶ pan."))

NEW_RECIPES.append(R("iron-bars", "میله‌ی آهنی", "Iron Bars", BUILDING,
                     [["iron-ingot", "iron-ingot", "iron-ingot"],
                      ["iron-ingot", "iron-ingot", "iron-ingot"],
                      [None, None, None]],
                     "iron-bars", 16, output_type="block",
                     aliases=["میله‌ی آهنی", "iron bars"],
                     icon="🪟",
                     description="میله‌ی آهنی: ۶ شمش آهن → ۱۶ میله."))

# ─── Walls ────────────────────────────────────────────────────────────
NEW_RECIPES.append(R("cobblestone-wall", "دیوار کوبل‌ستون", "Cobblestone Wall", BUILDING,
                     [["cobblestone", "cobblestone", "cobblestone"],
                      ["cobblestone", "cobblestone", "cobblestone"],
                      [None, None, None]],
                     "cobblestone-wall", 6, output_type="block",
                     aliases=["دیوار کوبل‌ستون", "cobblestone wall"],
                     icon="🧱",
                     description="دیوار کوبل‌ستون: ۶ کوبل‌ستون → ۶ دیوار."))

NEW_RECIPES.append(R("mossy-cobblestone-wall", "دیوار کوبل‌ستون خزه‌دار", "Mossy Cobblestone Wall", BUILDING,
                     [["mossy-cobblestone", "mossy-cobblestone", "mossy-cobblestone"],
                      ["mossy-cobblestone", "mossy-cobblestone", "mossy-cobblestone"],
                      [None, None, None]],
                     "mossy-cobblestone-wall", 6, output_type="block",
                     aliases=["دیوار کوبل‌ستون خزه‌دار", "mossy cobblestone wall"],
                     icon="🧱",
                     description="دیوار کوبل‌ستون خزه‌دار: ۶ بلوک → ۶ دیوار."))

NEW_RECIPES.append(R("end-stone-bricks", "آجر end stone", "End Stone Bricks", BUILDING,
                     [[None, None, None],
                      ["end-stone", "end-stone", None],
                      ["end-stone", "end-stone", None]],
                     "end-stone-bricks", 4, output_type="block",
                     aliases=["آجر end stone", "end stone bricks"],
                     icon="🧱",
                     description="آجر end stone: ۴ بلوک → ۴ آجر."))

# ─── Stone variant blocks (andesite/diorite/granite + polished) ──────
NEW_RECIPES.append(R("andesite", "آندزیت", "Andesite", BUILDING,
                     [[None, None, None],
                      ["cobblestone", "diorite", None],
                      [None, None, None]],
                     "andesite", 2, output_type="block",
                     aliases=["آندزیت", "andesite"],
                     icon="🪨",
                     shapeless=True,
                     description="آندزیت: ۱ کوبل‌ستون + ۱ diorite → ۲."))

NEW_RECIPES.append(R("diorite", "دیوریت", "Diorite", BUILDING,
                     [["cobblestone", "nether-quartz", None],
                      ["nether-quartz", "cobblestone", None],
                      [None, None, None]],
                     "diorite", 2, output_type="block",
                     aliases=["دیوریت", "diorite"],
                     icon="🪨",
                     shapeless=True,
                     description="دیوریت: ۲ کوبل‌ستون + ۲ کوارتز → ۲."))

NEW_RECIPES.append(R("granite", "گرانیت", "Granite", BUILDING,
                     [[None, None, None],
                      ["diorite", "nether-quartz", None],
                      [None, None, None]],
                     "granite", 2, output_type="block",
                     aliases=["گرانیت", "granite"],
                     icon="🪨",
                     shapeless=True,
                     description="گرانیت: ۱ diorite + ۱ کوارتز → ۲."))

NEW_RECIPES.append(R("polished-andesite", "آندزیت صیقلی", "Polished Andesite", BUILDING,
                     [[None, None, None],
                      ["andesite", "andesite", None],
                      ["andesite", "andesite", None]],
                     "polished-andesite", 4, output_type="block",
                     aliases=["آندزیت صیقلی", "polished andesite"],
                     icon="🪨",
                     description="آندزیت صیقلی: ۴ آندزیت → ۴ صیقلی."))

NEW_RECIPES.append(R("polished-granite", "گرانیت صیقلی", "Polished Granite", BUILDING,
                     [[None, None, None],
                      ["granite", "granite", None],
                      ["granite", "granite", None]],
                     "polished-granite", 4, output_type="block",
                     aliases=["گرانیت صیقلی", "polished granite"],
                     icon="🪨",
                     description="گرانیت صیقلی: ۴ گرانیت → ۴."))

NEW_RECIPES.append(R("polished-diorite", "دیوریت صیقلی", "Polished Diorite", BUILDING,
                     [[None, None, None],
                      ["diorite", "diorite", None],
                      ["diorite", "diorite", None]],
                     "polished-diorite", 4, output_type="block",
                     aliases=["دیوریت صیقلی", "polished diorite"],
                     icon="🪨",
                     description="دیوریت صیقلی: ۴ دیوریت → ۴."))

NEW_RECIPES.append(R("mossy-cobblestone", "کوبل‌ستون خزه‌دار", "Mossy Cobblestone", BUILDING,
                     [[None, None, None],
                      [None, None, None],
                      ["cobblestone", "vine", None]],
                     "mossy-cobblestone", 1, output_type="block",
                     aliases=["کوبل‌ستون خزه‌دار", "mossy cobblestone"],
                     icon="🪨",
                     shapeless=True,
                     description="کوبل‌ستون خزه‌دار: ۱ کوبل‌ستون + ۱ پیچک (یا moss-block)."))

# ─── Wool / Carpet / Banner / Painting ────────────────────────────────
NEW_RECIPES.append(R("wool", "پشم", "Wool", BUILDING,
                     [[None, None, None],
                      ["string", "string", None],
                      ["string", "string", None]],
                     "wool", 1, output_type="block",
                     aliases=["پشم", "wool"],
                     icon="🧶",
                     description="پشم: ۴ نخ → ۱ بلوک پشم."))

NEW_RECIPES.append(R("carpet", "فرش", "Carpet", BUILDING,
                     [[None, None, None],
                      ["wool", "wool", None],
                      [None, None, None]],
                     "carpet", 3, output_type="block",
                     aliases=["فرش", "carpet"],
                     icon="🟥",
                     description="فرش: ۲ پشم → ۳ فرش."))

NEW_RECIPES.append(R("banner", "پرچم", "Banner", BUILDING,
                     [[None, None, None],
                      ["wool", "wool", "wool"],
                      ["wool", "wool", "wool"]],
                     "banner", 1, output_type="block",
                     aliases=["پرچم", "banner"],
                     icon="🚩",
                     description="پرچم: ۶ پشم → ۱ پرچم. نیاز به چوب برای جا‌دادن."))

NEW_RECIPES.append(R("painting", "نقاشی", "Painting", BUILDING,
                     [["stick", "stick", "stick"],
                      ["stick", "wool", "stick"],
                      ["stick", "stick", "stick"]],
                     "painting", 1, output_type="block",
                     aliases=["نقاشی", "painting"],
                     icon="🖼️",
                     description="نقاشی: ۸ چوب + ۱ پشم → ۱ نقاشی."))

# ─── Colored variants (5 colors × 7 item types) ───────────────────────
COLORS = [
    ("red", "قرمز", "red", "🟥"),
    ("blue", "آبی", "blue", "🟦"),
    ("green", "سبز", "green", "🟩"),
    ("yellow", "زرد", "yellow", "🟨"),
    ("black", "سیاه", "black", "⬛"),
    ("white", "سفید", "white", "⬜"),
]

# Colored wool (shapeless: 1 white-wool + 1 dye → 1 colored-wool)
for color_id, color_fa, color_en, color_emoji in COLORS:
    NEW_RECIPES.append(R(f"{color_id}-wool", f"پشم {color_fa}", f"{color_en.title()} Wool", BUILDING,
                         [[None, None, None],
                          [None, None, None],
                          ["wool", f"{color_id}-dye", None]],
                         f"{color_id}-wool", 1, output_type="block",
                         aliases=[f"پشم {color_fa}", f"{color_en} wool"],
                         icon=color_emoji,
                         shapeless=True,
                         description=f"پشم {color_fa}: ۱ پشم سفید + ۱ رنگ {color_fa} → ۱."))

# Colored carpet (3 colored-wool → 6 carpet — actually 2 → 3 like white)
for color_id, color_fa, color_en, color_emoji in COLORS:
    NEW_RECIPES.append(R(f"{color_id}-carpet", f"فرش {color_fa}", f"{color_en.title()} Carpet", BUILDING,
                         [[None, None, None],
                          [f"{color_id}-wool", f"{color_id}-wool", None],
                          [None, None, None]],
                         f"{color_id}-carpet", 3, output_type="block",
                         aliases=[f"فرش {color_fa}", f"{color_en} carpet"],
                         icon=color_emoji,
                         description=f"فرش {color_fa}: ۲ پشم {color_fa} → ۳ فرش."))

# Colored bed (3 planks + 3 colored-wool → 1 colored-bed)
for color_id, color_fa, color_en, color_emoji in COLORS:
    NEW_RECIPES.append(R(f"{color_id}-bed", f"تخت {color_fa}", f"{color_en.title()} Bed", BUILDING,
                         [[f"{color_id}-wool", f"{color_id}-wool", f"{color_id}-wool"],
                          ["oak-planks", "oak-planks", "oak-planks"],
                          [None, None, None]],
                         f"{color_id}-bed", 1, output_type="block",
                         aliases=[f"تخت {color_fa}", f"{color_en} bed"],
                         icon="🛏️",
                         description=f"تخت {color_fa}: ۳ پشم {color_fa} + ۳ تخته → ۱."))

# Stained glass (8 glass + 1 dye → 8 stained glass — shapeless approximation)
for color_id, color_fa, color_en, color_emoji in COLORS:
    NEW_RECIPES.append(R(f"{color_id}-stained-glass", f"شیشه‌ی {color_fa}", f"{color_en.title()} Stained Glass", BUILDING,
                         [["glass", "glass", "glass"],
                          ["glass", f"{color_id}-dye", "glass"],
                          ["glass", "glass", "glass"]],
                         f"{color_id}-stained-glass", 8, output_type="block",
                         aliases=[f"شیشه‌ی {color_fa}", f"{color_en} stained glass"],
                         icon=color_emoji,
                         description=f"شیشه‌ی {color_fa}: ۸ شیشه + ۱ رنگ → ۸."))

# Stained glass pane (6 stained glass → 16 panes)
for color_id, color_fa, color_en, color_emoji in COLORS:
    NEW_RECIPES.append(R(f"{color_id}-stained-glass-pane", f"شیشه‌ی حصاری {color_fa}", f"{color_en.title()} Stained Glass Pane", BUILDING,
                         [[f"{color_id}-stained-glass", f"{color_id}-stained-glass", f"{color_id}-stained-glass"],
                          [f"{color_id}-stained-glass", f"{color_id}-stained-glass", f"{color_id}-stained-glass"],
                          [None, None, None]],
                         f"{color_id}-stained-glass-pane", 16, output_type="block",
                         aliases=[f"شیشه‌ی حصاری {color_fa}", f"{color_en} stained glass pane"],
                         icon=color_emoji,
                         description=f"شیشه‌ی حصاری {color_fa}: ۶ شیشه‌ی {color_fa} → ۱۶."))

# Colored terracotta (1 terracotta + 1 dye → 1 colored — terracotta smelted from clay first)
for color_id, color_fa, color_en, color_emoji in COLORS:
    NEW_RECIPES.append(R(f"{color_id}-terracotta", f"تراکوتای {color_fa}", f"{color_en.title()} Terracotta", BUILDING,
                         [[None, None, None],
                          [None, None, None],
                          ["terracotta", f"{color_id}-dye", None]],
                         f"{color_id}-terracotta", 1, output_type="block",
                         aliases=[f"تراکوتای {color_fa}", f"{color_en} terracotta"],
                         icon=color_emoji,
                         shapeless=True,
                         description=f"تراکوتای {color_fa}: ۱ تراکوتا + ۱ رنگ → ۱."))

# Concrete powder (4 sand + 4 gravel + 1 dye → 8 concrete powder)
for color_id, color_fa, color_en, color_emoji in COLORS:
    NEW_RECIPES.append(R(f"{color_id}-concrete-powder", f"پودر بتون {color_fa}", f"{color_en.title()} Concrete Powder", BUILDING,
                         [["sand", "sand", "sand"],
                          ["sand", f"{color_id}-dye", "gravel"],
                          ["gravel", "gravel", "gravel"]],
                         f"{color_id}-concrete-powder", 8, output_type="block",
                         aliases=[f"پودر بتون {color_fa}", f"{color_en} concrete powder"],
                         icon=color_emoji,
                         shapeless=True,
                         description=f"پودر بتون {color_fa}: ۴ شن + ۴ شن‌سنگ + ۱ رنگ → ۸. با آب → بتن."))


# ═════════════════════════════════════════════════════════════════════════
# REDSTONE
# ═════════════════════════════════════════════════════════════════════════

NEW_RECIPES.append(R("redstone-block", "بلوک رد‌استون", "Block of Redstone", REDSTONE,
                     [["redstone", "redstone", "redstone"],
                      ["redstone", "redstone", "redstone"],
                      ["redstone", "redstone", "redstone"]],
                     "redstone-block", 1, output_type="block",
                     aliases=["بلوک رد‌استون", "redstone block", "block of redstone"],
                     icon="🔴",
                     description="بلوک رد‌استون: ۹ redstone dust → ۱ بلوک. منبع سیگنال."))

NEW_RECIPES.append(R("repeater", "تکرارکننده‌ی رد‌استون", "Redstone Repeater", REDSTONE,
                     [[None, "redstone-torch", None],
                      ["redstone-torch", "redstone", None],
                      ["smooth-stone-slab", "smooth-stone-slab", None]],
                     "repeater", 1, output_type="block",
                     aliases=["تکرارکننده", "repeater", "redstone repeater"],
                     icon="🔁",
                     description="تکرارکننده: ۲ redstone-torch + ۱ redstone + ۲ تخته‌ی سنگی صاف."))

NEW_RECIPES.append(R("comparator", "مقایسه‌کننده", "Redstone Comparator", REDSTONE,
                     [[None, "redstone-torch", None],
                      ["nether-quartz", "redstone", None],
                      ["smooth-stone-slab", "smooth-stone-slab", None]],
                     "comparator", 1, output_type="block",
                     aliases=["مقایسه‌کننده", "comparator"],
                     icon="⚖️",
                     description="مقایسه‌کننده: ۱ torch + ۱ quartz + ۱ redstone + ۲ تخته‌ی سنگی."))

NEW_RECIPES.append(R("piston", "پیستون", "Piston", REDSTONE,
                     [["cobblestone", "cobblestone", "cobblestone"],
                      ["cobblestone", "iron-ingot", "cobblestone"],
                      ["cobblestone", "redstone", "cobblestone"]],
                     "piston", 1, output_type="block",
                     aliases=["پیستون", "piston"],
                     icon="🔧",
                     description="پیستون: ۴ کوبل‌ستون + ۱ آهن + ۱ redstone + ۳ تخته. متصل به solid block."))

NEW_RECIPES.append(R("sticky-piston", "پیستون چسبناک", "Sticky Piston", REDSTONE,
                     [[None, "slimeball", None],
                      ["piston", "piston", None],
                      [None, None, None]],
                     "sticky-piston", 1, output_type="block",
                     aliases=["پیستون چسبناک", "sticky piston"],
                     icon="🔧",
                     shapeless=True,
                     description="پیستون چسبناک: ۱ slimeball + ۱ پیستون."))

NEW_RECIPES.append(R("dispenser", "پخش‌کننده", "Dispenser", REDSTONE,
                     [["cobblestone", "bow", "cobblestone"],
                      ["cobblestone", "redstone", "cobblestone"],
                      ["cobblestone", "cobblestone", "cobblestone"]],
                     "dispenser", 1, output_type="block",
                     aliases=["پخش‌کننده", "dispenser"],
                     icon="🔫",
                     description="پخش‌کننده: ۷ کوبل‌ستون + ۱ کمان + ۱ redstone. آیتم‌ها رو شلیک می‌کنه."))

NEW_RECIPES.append(R("dropper", "ریزنده", "Dropper", REDSTONE,
                     [["cobblestone", "cobblestone", "cobblestone"],
                      ["cobblestone", None, "cobblestone"],
                      ["cobblestone", "redstone", "cobblestone"]],
                     "dropper", 1, output_type="block",
                     aliases=["ریزنده", "dropper"],
                     icon="📤",
                     description="ریزنده: ۷ کوبل‌ستون + ۱ redstone. آیتم رو ریزش می‌کنه."))

NEW_RECIPES.append(R("observer", "نگر", "Observer", REDSTONE,
                     [["cobblestone", "cobblestone", "cobblestone"],
                      ["redstone", "nether-quartz", "redstone"],
                      ["cobblestone", "cobblestone", "cobblestone"]],
                     "observer", 1, output_type="block",
                     aliases=["نگر", "observer"],
                     icon="👁️",
                     description="نگر: ۶ کوبل‌ستون + ۲ redstone + ۱ quartz. تغییرات بلاک رو تشخیص می‌ده."))

NEW_RECIPES.append(R("hopper", "قیف", "Hopper", REDSTONE,
                     [[None, "iron-ingot", None],
                      ["iron-ingot", "chest", "iron-ingot"],
                      ["iron-ingot", "iron-ingot", "iron-ingot"]],
                     "hopper", 1, output_type="block",
                     aliases=["قیف", "hopper"],
                     icon="⬇️",
                     description="قیف: ۵ آهن + ۱ صندوق. آیتم‌ها رو جمع می‌کنه."))

NEW_RECIPES.append(R("daylight-detector", "حسگر روز", "Daylight Detector", REDSTONE,
                     [[None, None, None],
                      ["glass", "glass", "glass"],
                      ["nether-quartz", "nether-quartz", "nether-quartz"]],
                     "daylight-detector", 1, output_type="block",
                     aliases=["حسگر روز", "daylight detector", "daylight sensor"],
                     icon="☀️",
                     description="حسگر روز: ۳ شیشه + ۳ کوارتز ندر + ۳ تخته. نور خورشید رو تشخیص می‌ده."))

NEW_RECIPES.append(R("note-block", "بلوک نت", "Note Block", REDSTONE,
                     [["oak-planks", "oak-planks", "oak-planks"],
                      ["oak-planks", "redstone", "oak-planks"],
                      ["oak-planks", "oak-planks", "oak-planks"]],
                     "note-block", 1, output_type="block",
                     aliases=["بلوک نت", "note block"],
                     icon="🎵",
                     description="بلوک نت: ۸ تخته + ۱ redstone. نت‌های موسیقی."))

NEW_RECIPES.append(R("tripwire-hook", "قلاب سیم", "Tripwire Hook", REDSTONE,
                     [[None, None, None],
                      ["iron-ingot", "stick", "oak-planks"],
                      [None, None, None]],
                     "tripwire-hook", 2, output_type="block",
                     aliases=["قلاب سیم", "tripwire hook"],
                     icon="🪝",
                     description="قلاب سیم: ۱ آهن + ۱ چوب + ۱ تخته → ۲. ساخت تله."))

NEW_RECIPES.append(R("target-block", "بلوک هدف", "Target", REDSTONE,
                     [["redstone", "redstone", "redstone"],
                      ["redstone", "hay-block", "redstone"],
                      ["redstone", "redstone", "redstone"]],
                     "target", 1, output_type="block",
                     aliases=["بلوک هدف", "target", "target block"],
                     icon="🎯",
                     description="بلوک هدف: ۴ redstone + ۱ بلوک یونجه. سیگنال بر اساس محل اصابت."))

NEW_RECIPES.append(R("redstone-torch", "مشعل رد‌استون", "Redstone Torch", REDSTONE,
                     [[None, None, None],
                      [None, "redstone", None],
                      [None, "stick", None]],
                     "redstone-torch", 1, output_type="block",
                     aliases=["مشعل رد‌استون", "redstone torch"],
                     icon="🔦",
                     description="مشعل رد‌استون: ۱ redstone + ۱ چوب. منبع سیگنال."))

NEW_RECIPES.append(R("redstone-lamp", "چراغ رد‌استون", "Redstone Lamp", REDSTONE,
                     [[None, None, None],
                      [None, "glowstone", None],
                      ["redstone", "redstone", "redstone"]],
                     "redstone-lamp", 1, output_type="block",
                     aliases=["چراغ رد‌استون", "redstone lamp"],
                     icon="💡",
                     description="چراغ رد‌استون: ۱ glowstone + ۴ redstone. با سیگنال روشن می‌شه."))

NEW_RECIPES.append(R("lever", "اهرم", "Lever", REDSTONE,
                     [[None, None, None],
                      [None, "stick", None],
                      [None, "cobblestone", None]],
                     "lever", 1, output_type="block",
                     aliases=["اهرم", "lever"],
                     icon="🎚️",
                     description="اهرم: ۱ چوب + ۱ کوبل‌ستون. سوئیچ دستی."))

NEW_RECIPES.append(R("wooden-pressure-plate", "صفحه‌ی فشار چوبی", "Wooden Pressure Plate", REDSTONE,
                     [[None, None, None],
                      [None, None, None],
                      ["oak-planks", "oak-planks", None]],
                     "oak-pressure-plate", 1, output_type="block",
                     aliases=["صفحه‌ی فشار چوبی", "wooden pressure plate"],
                     icon="🔛",
                     description="صفحه‌ی فشار چوبی: ۲ تخته → ۱. همه‌ی ماب‌ها فعالش می‌کنن."))

NEW_RECIPES.append(R("stone-pressure-plate", "صفحه‌ی فشار سنگی", "Stone Pressure Plate", REDSTONE,
                     [[None, None, None],
                      [None, None, None],
                      ["stone", "stone", None]],
                     "stone-pressure-plate", 1, output_type="block",
                     aliases=["صفحه‌ی فشار سنگی", "stone pressure plate"],
                     icon="🔛",
                     description="صفحه‌ی فشار سنگی: ۲ سنگ. فقط بازیکنان و ماب‌ها فعال می‌کنن."))

NEW_RECIPES.append(R("wooden-button", "دکمه‌ی چوبی", "Wooden Button", REDSTONE,
                     [[None, None, None],
                      [None, None, None],
                      [None, "oak-planks", None]],
                     "oak-button", 1, output_type="block",
                     aliases=["دکمه‌ی چوبی", "wooden button"],
                     icon="🔘",
                     shapeless=True,
                     description="دکمه‌ی چوبی: ۱ تخته. سیگنال کوتاه."))

NEW_RECIPES.append(R("stone-button", "دکمه‌ی سنگی", "Stone Button", REDSTONE,
                     [[None, None, None],
                      [None, None, None],
                      [None, "stone", None]],
                     "stone-button", 1, output_type="block",
                     aliases=["دکمه‌ی سنگی", "stone button"],
                     icon="🔘",
                     shapeless=True,
                     description="دکمه‌ی سنگی: ۱ سنگ. سیگنال خیلی کوتاه."))

NEW_RECIPES.append(R("rail", "ریل", "Rail", REDSTONE,
                     [[None, None, None],
                      ["iron-ingot", "stick", "iron-ingot"],
                      ["iron-ingot", "iron-ingot", "iron-ingot"]],
                     "rail", 16, output_type="block",
                     aliases=["ریل", "rail", "rails"],
                     icon="🛤️",
                     description="ریل: ۶ آهن + ۱ چوب → ۱۶ ریل. حرکت ماین‌کارت."))

NEW_RECIPES.append(R("powered-rail", "ریل فعال", "Powered Rail", REDSTONE,
                     [[None, None, None],
                      ["gold-ingot", "stick", "gold-ingot"],
                      ["gold-ingot", "redstone", "gold-ingot"]],
                     "powered-rail", 6, output_type="block",
                     aliases=["ریل فعال", "powered rail"],
                     icon="🛤️",
                     description="ریل فعال: ۶ طلا + ۱ چوب + ۱ redstone → ۶. سرعت ماین‌کارت."))

NEW_RECIPES.append(R("detector-rail", "ریل تشخیص‌دهنده", "Detector Rail", REDSTONE,
                     [[None, None, None],
                      ["iron-ingot", "stone-pressure-plate", "iron-ingot"],
                      ["iron-ingot", "redstone", "iron-ingot"]],
                     "detector-rail", 6, output_type="block",
                     aliases=["ریل تشخیص‌دهنده", "detector rail"],
                     icon="🛤️",
                     description="ریل تشخیص‌دهنده: ۶ آهن + ۱ صفحه فشار + ۱ redstone → ۶."))

NEW_RECIPES.append(R("activator-rail", "ریل فعال‌کننده", "Activator Rail", REDSTONE,
                     [[None, None, None],
                      ["iron-ingot", "stick", "iron-ingot"],
                      ["iron-ingot", "redstone-torch", "iron-ingot"]],
                     "activator-rail", 6, output_type="block",
                     aliases=["ریل فعال‌کننده", "activator rail"],
                     icon="🛤️",
                     description="ریل فعال‌کننده: ۶ آهن + ۱ چوب + ۱ redstone-torch → ۶."))

NEW_RECIPES.append(R("lightning-rod", "میله‌ی رعد", "Lightning Rod", REDSTONE,
                     [[None, "copper-ingot", None],
                      [None, "copper-ingot", None],
                      [None, "copper-ingot", None]],
                     "lightning-rod", 1, output_type="block",
                     aliases=["میله‌ی رعد", "lightning rod"],
                     icon="⚡",
                     description="میله‌ی رعد: ۳ شمش مس. رعد رو جذب می‌کنه."))


# ═════════════════════════════════════════════════════════════════════════
# FOOD
# ═════════════════════════════════════════════════════════════════════════

NEW_RECIPES.append(R("cake", "کیک", "Cake", FOOD,
                     [[None, "milk-bucket", None],
                      ["milk-bucket", "egg", "milk-bucket"],
                      ["wheat", "sugar", "wheat"]],
                     "cake", 1, output_type="block",
                     aliases=["کیک", "cake"],
                     icon="🎂",
                     description="کیک: ۳ سطل شیر + ۲ گندم + ۱ تخم‌مرغ + ۲ شکر. ۸ بیت."))

NEW_RECIPES.append(R("cookie", "کوکی", "Cookie", FOOD,
                     [[None, None, None],
                      [None, None, None],
                      ["wheat", "cocoa-beans", "wheat"]],
                     "cookie", 8,
                     aliases=["کوکی", "cookie"],
                     icon="🍪",
                     shapeless=True,
                     description="کوکی: ۲ گندم + ۱ cocoa beans → ۸ کوکی."))

NEW_RECIPES.append(R("pumpkin-pie", "پای کدو", "Pumpkin Pie", FOOD,
                     [[None, None, None],
                      [None, None, None],
                      ["pumpkin", "egg", "sugar"]],
                     "pumpkin-pie", 1,
                     aliases=["پای کدو", "pumpkin pie"],
                     icon="🥧",
                     shapeless=True,
                     description="پای کدو: ۱ کدو + ۱ تخم‌مرغ + ۱ شکر."))

NEW_RECIPES.append(R("golden-apple", "سیب طلایی", "Golden Apple", FOOD,
                     [["gold-ingot", "gold-ingot", "gold-ingot"],
                      ["gold-ingot", "apple", "gold-ingot"],
                      ["gold-ingot", "gold-ingot", "gold-ingot"]],
                     "golden-apple", 1,
                     aliases=["سیب طلایی", "golden apple"],
                     icon="🍎",
                     description="سیب طلایی: ۸ شمش طلا + ۱ سیب. درمان سریع."))

NEW_RECIPES.append(R("golden-carrot", "هویج طلایی", "Golden Carrot", FOOD,
                     [["gold-nugget", "gold-nugget", "gold-nugget"],
                      ["gold-nugget", "carrot", "gold-nugget"],
                      ["gold-nugget", "gold-nugget", "gold-nugget"]],
                     "golden-carrot", 1,
                     aliases=["هویج طلایی", "golden carrot"],
                     icon="🥕",
                     description="هویج طلایی: ۸ gold nugget + ۱ هویج. غذای اسب."))

NEW_RECIPES.append(R("sugar", "شکر", "Sugar", FOOD,
                     [[None, None, None],
                      [None, None, None],
                      [None, "sugar-cane", None]],
                     "sugar", 1,
                     aliases=["شکر", "sugar"],
                     icon="🍬",
                     shapeless=True,
                     description="شکر: ۱ نیشکر → ۱. برای کیک، کوکی، و معجون."))

NEW_RECIPES.append(R("mushroom-stew", "خورش قارچ", "Mushroom Stew", FOOD,
                     [[None, None, None],
                      [None, "red-mushroom", "brown-mushroom"],
                      [None, "bowl", None]],
                     "mushroom-stew", 1,
                     aliases=["خورش قارچ", "mushroom stew"],
                     icon="🍲",
                     shapeless=True,
                     description="خورش قارچ: ۱ قارچ قرمز + ۱ قارچ قهوه‌ای + ۱ کاسه."))

NEW_RECIPES.append(R("beetroot-soup", "سوپ چغندر", "Beetroot Soup", FOOD,
                     [[None, None, None],
                      ["beetroot", "beetroot", "beetroot"],
                      ["beetroot", "bowl", "beetroot"]],
                     "beetroot-soup", 1,
                     aliases=["سوپ چغندر", "beetroot soup"],
                     icon="🥣",
                     description="سوپ چغندر: ۴ چغندر + ۱ کاسه."))

NEW_RECIPES.append(R("honey-bottle", "بطری عسل", "Honey Bottle", FOOD,
                     [["honeycomb", "honeycomb", None],
                      ["honeycomb", "glass-bottle", None],
                      ["honeycomb", "honeycomb", None]],
                     "honey-bottle", 1,
                     aliases=["بطری عسل", "honey bottle"],
                     icon="🍯",
                     shapeless=True,
                     description="بطری عسل: ۴ honeycomb + ۱ بطری شیشه‌ای. پاک‌کردن مسمومیت."))

NEW_RECIPES.append(R("honey-block", "بلوک عسل", "Honey Block", FOOD,
                     [["honey-bottle", "honey-bottle", "honey-bottle"],
                      ["honey-bottle", "honey-bottle", "honey-bottle"],
                      ["honey-bottle", "honey-bottle", "honey-bottle"]],
                     "honey-block", 4, output_type="block",
                     aliases=["بلوک عسل", "honey block"],
                     icon="🍯",
                     description="بلوک عسل: ۴ بطری عسل → ۱. چسبناک، افت سرعت."))

NEW_RECIPES.append(R("melon-seeds", "تخم هندوانه", "Melon Seeds", FOOD,
                     [[None, None, None],
                      [None, None, None],
                      [None, "melon-slice", None]],
                     "melon-seeds", 1,
                     aliases=["تخم هندوانه", "melon seeds"],
                     icon="🌱",
                     shapeless=True,
                     description="تخم هندوانه: ۱ قاچ هندوانه → ۱ تخم."))

NEW_RECIPES.append(R("pumpkin-seeds", "تخم کدو", "Pumpkin Seeds", FOOD,
                     [[None, None, None],
                      [None, "pumpkin", None],
                      [None, None, None]],
                     "pumpkin-seeds", 4,
                     aliases=["تخم کدو", "pumpkin seeds"],
                     icon="🌱",
                     shapeless=True,
                     description="تخم کدو: ۱ کدو → ۴ تخم."))

NEW_RECIPES.append(R("suspicious-stew", "خورش مشکوک", "Suspicious Stew", FOOD,
                     [[None, None, None],
                      ["red-mushroom", "brown-mushroom", None],
                      ["bowl", None, None]],
                     "suspicious-stew", 1,
                     aliases=["خورش مشکوک", "suspicious stew"],
                     icon="🍲",
                     shapeless=True,
                     description="خورش مشکوک: ۲ قارچ + ۱ گل + ۱ کاسه. اثر بسته به گل."))

NEW_RECIPES.append(R("rabbit-stew", "خورش خرگوش", "Rabbit Stew", FOOD,
                     [[None, None, None],
                      [None, None, None],
                      ["cooked-rabbit", "baked-potato", None]],
                     "rabbit-stew", 1,
                     aliases=["خورش خرگوش", "rabbit stew"],
                     icon="🍲",
                     shapeless=True,
                     description="خورش خرگوش: ۱ خرگوش پخته + ۱ سیب‌زمینی پخته + ۱ هویج + ۱ قارچ + ۱ کاسه."))


# ═════════════════════════════════════════════════════════════════════════
# BREWING
# ═════════════════════════════════════════════════════════════════════════

NEW_RECIPES.append(R("brewing-stand", "میز جوش‌سازی", "Brewing Stand", BREWING,
                     [[None, "blaze-rod", None],
                      [None, "cobblestone", None],
                      ["cobblestone", "cobblestone", "cobblestone"]],
                     "brewing-stand", 1, output_type="block",
                     aliases=["میز جوش‌سازی", "brewing stand"],
                     icon="⚗️",
                     description="میز جوش‌سازی: ۱ blaze-rod + ۳ کوبل‌ستون. ساخت معجون."))

NEW_RECIPES.append(R("cauldron", "دیگ", "Cauldron", BREWING,
                     [["iron-ingot", None, "iron-ingot"],
                      ["iron-ingot", None, "iron-ingot"],
                      ["iron-ingot", "iron-ingot", "iron-ingot"]],
                     "cauldron", 1, output_type="block",
                     aliases=["دیگ", "cauldron"],
                     icon="🪣",
                     description="دیگ: ۷ شمش آهن. نگه‌داری آب و شستشوی رنگ banner."))

NEW_RECIPES.append(R("blaze-powder", "پودر blaze", "Blaze Powder", BREWING,
                     [[None, None, None],
                      [None, None, None],
                      [None, "blaze-rod", None]],
                     "blaze-powder", 2,
                     aliases=["پودر blaze", "blaze powder"],
                     icon="🔥",
                     shapeless=True,
                     description="پودر blaze: ۱ blaze-rod → ۲ پودر. سوخت brewing."))

NEW_RECIPES.append(R("glistering-melon", "هندوانه‌ی درخشنده", "Glistering Melon", BREWING,
                     [["gold-nugget", "gold-nugget", "gold-nugget"],
                      ["gold-nugget", "melon-slice", "gold-nugget"],
                      ["gold-nugget", "gold-nugget", "gold-nugget"]],
                     "glistering-melon", 1,
                     aliases=["هندوانه‌ی درخشنده", "glistering melon"],
                     icon="✨",
                     description="هندوانه‌ی درخشنده: ۸ gold-nugget + ۱ قاچ هندوانه. معجون درمان."))

NEW_RECIPES.append(R("magma-cream", "خامه‌ی ماگما", "Magma Cream", BREWING,
                     [[None, None, None],
                      [None, None, None],
                      ["slimeball", "blaze-powder", None]],
                     "magma-cream", 1,
                     aliases=["خامه‌ی ماگما", "magma cream"],
                     icon="🔥",
                     shapeless=True,
                     description="خامه‌ی ماگما: ۱ slimeball + ۱ پودر blaze. معجون مقاومت آتش."))

NEW_RECIPES.append(R("fermented-spider-eye", "چشم عنکبوت تخمیری", "Fermented Spider Eye", BREWING,
                     [[None, None, None],
                      [None, None, None],
                      ["spider-eye", "brown-mushroom", "sugar"]],
                     "fermented-spider-eye", 1,
                     aliases=["چشم عنکبوت تخمیری", "fermented spider eye"],
                     icon="👁️",
                     shapeless=True,
                     description="چشم عنکبوت تخمیری: ۱ چشم + ۱ قارچ + ۱ شکر. معجون آسیب."))

NEW_RECIPES.append(R("glass-bottle", "بطری شیشه‌ای", "Glass Bottle", BREWING,
                     [[None, None, None],
                      ["glass", None, "glass"],
                      [None, "glass", None]],
                     "glass-bottle", 3,
                     aliases=["بطری شیشه‌ای", "glass bottle"],
                     icon="🍾",
                     description="بطری شیشه‌ای: ۳ شیشه → ۳ بطری."))

NEW_RECIPES.append(R("ender-eye", "چشم دراگون", "Eye of Ender", BREWING,
                     [[None, None, None],
                      [None, None, None],
                      ["blaze-powder", "ender-pearl", None]],
                     "ender-eye", 1,
                     aliases=["چشم دراگون", "ender eye", "eye of ender"],
                     icon="👁️",
                     shapeless=True,
                     description="چشم دراگون: ۱ پودر blaze + ۱ مروارید ender. پیدا‌کردن stronghold."))

NEW_RECIPES.append(R("glowstone", "گلاستون", "Glowstone", BREWING,
                     [["glowstone-dust", "glowstone-dust", None],
                      ["glowstone-dust", "glowstone-dust", None],
                      [None, None, None]],
                     "glowstone", 1, output_type="block",
                     aliases=["گلاستون", "glowstone"],
                     icon="✨",
                     description="گلاستون: ۴ glowstone-dust → ۱ بلوک. تقویت‌کننده‌ی معجون."))

NEW_RECIPES.append(R("nether-wart-block", "بلوک wart ندر", "Nether Wart Block", BREWING,
                     [["nether-wart", "nether-wart", "nether-wart"],
                      ["nether-wart", "nether-wart", "nether-wart"],
                      ["nether-wart", "nether-wart", "nether-wart"]],
                     "nether-wart-block", 1, output_type="block",
                     aliases=["بلوک wart ندر", "nether wart block"],
                     icon="🌱",
                     description="بلوک wart ندر: ۹ wart → ۱ بلوک. تزئینی."))

NEW_RECIPES.append(R("tipped-arrow", "تیر کارآمد", "Tipped Arrow", BREWING,
                     [["arrow", "arrow", "arrow"],
                      ["arrow", "lingering-potion", "arrow"],
                      ["arrow", "arrow", "arrow"]],
                     "tipped-arrow", 8,
                     aliases=["تیر کارآمد", "tipped arrow"],
                     icon="🏹",
                     description="تیر کارآمد: ۸ تیر + ۱ معجون lingering → ۸ تیر با اثر."))


# ═════════════════════════════════════════════════════════════════════════
# MISC — storage, utility, decorative
# ═════════════════════════════════════════════════════════════════════════

NEW_RECIPES.append(R("trapped-chest", "صندوق تله", "Trapped Chest", MISC,
                     [[None, None, None],
                      [None, None, None],
                      ["chest", "tripwire-hook", None]],
                     "trapped-chest", 1, output_type="block",
                     aliases=["صندوق تله", "trapped chest"],
                     icon="📦",
                     shapeless=True,
                     description="صندوق تله: ۱ صندوق + ۱ قلاب سیم. سیگنال باز شدن."))

NEW_RECIPES.append(R("ender-chest", "صندوق ender", "Ender Chest", MISC,
                     [[None, "obsidian", None],
                      ["obsidian", "ender-eye", "obsidian"],
                      [None, "obsidian", None]],
                     "ender-chest", 1, output_type="block",
                     aliases=["صندوق ender", "ender chest"],
                     icon="📦",
                     description="صندوق ender: ۸ obsidian + ۱ چشم دراگون. ذخیره‌ی اشتراکی."))

NEW_RECIPES.append(R("enchanting-table", "میز افسون", "Enchanting Table", MISC,
                     [[None, None, None],
                      [None, "book", None],
                      ["obsidian", "obsidian", "diamond"]],
                     "enchanting-table", 1, output_type="block",
                     aliases=["میز افسون", "enchanting table"],
                     icon="📚",
                     description="میز افسون: ۴ obsidian + ۲ diamond + ۱ کتاب. ساخت افسون."))

NEW_RECIPES.append(R("anvil", "آهنگ", "Anvil", MISC,
                     [[None, "iron-block", None],
                      [None, "iron-ingot", None],
                      ["iron-ingot", "iron-ingot", "iron-ingot"]],
                     "anvil", 1, output_type="block",
                     aliases=["آهنگ", "anvil"],
                     icon="🔨",
                     description="آهنگ: ۳ بلوک آهن (top) + ۱ شمش (mid) + ۳ شمش (bot) = ۳۱ آهن."))

NEW_RECIPES.append(R("beacon", "بیکن", "Beacon", MISC,
                     [[None, None, None],
                      ["glass", "nether-star", "glass"],
                      ["obsidian", "obsidian", "obsidian"]],
                     "beacon", 1, output_type="block",
                     aliases=["بیکن", "beacon"],
                     icon="🁢",
                     description="بیکن: ۳ obsidian + ۵ شیشه + ۱ nether-star. اثر منطقه‌ای."))

NEW_RECIPES.append(R("conduit", "کاندویت", "Conduit", MISC,
                     [["nautilus-shell", "nautilus-shell", "nautilus-shell"],
                      ["nautilus-shell", "heart-of-the-sea", "nautilus-shell"],
                      ["nautilus-shell", "nautilus-shell", "nautilus-shell"]],
                     "conduit", 1, output_type="block",
                     aliases=["کاندویت", "conduit"],
                     icon="🌀",
                     description="کاندویت: ۸ صدف nautilus + ۱ heart of the sea. تنفس زیر آب."))

NEW_RECIPES.append(R("sea-lantern", "چراغ دریایی", "Sea Lantern", MISC,
                     [["prismarine-shard", "prismarine-crystals", "prismarine-shard"],
                      ["prismarine-crystals", "prismarine-crystals", "prismarine-crystals"],
                      ["prismarine-shard", "prismarine-crystals", "prismarine-shard"]],
                     "sea-lantern", 1, output_type="block",
                     aliases=["چراغ دریایی", "sea lantern"],
                     icon="💡",
                     description="چراغ دریایی: ۵ shard + ۴ crystals. نور زیر آب."))

NEW_RECIPES.append(R("lantern", "فانوس", "Lantern", MISC,
                     [[None, None, None],
                      [None, None, None],
                      ["iron-ingot", "torch", None]],
                     "lantern", 1, output_type="block",
                     aliases=["فانوس", "lantern"],
                     icon="🏮",
                     shapeless=True,
                     description="فانوس: ۱ شمش آهن + ۱ مشعل. نور روشن‌تر از مشعل."))

NEW_RECIPES.append(R("soul-torch", "مشعل روح", "Soul Torch", MISC,
                     [[None, None, None],
                      [None, "coal", None],
                      ["stick", "soul-sand", None]],
                     "soul-torch", 4, output_type="block",
                     aliases=["مشعل روح", "soul torch"],
                     icon="🔦",
                     shapeless=True,
                     description="مشعل روح: ۱ زغال + ۱ چوب + ۱ soul-sand/soul-soil → ۴."))

NEW_RECIPES.append(R("soul-lantern", "فانوس روح", "Soul Lantern", MISC,
                     [[None, None, None],
                      [None, None, None],
                      ["iron-ingot", "soul-torch", None]],
                     "soul-lantern", 1, output_type="block",
                     aliases=["فانوس روح", "soul lantern"],
                     icon="🏮",
                     shapeless=True,
                     description="فانوس روح: ۱ شمش + ۱ مشعل روح."))

NEW_RECIPES.append(R("campfire", "آتش اردوگاه", "Campfire", MISC,
                     [[None, "stick", None],
                      ["stick", "coal", "stick"],
                      ["oak-log", "oak-log", "oak-log"]],
                     "campfire", 1, output_type="block",
                     aliases=["آتش اردوگاه", "campfire"],
                     icon="🔥",
                     description="آتش اردوگاه: ۳ چوب + ۱ زغال/زغال چوب + ۳ sticks. پختن غذا."))

NEW_RECIPES.append(R("soul-campfire", "آتش اردوگاه روح", "Soul Campfire", MISC,
                     [[None, "stick", None],
                      ["stick", "soul-sand", "stick"],
                      ["oak-log", "oak-log", "oak-log"]],
                     "soul-campfire", 1, output_type="block",
                     aliases=["آتش اردوگاه روح", "soul campfire"],
                     icon="🔥",
                     description="آتش اردوگاه روح: ۳ چوب + ۱ soul-sand + ۳ sticks."))

NEW_RECIPES.append(R("item-frame", "قاب آیتم", "Item Frame", MISC,
                     [["stick", "stick", "stick"],
                      ["stick", "leather", "stick"],
                      ["stick", "stick", "stick"]],
                     "item-frame", 1, output_type="block",
                     aliases=["قاب آیتم", "item frame"],
                     icon="🖼️",
                     description="قاب آیتم: ۸ چوب + ۱ چرم. نمایش آیتم روی دیوار."))

NEW_RECIPES.append(R("flower-pot", "گلدان", "Flower Pot", MISC,
                     [[None, "brick-item", None],
                      ["brick-item", None, "brick-item"],
                      [None, None, None]],
                     "flower-pot", 1, output_type="block",
                     aliases=["گلدان", "flower pot"],
                     icon="🪴",
                     description="گلدان: ۳ brick-item. کاشتن گل‌های کوچک."))

NEW_RECIPES.append(R("jukebox", "جاک‌باکس", "Jukebox", MISC,
                     [["oak-planks", "oak-planks", "oak-planks"],
                      ["oak-planks", "diamond", "oak-planks"],
                      ["oak-planks", "oak-planks", "oak-planks"]],
                     "jukebox", 1, output_type="block",
                     aliases=["جاک‌باکس", "jukebox"],
                     icon="🎵",
                     description="جاک‌باکس: ۸ تخته + ۱ diamond. پخش موسیقی disc."))

NEW_RECIPES.append(R("barrel", "بشکه", "Barrel", MISC,
                     [["oak-planks", "oak-planks", "oak-planks"],
                      ["oak-slab", None, "oak-slab"],
                      ["oak-planks", "oak-planks", "oak-planks"]],
                     "barrel", 1, output_type="block",
                     aliases=["بشکه", "barrel"],
                     icon="🛢️",
                     description="بشکه: ۶ تخته + ۲ تخته‌ی نازک. ذخیره‌سازی."))

NEW_RECIPES.append(R("end-crystal", "کریستال end", "End Crystal", MISC,
                     [["glass", "eye-of-ender", "glass"],
                      ["glass", "ghast-tear", "glass"],
                      [None, None, None]],
                     "end-crystal", 1,
                     aliases=["کریستال end", "end crystal"],
                     icon="💎",
                     shapeless=True,
                     description="کریستال end: ۷ شیشه + ۱ ender-eye + ۱ ghast-tear. احضار دراگون."))

NEW_RECIPES.append(R("respawn-anchor", "لنگر تولد", "Respawn Anchor", MISC,
                     [["crying-obsidian", "crying-obsidian", "crying-obsidian"],
                      [None, "glowstone", None],
                      ["crying-obsidian", "crying-obsidian", "crying-obsidian"]],
                     "respawn-anchor", 1, output_type="block",
                     aliases=["لنگر تولد", "respawn anchor"],
                     icon="🌑",
                     description="لنگر تولد: ۶ crying-obsidian + ۱ glowstone. نقطه‌ی تولد در Nether."))

NEW_RECIPES.append(R("lodestone", "لودستون", "Lodestone", MISC,
                     [["netherite-ingot", "netherite-ingot", "netherite-ingot"],
                      ["netherite-ingot", "chiseled-stone-bricks", "netherite-ingot"],
                      ["netherite-ingot", "netherite-ingot", "netherite-ingot"]],
                     "lodestone", 1, output_type="block",
                     aliases=["لودستون", "lodestone"],
                     icon="🧭",
                     description="لودستون: ۸ netherite-ingot + ۱ chiseled-stone-bricks. تغییر قطب‌نما."))

# ─── Storage blocks (decompress ingots to blocks) ─────────────────────
NEW_RECIPES.append(R("diamond-block", "بلوک الماس", "Block of Diamond", MISC,
                     [["diamond", "diamond", "diamond"],
                      ["diamond", "diamond", "diamond"],
                      ["diamond", "diamond", "diamond"]],
                     "diamond-block", 1, output_type="block",
                     aliases=["بلوک الماس", "diamond block", "block of diamond"],
                     icon="💎",
                     description="بلوک الماس: ۹ الماس → ۱. تزئینی و برای beacon."))

NEW_RECIPES.append(R("iron-block", "بلوک آهن", "Block of Iron", MISC,
                     [["iron-ingot", "iron-ingot", "iron-ingot"],
                      ["iron-ingot", "iron-ingot", "iron-ingot"],
                      ["iron-ingot", "iron-ingot", "iron-ingot"]],
                     "iron-block", 1, output_type="block",
                     aliases=["بلوک آهن", "iron block", "block of iron"],
                     icon="🔩",
                     description="بلوک آهن: ۹ شمش آهن → ۱. برای آهنگ و beacon."))

NEW_RECIPES.append(R("gold-block", "بلوک طلا", "Block of Gold", MISC,
                     [["gold-ingot", "gold-ingot", "gold-ingot"],
                      ["gold-ingot", "gold-ingot", "gold-ingot"],
                      ["gold-ingot", "gold-ingot", "gold-ingot"]],
                     "gold-block", 1, output_type="block",
                     aliases=["بلوک طلا", "gold block", "block of gold"],
                     icon="🟨",
                     description="بلوک طلا: ۹ شمش طلا → ۱. تزئینی."))

NEW_RECIPES.append(R("emerald-block", "بلوک زمرد", "Block of Emerald", MISC,
                     [["emerald", "emerald", "emerald"],
                      ["emerald", "emerald", "emerald"],
                      ["emerald", "emerald", "emerald"]],
                     "emerald-block", 1, output_type="block",
                     aliases=["بلوک زمرد", "emerald block", "block of emerald"],
                     icon="💚",
                     description="بلوک زمرد: ۹ زمرد → ۱. تزئینی."))

NEW_RECIPES.append(R("netherite-block", "بلوک نادرین", "Block of Netherite", MISC,
                     [["netherite-ingot", "netherite-ingot", "netherite-ingot"],
                      ["netherite-ingot", "netherite-ingot", "netherite-ingot"],
                      ["netherite-ingot", "netherite-ingot", "netherite-ingot"]],
                     "netherite-block", 1, output_type="block",
                     aliases=["بلوک نادرین", "netherite block", "block of netherite"],
                     icon="⬛",
                     description="بلوک نادرین: ۹ netherite-ingot → ۱. تزئینی."))

NEW_RECIPES.append(R("coal-block", "بلوک زغال", "Block of Coal", MISC,
                     [["coal", "coal", "coal"],
                      ["coal", "coal", "coal"],
                      ["coal", "coal", "coal"]],
                     "coal-block", 1, output_type="block",
                     aliases=["بلوک زغال", "coal block", "block of coal"],
                     icon="⚫",
                     description="بلوک زغال: ۹ زغال → ۱. سوخت فشرده."))

NEW_RECIPES.append(R("lapis-block", "بلوک لاپیس", "Block of Lapis Lazuli", MISC,
                     [["lapis-lazuli", "lapis-lazuli", "lapis-lazuli"],
                      ["lapis-lazuli", "lapis-lazuli", "lapis-lazuli"],
                      ["lapis-lazuli", "lapis-lazuli", "lapis-lazuli"]],
                     "lapis-block", 1, output_type="block",
                     aliases=["بلوک لاپیس", "lapis block", "block of lapis lazuli"],
                     icon="🔵",
                     description="بلوک لاپیس: ۹ lapis lazuli → ۱. تزئینی."))

NEW_RECIPES.append(R("slime-block", "بلوک اسلایم", "Slime Block", MISC,
                     [["slimeball", "slimeball", "slimeball"],
                      ["slimeball", "slimeball", "slimeball"],
                      ["slimeball", "slimeball", "slimeball"]],
                     "slime-block", 1, output_type="block",
                     aliases=["بلوک اسلایم", "slime block"],
                     icon="🟢",
                     description="بلوک اسلایم: ۹ slimeball → ۱. چسبناک و کشسان."))

NEW_RECIPES.append(R("hay-block", "بلوک یونجه", "Hay Bale", MISC,
                     [["wheat", "wheat", "wheat"],
                      ["wheat", "wheat", "wheat"],
                      ["wheat", "wheat", "wheat"]],
                     "hay-block", 1, output_type="block",
                     aliases=["بلوک یونجه", "hay block", "hay bale"],
                     icon="🌾",
                     description="بلوک یونجه: ۹ گندم → ۱. کاهش آسیب افت."))

NEW_RECIPES.append(R("snow-block", "بلوک برف", "Snow Block", MISC,
                     [[None, None, None],
                      ["snowball", "snowball", None],
                      ["snowball", "snowball", None]],
                     "snow-block", 1, output_type="block",
                     aliases=["بلوک برف", "snow block"],
                     icon="❄️",
                     description="بلوک برف: ۴ گلوله‌ی برف → ۱."))

NEW_RECIPES.append(R("bone-block", "بلوک استخوان", "Block of Bone", MISC,
                     [["bone-meal", "bone-meal", "bone-meal"],
                      ["bone-meal", "bone-meal", "bone-meal"],
                      ["bone-meal", "bone-meal", "bone-meal"]],
                     "bone-block", 1, output_type="block",
                     aliases=["بلوک استخوان", "bone block"],
                     icon="🦴",
                     description="بلوک استخوان: ۹ bone-meal → ۱. تزئینی."))

NEW_RECIPES.append(R("crying-obsidian", "ابسیدین گریان", "Crying Obsidian", MISC,
                     [[None, None, None],
                      [None, None, None],
                      ["obsidian", "crying-obsidian-item", None]],
                     "crying-obsidian", 1, output_type="block",
                     aliases=["ابسیدین گریان", "crying obsidian"],
                     icon="🟣",
                     shapeless=True,
                     description="ابسیدین گریان: ابسیدین + گله استخوان. برای لنگر تولد."))


# ═════════════════════════════════════════════════════════════════════════
# Load existing 33, add category field, append new recipes
# ═════════════════════════════════════════════════════════════════════════

# Manual category assignment for the 33 existing recipes
EXISTING_CATEGORIES = {
    "stick": MISC,
    "crafting-table": MISC,
    "torch": MISC,
    "chest": MISC,
    "furnace": MISC,
    "wooden-pickaxe": COMBAT,
    "stone-pickaxe": COMBAT,
    "iron-pickaxe": COMBAT,
    "diamond-pickaxe": COMBAT,
    "wooden-sword": COMBAT,
    "stone-sword": COMBAT,
    "iron-sword": COMBAT,
    "diamond-sword": COMBAT,
    "wooden-axe": COMBAT,
    "stone-axe": COMBAT,
    "iron-axe": COMBAT,
    "diamond-axe": COMBAT,
    "wooden-shovel": COMBAT,
    "iron-shovel": COMBAT,
    "bow": COMBAT,
    "arrow": COMBAT,
    "shield": COMBAT,
    "tnt": COMBAT,
    "ladder": BUILDING,
    "boat": MISC,
    "bed": MISC,
    "bread": FOOD,
    "bucket": MISC,
    "bookshelf": BUILDING,
    "iron-helmet": COMBAT,
    "iron-chestplate": COMBAT,
    "iron-leggings": COMBAT,
    "iron-boots": COMBAT,
}

# Emoji icons for existing 33 (for output fallback)
EXISTING_ICONS = {
    "stick": "🪵",
    "crafting-table": "🛠️",
    "torch": "🔦",
    "chest": "📦",
    "furnace": "🔥",
    "wooden-pickaxe": "⛏️",
    "stone-pickaxe": "⛏️",
    "iron-pickaxe": "⛏️",
    "diamond-pickaxe": "⛏️",
    "wooden-sword": "🗡️",
    "stone-sword": "🗡️",
    "iron-sword": "🗡️",
    "diamond-sword": "🗡️",
    "wooden-axe": "🪓",
    "stone-axe": "🪓",
    "iron-axe": "🪓",
    "diamond-axe": "🪓",
    "wooden-shovel": "🪏",
    "iron-shovel": "🪏",
    "bow": "🏹",
    "arrow": "🏹",
    "shield": "🛡️",
    "tnt": "🧨",
    "ladder": "🪜",
    "boat": "🚣",
    "bed": "🛏️",
    "bread": "🍞",
    "bucket": "🪣",
    "bookshelf": "📚",
    "iron-helmet": "🪖",
    "iron-chestplate": "🦺",
    "iron-leggings": "👖",
    "iron-boots": "👢",
}


def main():
    # Load existing
    with open(EXISTING_PATH, "r", encoding="utf-8") as f:
        existing = json.load(f)

    existing_recipes = existing.get("recipes", [])
    print(f"Loaded {len(existing_recipes)} existing recipes.")

    # Annotate existing 33 with category + icon (keep all other fields)
    for r in existing_recipes:
        rid = r.get("id")
        if rid in EXISTING_CATEGORIES:
            r["category"] = EXISTING_CATEGORIES[rid]
        else:
            r["category"] = MISC  # default
        if "icon" not in r and rid in EXISTING_ICONS:
            r["icon"] = EXISTING_ICONS[rid]

    # Sanity check: ensure no duplicate IDs between existing and new
    existing_ids = {r["id"] for r in existing_recipes}
    new_ids = [r["id"] for r in NEW_RECIPES]
    dupes = [rid for rid in new_ids if rid in existing_ids]
    if dupes:
        print(f"WARNING: duplicate IDs (new vs existing): {dupes}")
        # filter out dupes from NEW_RECIPES
        for r in list(NEW_RECIPES):
            if r["id"] in existing_ids:
                NEW_RECIPES.remove(r)

    # Check internal duplicates in NEW_RECIPES
    seen = set()
    internal_dupes = []
    for r in NEW_RECIPES:
        if r["id"] in seen:
            internal_dupes.append(r["id"])
        seen.add(r["id"])
    if internal_dupes:
        print(f"WARNING: internal duplicate IDs in NEW_RECIPES: {internal_dupes}")

    all_recipes = existing_recipes + NEW_RECIPES
    print(f"Total recipes: {len(all_recipes)}")

    # Count by category
    cat_counts = {}
    for r in all_recipes:
        c = r.get("category", "unknown")
        cat_counts[c] = cat_counts.get(c, 0) + 1
    print(f"Category counts: {cat_counts}")

    # Build the itemIcons map — collect all item names used in any grid
    icon_map = dict(ITEM_ICONS)  # start with predefined
    for r in all_recipes:
        for row in r.get("grid", []):
            for cell in row:
                if cell and cell not in icon_map:
                    icon_map[cell] = "📦"  # generic fallback
        # also include the output item
        out_item = r.get("output", {}).get("item", "")
        if out_item and out_item not in icon_map:
            icon_map[out_item] = r.get("icon", "📦")

    # Build final JSON
    final = OrderedDict()
    final["recipes"] = all_recipes
    final["itemIcons"] = icon_map
    # Preserve any other top-level keys from the existing file (e.g., "_meta")
    for k, v in existing.items():
        if k not in ("recipes",):
            final[k] = v

    # Write back (UTF-8, indented for readability)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {len(all_recipes)} recipes + {len(icon_map)} icon entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
