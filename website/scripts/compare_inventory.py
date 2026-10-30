#!/usr/bin/env python3
"""
فاز ۳ — Compare: مقایسه‌ی inventory و reference و تولید diff report

این اسکریپت:
1. inventory.json (از repo ما) و reference.json (از minecraft.wiki) رو بارگذاری می‌کنه
2. برای هر دسته (blocks, items, mobs, biomes):
   - عنوان‌های wiki رو به kebab-case ID تبدیل می‌کنه
   - مقایسه می‌کنه: missing (در reference ولی نه در inventory)، extra (در inventory ولی نه در reference)
3. خروجی به‌صورت JSON ساختاریافته در /tmp/diff_report.json

خروجی: /tmp/diff_report.json با ساختار:
{
  "blocks": {"missing": [...], "extra": [...], "summary": {...}},
  "items": {...},
  "mobs": {...},
  "biomes": {...},
  "totals": {...}
}
"""
import json, re

INVENTORY_PATH = '/tmp/inventory.json'
REFERENCE_PATH = '/tmp/reference.json'
OUTPUT_PATH = '/tmp/diff_report.json'

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def title_to_id(title):
    """Convert wiki title (e.g., 'Acacia Sapling') to kebab-case ID (e.g., 'acacia-sapling')."""
    s = title.lower()
    # Handle special chars
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

# Manual mapping for known mismatches (wiki title → our ID)
WIKI_TO_OUR_ID = {
    # Blocks
    'Wooden Door': 'oak-door',
    'Wooden Button': 'oak-button',
    'Wooden Pressure Plate': 'oak-pressure-plate',
    'Wooden Fence': 'oak-fence',
    'Wooden Trapdoor': 'oak-trapdoor',
    'Wooden Slab': 'oak-slab',
    'Wooden Stairs': 'oak-stairs',
    'Wooden Sign': 'oak-sign',
    'Wooden Hanging Sign': 'oak-hanging-sign',
    'Wooden Wall Sign': 'oak-wall-sign',
    'Wooden Wall Hanging Sign': 'oak-wall-hanging-sign',
    'Wall Hanging Sign': 'oak-wall-hanging-sign',
    'Hanging Sign': 'oak-hanging-sign',
    'Wall Sign': 'oak-wall-sign',
    'Sign': 'oak-sign',
    'Door': 'oak-door',
    'Fence': 'oak-fence',
    'Fence Gate': 'oak-fence-gate',
    'Trapdoor': 'oak-trapdoor',
    'Button': 'stone-button',
    'Pressure Plate': 'stone-pressure-plate',
    'Slab': 'stone-slab',
    'Stairs': 'stone-stairs',
    'Wall': 'stone-wall',
    'Leaves': 'oak-leaves',
    'Log': 'oak-log',
    'Wood': 'oak-wood',
    'Planks': 'oak-planks',
    'Sapling': 'oak-sapling',
    'Wool': 'white-wool',
    'Bed': 'white-bed',
    'Banner': 'white-banner',
    'Carpet': 'white-carpet',
    'Concrete': 'white-concrete',
    'Concrete Powder': 'white-concrete-powder',
    'Glazed Terracotta': 'white-glazed-terracotta',
    'Terracotta': 'terracotta',
    'Stained Glass': 'white-stained-glass',
    'Stained Glass Pane': 'white-stained-glass-pane',
    'Glass Pane': 'glass-pane',
    'Head': 'zombie-head',
    'Coral': 'tube-coral',
    'Coral Block': 'tube-coral-block',
    'Coral Fan': 'tube-coral-fan',
    'Dead Coral': 'dead-tube-coral',
    'Dead Coral Block': 'dead-tube-coral-block',
    'Dead Coral Fan': 'dead-tube-coral-fan',
    'Cobblestone Slab': 'cobblestone-slab',
    'Cobblestone Stairs': 'cobblestone-stairs',
    'Cobblestone Wall': 'cobblestone-wall',
    'Stone Bricks': 'stone-bricks',
    'Mossy Stone Bricks': 'mossy-stone-bricks',
    'Cracked Stone Bricks': 'cracked-stone-bricks',
    'Chiseled Stone Bricks': 'chiseled-stone-bricks',
    'Smooth Stone Bricks': 'stone-bricks',
    'End Portal (block)': 'end-portal',
    'End Gateway (block)': 'end-gateway',
    'Nether Portal (block)': 'nether-portal',
    'Light (block)': 'light-block',
    'Fluid': 'water',
    'Flower': 'dandelion',
    'Mushroom Block': 'mushroom-stem',
    'Monster Spawner': 'spawner',
    'Infested Block': 'infested-stone',
    'Mushroom': 'brown-mushroom',
    'Lily Pad': 'lily-pad',
    'Lily of the Valley': 'lily-of-the-valley',
    'Wither Rose': 'wither-rose',
    # Mobs
    'Entity': None,  # skip
    'Animal': None,
    'Aquatic': None,
    'Item (entity)': None,
    'Item Frame (entity)': None,
    'Fishing Bobber': None,
    'Anvil': None,  # this is the block, not a mob
    'Agent': None,  # Education
    'Alex': None,  # player skin
    'Ari': None,
    'Efe': None,
    'Kai': None,
    'Makena': None,
    'Noor': None,
    'Steve': None,
    'Sunny': None,
    'Zuri': None,
    'Player': None,
    'Armor Stand': None,  # already a block
    'Ankle Monitor': None,  # Education
    'Camera': None,  # Education
    'NPC': None,
    '3D': None,  # April Fools
    'A Very Fine Item': None,  # April Fools
    'Amber Gem': None,  # April Fools
}

