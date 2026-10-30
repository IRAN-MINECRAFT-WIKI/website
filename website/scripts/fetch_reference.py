#!/usr/bin/env python3
"""
فاز ۲ — Reference: گرفتن لیست‌های مرجع کامل از Minecraft Wiki API

این اسکریپت لیست‌های کامل بلاک‌ها، آیتم‌ها، ماب‌ها و بایوم‌های ماینکرفت رو
از minecraft.wiki API می‌گیره و در /tmp/reference.json ذخیره می‌کنه.

خروجی: /tmp/reference.json با ساختار:
{
  "blocks": ["Stone", "Dirt", ...],  # all block titles from Category:Blocks
  "items": ["Stick", "Iron Ingot", ...],  # from Category:Items
  "mobs": ["Creeper", "Zombie", ...],  # from Category:Entities (filtered to mobs)
  "biomes": ["Plains", "Desert", ...],  # from Category:Biomes
  "counts": {...}
}
"""
import json, urllib.request, time, sys

OUTPUT = '/tmp/reference.json'
HEADERS = {"User-Agent": "iran-minecraft-wiki/1.0 (github.com/IRAN-MINECRAFT-WIKI/website)"}

def fetch_category_members(category, max_pages=20):
    """Fetch all pages in a category (with pagination)."""
    all_titles = []
    cmcontinue = ''
    pages_fetched = 0
    while pages_fetched < max_pages:
        url = f"https://minecraft.wiki/api.php?action=query&list=categorymembers&cmtitle=Category:{category}&cmlimit=500&cmtype=page&format=json"
        if cmcontinue:
            url += "&cmcontinue=" + urllib.parse.quote(cmcontinue)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
        except Exception as e:
            print(f"  ! Error fetching {category}: {e}", file=sys.stderr)
            break
        pages = data.get('query', {}).get('categorymembers', [])
        all_titles.extend(p['title'] for p in pages)
        pages_fetched += 1
        cont = data.get('continue', {})
        cmcontinue = cont.get('cmcontinue', '')
        if not cmcontinue or len(pages) == 0:
            break
        time.sleep(0.3)
    return all_titles

def filter_titles(titles, skip_substrings=None, require_substrings=None):
    """Filter out disambiguation/template/file pages and April Fools/Education stuff."""
    skip_substrings = skip_substrings or []
    SKIP_PREFIXES = ('Block ', 'List of', 'Template:', 'Category:', 'File:', 'User:', 'Template talk:', 'Minecraft Wiki:')
    SKIP_EXACT = {
        'An Ant', 'Bars', 'Block', 'Block of', 'Block sprite', 'Blocks', 'Block tag',
        'Opacity/1', 'Opacity/2', 'Opacity/3', 'Opacity/4', 'Opacity/5', 'Opacity/6',
        'Opacity/7', 'Opacity/8', 'Opacity/9', 'Opacity/10', 'Opacity/11', 'Opacity/12',
        'Opacity/13', 'Opacity/14', 'Opacity/15',
        'Removed blocks', 'Technical blocks', 'Invisible blocks', 'Interactable blocks',
        'Item (disambiguation)', 'Mob (disambiguation)', 'Biome (disambiguation)',
        'Entity', 'Data values', 'Spawn egg', 'Spawn Egg',
    }
    filtered = []
    for t in titles:
        if t in SKIP_EXACT: continue
        if any(t.startswith(p) for p in SKIP_PREFIXES): continue
        if 'disambiguation' in t.lower(): continue
        if any(s in t.lower() for s in skip_substrings): continue
        if require_substrings and not any(s in t.lower() for s in require_substrings): continue
        filtered.append(t)
    return filtered

