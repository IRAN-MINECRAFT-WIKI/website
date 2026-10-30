#!/usr/bin/env python3
"""
فاز ۱ — Inventory: استخراج کامل همه‌ی داده‌های سایت
این اسکریپت همه‌ی بلاک‌ها، ماب‌ها، آیتم‌های لیست‌شده در صفحه‌ی items،
مقالات ویکی، نسخه‌ها، رسپی‌ها، و سیدها رو از repo استخراج می‌کنه
و به‌صورت ساختاریافته در /tmp/inventory.json ذخیره می‌کنه.

خروجی: /tmp/inventory.json با ساختار:
{
  "blocks": [{id, nameEn, nameFa, category}, ...],
  "mobs": [{id, nameEn, nameFa, category}, ...],
  "items": [{id, nameFa, category}, ...],  # extracted from items page
  "wiki_articles": [{id, title, topic}, ...],
  "versions": [{id, version, name, platform}, ...],
  "recipes": [{id, nameFa, nameEn}, ...],
  "mods": [{id, name, slug}, ...],
  "seeds": [{id, title}, ...],
  "counts": {blocks, mobs, items, wiki, versions, recipes, mods, seeds}
}
"""
import json, os, re, sys

ROOT = '/home/z/work/imc-website/website'
OUTPUT = '/tmp/inventory.json'

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  ! Error loading {path}: {e}", file=sys.stderr)
        return None

# ═══ 1. BLOCKS ═══
print("=== Phase 1: Inventory ===\n--- Blocks ---")
blocks = []
blocks_dir = os.path.join(ROOT, 'src/data/blocks')
for fname in sorted(os.listdir(blocks_dir)):
    if not fname.endswith('.json') or fname == 'index.json':
        continue
    data = load_json(os.path.join(blocks_dir, fname))
    if data:
        blocks.append({
            'id': data.get('id', fname[:-5]),
            'nameEn': data.get('nameEn', ''),
            'nameFa': data.get('nameFa', ''),
            'category': data.get('category', 'unknown'),
            'hardness': data.get('hardness', 0),
            'tool': data.get('tool', 'none'),
        })
print(f"  Loaded {len(blocks)} blocks")

# Group by category
blocks_by_cat = {}
for b in blocks:
    cat = b['category']
    if cat not in blocks_by_cat:
        blocks_by_cat[cat] = []
    blocks_by_cat[cat].append(b['id'])
print(f"  Categories: {list(blocks_by_cat.keys())}")
for cat, ids in blocks_by_cat.items():
    print(f"    {cat}: {len(ids)} blocks")

# ═══ 2. MOBS ═══
print("\n--- Mobs ---")
mobs = []
mobs_dir = os.path.join(ROOT, 'src/data/mobs')
for fname in sorted(os.listdir(mobs_dir)):
    if not fname.endswith('.json') or fname == 'index.json':
        continue
    data = load_json(os.path.join(mobs_dir, fname))
    if data:
        mobs.append({
            'id': data.get('id', fname[:-5]),
            'nameEn': data.get('nameEn', ''),
            'nameFa': data.get('nameFa', ''),
            'category': data.get('category', 'unknown'),
            'health': data.get('health', 0),
        })
print(f"  Loaded {len(mobs)} mobs")

mobs_by_cat = {}
for m in mobs:
    cat = m['category']
    mobs_by_cat.setdefault(cat, []).append(m['id'])
print(f"  Categories: {list(mobs_by_cat.keys())}")
for cat, ids in mobs_by_cat.items():
    print(f"    {cat}: {len(ids)} mobs")

# ═══ 3. ITEMS (from items page) ═══
print("\n--- Items (from /wiki/items page) ---")
items = []
items_page = os.path.join(ROOT, 'src/pages/wiki/items/index.astro')
if os.path.exists(items_page):
    with open(items_page, 'r', encoding='utf-8') as f:
        content = f.read()
    # Parse the ITEM_CATEGORIES array — find each { id, nameFa, } entry
    # Pattern: { id: 'xxx', nameFa: 'yyy' }
    # Or { id: 'xxx', nameFa: 'yyy', nameEn: 'zzz' }
    pattern = re.compile(r"\{\s*id:\s*'([^']+)'\s*,\s*nameFa:\s*'([^']+)'\s*(?:,\s*nameEn:\s*'([^']*)')?\s*\}")
    # Find current category by looking at id: 'category_name'
    cat_pattern = re.compile(r"id:\s*'([a-z-]+)'\s*,\s*nameFa:\s*'([^']+)'\s*,\s*emoji:")
    current_cat = 'unknown'
    current_cat_fa = ''
    for line in content.split('\n'):
        cat_match = cat_pattern.search(line)
        if cat_match:
            current_cat = cat_match.group(1)
            current_cat_fa = cat_match.group(2)
        for m in pattern.finditer(line):
            items.append({
                'id': m.group(1),
                'nameFa': m.group(2),
                'category': current_cat,
                'categoryFa': current_cat_fa,
            })
print(f"  Loaded {len(items)} items from items page")

items_by_cat = {}
for i in items:
    items_by_cat.setdefault(i['category'], []).append(i['id'])
print(f"  Categories: {list(items_by_cat.keys())}")
for cat, ids in items_by_cat.items():
    print(f"    {cat}: {len(ids)} items")