def wiki_id_to_our_id(wiki_id):
    """Map a wiki-derived ID to our ID using the manual mapping, or return the wiki ID."""
    # Try direct mapping first
    if wiki_id in WIKI_TO_OUR_ID:
        return WIKI_TO_OUR_ID[wiki_id]
    return wiki_id

def title_to_our_id(title):
    """Convert wiki title to our ID with mapping."""
    # Try direct mapping by title
    if title in WIKI_TO_OUR_ID:
        return WIKI_TO_OUR_ID[title]
    # Convert to kebab-case
    return title_to_id(title)

inventory = load_json(INVENTORY_PATH)
reference = load_json(REFERENCE_PATH)

# Build our ID sets
our_blocks = set(b['id'] for b in inventory['blocks'])
our_mobs = set(m['id'] for m in inventory['mobs'])
our_items = set(i['id'] for i in inventory['items'])

# Build wiki ID sets (with mapping)
def build_wiki_id_set(titles):
    """Convert wiki titles to our ID format, returning set + lookup."""
    result = set()
    title_to_id_map = {}
    for title in titles:
        oid = title_to_our_id(title)
        if oid is None: continue  # skip
        result.add(oid)
        title_to_id_map[oid] = title
    return result, title_to_id_map

wiki_blocks, wiki_blocks_titles = build_wiki_id_set(reference['blocks'])
wiki_items, wiki_items_titles = build_wiki_id_set(reference['items'])
wiki_mobs, wiki_mobs_titles = build_wiki_id_set(reference['mobs'])

# Compute diffs
def compute_diff(our_set, wiki_set, wiki_titles_map):
    missing = sorted(wiki_set - our_set)
    extra = sorted(our_set - wiki_set)
    return {
        'missing': [{'id': m, 'wiki_title': wiki_titles_map.get(m, m)} for m in missing],
        'extra': list(extra),
        'missing_count': len(missing),
        'extra_count': len(extra),
        'our_count': len(our_set),
        'wiki_count': len(wiki_set),
        'common_count': len(our_set & wiki_set),
    }

diff = {
    'blocks': compute_diff(our_blocks, wiki_blocks, wiki_blocks_titles),
    'items': compute_diff(our_items, wiki_items, wiki_items_titles),
    'mobs': compute_diff(our_mobs, wiki_mobs, wiki_mobs_titles),
}

diff['totals'] = {
    'total_missing': sum(d['missing_count'] for d in diff.values()),
    'total_extra': sum(d['extra_count'] for d in diff.values()),
    'categories_with_gaps': sum(1 for d in diff.values() if d['missing_count'] > 0),
}

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(diff, f, ensure_ascii=False, indent=2)

# Print summary
print("=== Phase 3: Diff Report ===\n")
for cat_name, cat_diff in diff.items():
    if cat_name == 'totals': continue
    print(f"--- {cat_name.upper()} ---")
    print(f"  Our count:    {cat_diff['our_count']}")
    print(f"  Wiki count:   {cat_diff['wiki_count']}")
    print(f"  Common:       {cat_diff['common_count']}")
    print(f"  Missing:      {cat_diff['missing_count']}")
    print(f"  Extra:        {cat_diff['extra_count']}")
    if cat_diff['missing_count'] > 0:
        print(f"  First 15 missing:")
        for m in cat_diff['missing'][:15]:
            print(f"    - {m['id']} ({m['wiki_title']})")
    print()

print(f"\n=== TOTALS ===")
print(f"Total missing: {diff['totals']['total_missing']}")
print(f"Total extra: {diff['totals']['total_extra']}")
print(f"Categories with gaps: {diff['totals']['categories_with_gaps']}")
print(f"\nFull report saved to: {OUTPUT_PATH}")