# Categories to fetch (and their filter rules)
CATEGORIES = [
    {
        'name': 'blocks',
        'wiki_cat': 'Blocks',
        'skip': ['24w14potato', 'april fools', 'potato brick', 'poisonous potato',
                 'charred baked', 'expired baked', 'baked potato brick',
                 'compressed poisonous', 'triple compressed', 'quadruple compressed',
                 'double compressed', 'copper golem statue', 'copper spleaves',
                 'copper trap', 'copper sink', 'copper lantern', 'copper chest',
                 'copper torch', 'copper bars', 'copper chain',
                 'golden chest', 'golden dandelion',
                 'taterstone', 'potone', 'sulfur', 'cinnabar',
                 'peelgrass', 'corrupted peelgrass', 'terre de pomme',
                 'funky portal', 'how did we get here', 'swaggiest',
                 'big brain', 'brittle ice', 'cheese', 'floatater', 'floatato',
                 'gravtater', 'powerful potato', 'vicious potato', 'potent sulfur',
                 'bush', 'shrub', 'cactus flower',
                 'paeonia', 'etho slab', 'seamless stone slab',
                 'locked chest', 'deprecated', 'gear', 'six-sided piston',
                 'infinite lava', 'infinite water', 'attached melon', 'attached pumpkin',
                 'melon stem', 'pumpkin stem', 'frosted ice', 'cave air', 'void air',
                 'grass carried', 'leaves carried', 'wool slab', 'wool stairs',
                 'wooden slab', 'wooden stairs', 'wooden fence', 'wooden pressure plate',
                 'wooden trapdoor', 'wooden door', 'wooden button',
                 'firefly bush',  # actually real
                 ],
    },
    {
        'name': 'items',
        'wiki_cat': 'Items',
        'skip': ['24w14potato', 'april fools', 'potato',
                 'charred', 'expired', 'baked potato brick',
                 'compressed poisonous', 'triple compressed', 'quadruple compressed',
                 'double compressed',
                 'copper golem', 'copper spleaves', 'copper trap', 'copper sink',
                 'copper lantern', 'copper chest', 'copper torch', 'copper bars',
                 'copper chain', 'golden chest', 'golden dandelion',
                 'taterstone', 'potone', 'sulfur', 'cinnabar',
                 'peelgrass', 'corrupted peelgrass', 'terre de pomme',
                 'funky portal', 'how did we get here', 'swaggiest',
                 'big brain', 'brittle ice', 'cheese', 'floatater', 'floatato',
                 'gravtater', 'powerful potato', 'vicious potato', 'potent sulfur',
                 'spawn egg',  # we don't list these
                 ],
    },
    {
        'name': 'mobs',
        'wiki_cat': 'Entities',
        'skip': ['24w14potato', 'april fools', 'potato', 'poisonous potato',
                 'copper golem', 'glare', 'mob (disambiguation)',
                 'tnt', 'falling block', 'eye of ender', 'experience orb',
                 'item (entity)', 'item frame (entity)', 'fishing bobber',
                 'primed tnt', 'snow golem ', 'lead knot',
                 'lightning bolt', 'fishing hook', 'arrow (entity)',
                 'spectral arrow (entity)', 'tipped arrow (entity)',
                 'egg (entity)', 'ender pearl (entity)', 'snowball (entity)',
                 'fireball (entity)', 'small fireball (entity)',
                 'wither skull (entity)', 'dragon fireball (entity)',
                 'llama spit (entity)', 'evoker fangs (entity)',
                 'shulker bullet (entity)', 'spit (entity)',
                 'fishing bobber (entity)', 'bobber', 'potion (entity)',
                 'bottle of enchanting (entity)', 'firework rocket (entity)',
                 'tnt (entity)', 'falling block (entity)', 'moving piston',
                 'area effect cloud', 'leash knot', 'painting (entity)',
                 'armor stand (entity)', 'item display', 'block display',
                 'text display', 'interaction', 'marker',
                 ],
    },
    {
        'name': 'biomes',
        'wiki_cat': 'Biomes',
        'skip': ['24w14potato', 'april fools', 'potato',
                 'peelgrass', 'terre de pomme',
                 ],
    },
]

reference = {}
print("=== Phase 2: Reference lists from minecraft.wiki ===\n")

for cat in CATEGORIES:
    print(f"--- {cat['name']} (Category:{cat['wiki_cat']}) ---")
    titles = fetch_category_members(cat['wiki_cat'])
    print(f"  Raw: {len(titles)} pages")
    filtered = filter_titles(titles, skip_substrings=cat['skip'])
    print(f"  After filtering: {len(filtered)} pages")
    reference[cat['name']] = filtered
    print(f"  Sample (first 10): {filtered[:10]}")
    print()

reference['counts'] = {k: len(v) for k, v in reference.items() if isinstance(v, list)}

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(reference, f, ensure_ascii=False, indent=2)

print(f"\n=== REFERENCE SAVED ===")
print(f"File: {OUTPUT}")
print(f"\nSummary:")
for k, v in reference['counts'].items():
    print(f"  {k}: {v}")