# ═══ 4. WIKI ARTICLES ═══
print("\n--- Wiki Articles ---")
wiki_articles = []
wiki_dir = os.path.join(ROOT, 'src/content/wiki')
for fname in sorted(os.listdir(wiki_dir)):
    if not fname.endswith('.mdx'):
        continue
    with open(os.path.join(wiki_dir, fname), 'r', encoding='utf-8') as f:
        content = f.read()
    # Extract frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        title_m = re.search(r"^title:\s*'([^']*)'", fm, re.MULTILINE)
        topic_m = re.search(r"^topic:\s*'([^']*)'", fm, re.MULTILINE)
        title = title_m.group(1) if title_m else ''
        topic = topic_m.group(1) if topic_m else ''
        wiki_articles.append({
            'id': fname[:-4],  # remove .mdx
            'title': title,
            'topic': topic,
        })
print(f"  Loaded {len(wiki_articles)} wiki articles")

wiki_by_topic = {}
for a in wiki_articles:
    wiki_by_topic.setdefault(a['topic'], []).append(a['id'])
print(f"  Topics: {list(wiki_by_topic.keys())}")
for topic, ids in wiki_by_topic.items():
    print(f"    {topic}: {len(ids)} articles")

# ═══ 5. VERSIONS ═══
print("\n--- Versions ---")
versions = []
versions_data = load_json(os.path.join(ROOT, 'src/data/versions.json'))
if versions_data:
    for platform in ['java', 'bedrock']:
        for v in versions_data.get(platform, []):
            versions.append({
                'id': v.get('id', ''),
                'version': v.get('version', ''),
                'name': v.get('name', ''),
                'platform': platform,
                'releaseDate': v.get('releaseDate', ''),
            })
print(f"  Loaded {len(versions)} versions ({sum(1 for v in versions if v['platform']=='java')} Java + {sum(1 for v in versions if v['platform']=='bedrock')} Bedrock)")

# ═══ 6. RECIPES ═══
print("\n--- Recipes ---")
recipes = []
recipes_data = load_json(os.path.join(ROOT, 'src/data/crafting-recipes.json'))
if recipes_data:
    for r in recipes_data.get('recipes', []):
        recipes.append({
            'id': r.get('id', ''),
            'nameFa': r.get('nameFa', ''),
            'nameEn': r.get('nameEn', ''),
            'category': r.get('category', ''),
        })
print(f"  Loaded {len(recipes)} recipes")

recipes_by_cat = {}
for r in recipes:
    recipes_by_cat.setdefault(r['category'], []).append(r['id'])
print(f"  Categories: {list(recipes_by_cat.keys())}")
for cat, ids in recipes_by_cat.items():
    print(f"    {cat}: {len(ids)} recipes")

# ═══ 7. MODS ═══
print("\n--- Mods ---")
mods = []
mods_data = load_json(os.path.join(ROOT, 'src/data/mods.json'))
if mods_data:
    if isinstance(mods_data, list):
        for m in mods_data:
            mods.append({
                'id': m.get('id', m.get('slug', '')),
                'name': m.get('name', m.get('nameFa', '')),
                'slug': m.get('slug', m.get('id', '')),
                'category': m.get('category', ''),
            })
    elif isinstance(mods_data, dict) and 'mods' in mods_data:
        for m in mods_data['mods']:
            mods.append({
                'id': m.get('id', m.get('slug', '')),
                'name': m.get('name', m.get('nameFa', '')),
                'slug': m.get('slug', m.get('id', '')),
                'category': m.get('category', ''),
            })
print(f"  Loaded {len(mods)} mods")

# ═══ 8. SEEDS ═══
print("\n--- Seeds ---")
seeds = []
seeds_data = load_json(os.path.join(ROOT, 'src/data/seeds.json'))
if seeds_data:
    if isinstance(seeds_data, list):
        for s in seeds_data:
            seeds.append({
                'id': s.get('id', ''),
                'title': s.get('title', s.get('nameFa', '')),
            })
    elif isinstance(seeds_data, dict) and 'seeds' in seeds_data:
        for s in seeds_data['seeds']:
            seeds.append({
                'id': s.get('id', ''),
                'title': s.get('title', s.get('nameFa', '')),
            })
print(f"  Loaded {len(seeds)} seeds")

# ═══ FINAL INVENTORY ═══
inventory = {
    'counts': {
        'blocks': len(blocks),
        'mobs': len(mobs),
        'items': len(items),
        'wiki_articles': len(wiki_articles),
        'versions': len(versions),
        'recipes': len(recipes),
        'mods': len(mods),
        'seeds': len(seeds),
    },
    'blocks': blocks,
    'mobs': mobs,
    'items': items,
    'wiki_articles': wiki_articles,
    'versions': versions,
    'recipes': recipes,
    'mods': mods,
    'seeds': seeds,
    'blocks_by_category': blocks_by_cat,
    'mobs_by_category': mobs_by_cat,
    'items_by_category': items_by_cat,
    'wiki_by_topic': wiki_by_topic,
    'recipes_by_category': recipes_by_cat,
}

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(inventory, f, ensure_ascii=False, indent=2)

print(f"\n=== INVENTORY SAVED ===")
print(f"File: {OUTPUT}")
print(f"Total entries: {sum(inventory['counts'].values())}")
print(f"\nSummary:")
for k, v in inventory['counts'].items():
    print(f"  {k}: {v}")
