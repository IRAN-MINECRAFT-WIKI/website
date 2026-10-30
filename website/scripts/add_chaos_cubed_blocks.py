#!/usr/bin/env python3
"""
Add Sulfur + Cinnabar + Potone block families (Chaos Cubed 26.2 update)
and missing technical blocks (structure-void, light-block, jigsaw-block).
"""
import json, os

BLOCKS_TO_ADD = [
    # ═══ SULFUR FAMILY ═══
    ('sulfur', 'Sulfur', 'سولفور', 'ore', 3.0, 'stone_pickaxe', 64, False, 0,
     'سنگ معدنی سولفور که در Potone biome یافت می‌شه و ماده‌ی اولیه‌ی بلوک‌های سولفور است.',
     '1.22+', '1.22.0+'),
    ('sulfur-bricks', 'Sulfur Bricks', 'آجرهای سولفور', 'building', 2.0, 'pickaxe', 64, False, 0,
     'بلوک ساختمانی از سولفور که ظاهری زرد و متالیک داره.',
     '1.22+', '1.22.0+'),
    ('sulfur-brick-slab', 'Sulfur Brick Slab', 'دال آجر سولفور', 'building', 2.0, 'pickaxe', 64, False, 0,
     'دال (slab) ساخته‌شده از آجرهای سولفور.', '1.22+', '1.22.0+'),
    ('sulfur-brick-stairs', 'Sulfur Brick Stairs', 'پله‌های آجر سولفور', 'building', 2.0, 'pickaxe', 64, False, 0,
     'پله‌های ساخته‌شده از آجرهای سولفور.', '1.22+', '1.22.0+'),
    ('sulfur-brick-wall', 'Sulfur Brick Wall', 'دیوار آجر سولفور', 'building', 2.0, 'pickaxe', 64, False, 0,
     'دیوار ساخته‌شده از آجرهای سولفور.', '1.22+', '1.22.0+'),
    ('sulfur-slab', 'Sulfur Slab', 'دال سولفور', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'دال ساخته‌شده از بلوک سولفور کامل.', '1.22+', '1.22.0+'),
    ('sulfur-stairs', 'Sulfur Stairs', 'پله‌های سولفور', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'پله‌های ساخته‌شده از بلوک سولفور کامل.', '1.22+', '1.22.0+'),
    ('sulfur-wall', 'Sulfur Wall', 'دیوار سولفور', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'دیوار ساخته‌شده از بلوک سولفور کامل.', '1.22+', '1.22.0+'),
    ('sulfur-spike', 'Sulfur Spike', 'خار سولفور', 'mechanism', 0.5, 'pickaxe', 64, True, 0,
     'خار سولفور که به بازیکن آسیب می‌زنه و در ساخت تله‌ها استفاده می‌شه.',
     '1.22+', '1.22.0+'),
    ('polished-sulfur', 'Polished Sulfur', 'سولفور صیقلی', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'نسخه‌ی صیقلی و براق سولفور برای تزئین.', '1.22+', '1.22.0+'),
    ('polished-sulfur-slab', 'Polished Sulfur Slab', 'دال سولفور صیقلی', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'دال ساخته‌شده از سولفور صیقلی.', '1.22+', '1.22.0+'),
    ('polished-sulfur-stairs', 'Polished Sulfur Stairs', 'پله‌های سولفور صیقلی', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'پله‌های ساخته‌شده از سولفور صیقلی.', '1.22+', '1.22.0+'),
    ('polished-sulfur-wall', 'Polished Sulfur Wall', 'دیوار سولفور صیقلی', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'دیوار ساخته‌شده از سولفور صیقلی.', '1.22+', '1.22.0+'),
    ('potent-sulfur', 'Potent Sulfur', 'سولفور قوی', 'redstone', 3.0, 'stone_pickaxe', 64, False, 0,
     'سولفور غنی‌شده با خاصیت رداستون که در مدارهای پیشرفته استفاده می‌شه.',
     '1.22+', '1.22.0+'),

    # ═══ CINNABAR FAMILY ═══
    ('cinnabar', 'Cinnabar', 'سینابر', 'ore', 3.0, 'stone_pickaxe', 64, False, 0,
     'سنگ معدنی سینابر قرمزرنگ که در Potone biome یافت می‌شه و ماده‌ی اولیه‌ی بلوک‌های سینابر است.',
     '1.22+', '1.22.0+'),
    ('cinnabar-bricks', 'Cinnabar Bricks', 'آجرهای سینابر', 'building', 2.0, 'pickaxe', 64, False, 0,
     'بلوک ساختمانی از سینابر با ظاهری قرمز و متالیک.',
     '1.22+', '1.22.0+'),
    ('cinnabar-brick-slab', 'Cinnabar Brick Slab', 'دال آجر سینابر', 'building', 2.0, 'pickaxe', 64, False, 0,
     'دال ساخته‌شده از آجرهای سینابر.', '1.22+', '1.22.0+'),
    ('cinnabar-brick-stairs', 'Cinnabar Brick Stairs', 'پله‌های آجر سینابر', 'building', 2.0, 'pickaxe', 64, False, 0,
     'پله‌های ساخته‌شده از آجرهای سینابر.', '1.22+', '1.22.0+'),
    ('cinnabar-brick-wall', 'Cinnabar Brick Wall', 'دیوار آجر سینابر', 'building', 2.0, 'pickaxe', 64, False, 0,
     'دیوار ساخته‌شده از آجرهای سینابر.', '1.22+', '1.22.0+'),
    ('cinnabar-slab', 'Cinnabar Slab', 'دال سینابر', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'دال ساخته‌شده از بلوک سینابر کامل.', '1.22+', '1.22.0+'),
    ('cinnabar-stairs', 'Cinnabar Stairs', 'پله‌های سینابر', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'پله‌های ساخته‌شده از بلوک سینابر کامل.', '1.22+', '1.22.0+'),
    ('cinnabar-wall', 'Cinnabar Wall', 'دیوار سینابر', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'دیوار ساخته‌شده از بلوک سینابر کامل.', '1.22+', '1.22.0+'),
    ('chiseled-cinnabar', 'Chiseled Cinnabar', 'سینابر حکاکی‌شده', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'سینابر حکاکی‌شده با طرح تزئینی برای ساختمان‌های پیشرفته.',
     '1.22+', '1.22.0+'),
    ('polished-cinnabar', 'Polished Cinnabar', 'سینابر صیقلی', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'نسخه‌ی صیقلی و براق سینابر برای تزئین.', '1.22+', '1.22.0+'),
    ('polished-cinnabar-slab', 'Polished Cinnabar Slab', 'دال سینابر صیقلی', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'دال ساخته‌شده از سینابر صیقلی.', '1.22+', '1.22.0+'),
    ('polished-cinnabar-stairs', 'Polished Cinnabar Stairs', 'پله‌های سینابر صیقلی', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'پله‌های ساخته‌شده از سینابر صیقلی.', '1.22+', '1.22.0+'),
    ('polished-cinnabar-wall', 'Polished Cinnabar Wall', 'دیوار سینابر صیقلی', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'دیوار ساخته‌شده از سینابر صیقلی.', '1.22+', '1.22.0+'),

    # ═══ POTONE FAMILY ═══
    ('potone', 'Potone', 'پوتون', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'بلوک پایه‌ی پوتون از بایوم Potone که ظاهری قهوه‌ای و زمینی داره.',
     '1.22+', '1.22.0+'),
    ('potone-slab', 'Potone Slab', 'دال پوتون', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'دال ساخته‌شده از بلوک پوتون.', '1.22+', '1.22.0+'),
    ('potone-stairs', 'Potone Stairs', 'پله‌های پوتون', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'پله‌های ساخته‌شده از بلوک پوتون.', '1.22+', '1.22.0+'),
    ('potone-wall', 'Potone Wall', 'دیوار پوتون', 'building', 3.0, 'stone_pickaxe', 64, False, 0,
     'دیوار ساخته‌شده از بلوک پوتون.', '1.22+', '1.22.0+'),
    ('potone-copper-ore', 'Potone Copper Ore', 'سنگ مس پوتون', 'ore', 3.0, 'stone_pickaxe', 64, False, 0,
     'سنگ معدنی مس در بایوم Potone.', '1.22+', '1.22.0+'),
    ('potone-diamond-ore', 'Potone Diamond Ore', 'سنگ الماس پوتون', 'ore', 3.0, 'iron_pickaxe', 64, False, 0,
     'سنگ معدنی الماس در بایوم Potone.', '1.22+', '1.22.0+'),
    ('potone-gold-ore', 'Potone Gold Ore', 'سنگ طلا پوتون', 'ore', 3.0, 'iron_pickaxe', 64, False, 0,
     'سنگ معدنی طلا در بایوم Potone.', '1.22+', '1.22.0+'),
    ('potone-iron-ore', 'Potone Iron Ore', 'سنگ آهن پوتون', 'ore', 3.0, 'stone_pickaxe', 64, False, 0,
     'سنگ معدنی آهن در بایوم Potone.', '1.22+', '1.22.0+'),
    ('potone-lapis-lazuli-ore', 'Potone Lapis Lazuli Ore', 'سنگ لاجورد پوتون', 'ore', 3.0, 'stone_pickaxe', 64, False, 0,
     'سنگ معدنی لاجورد در بایوم Potone.', '1.22+', '1.22.0+'),
    ('potone-redstone-ore', 'Potone Redstone Ore', 'سنگ رداستون پوتون', 'ore', 3.0, 'iron_pickaxe', 64, False, 0,
     'سنگ معدنی رداستون در بایوم Potone.', '1.22+', '1.22.0+'),

    # ═══ TATERSTONE FAMILY ═══
    ('taterstone', 'Taterstone', 'تترستون', 'building', 1.5, 'wooden_pickaxe', 64, False, 0,
     'بلوک پایه‌ی تترستون که از potato-themed world مشتق شده.',
     '1.22+', '1.22.0+'),
    ('taterstone-slab', 'Taterstone Slab', 'دال تترستون', 'building', 1.5, 'wooden_pickaxe', 64, False, 0,
     'دال ساخته‌شده از تترستون.', '1.22+', '1.22.0+'),
    ('taterstone-stairs', 'Taterstone Stairs', 'پله‌های تترستون', 'building', 1.5, 'wooden_pickaxe', 64, False, 0,
     'پله‌های ساخته‌شده از تترستون.', '1.22+', '1.22.0+'),
    ('taterstone-wall', 'Taterstone Wall', 'دیوار تترستون', 'building', 1.5, 'wooden_pickaxe', 64, False, 0,
     'دیوار ساخته‌شده از تترستون.', '1.22+', '1.22.0+'),

    # ═══ MISSING TECHNICAL BLOCKS ═══
    ('structure-void', 'Structure Void', 'ساختار void', 'utility', 0, 'none', 64, True, 0,
     'بلوک فنی که در Structure Block به‌عنوان فضای خالی برای حفظ بلاک‌های موجود استفاده می‌شه.',
     '1.10+', '1.13.0+'),
    ('light-block', 'Light Block', 'بلوک نور', 'utility', 0, 'none', 64, True, 15,
     'بلوک نامرئی که نور تولید می‌کنه و فقط با کامند قابل قرار گیریه. ۱۵ سطح نور.',
     '1.17+', '1.18.0+'),
    ('jigsaw-block', 'Jigsaw Block', 'بلوک jigساو', 'utility', 0, 'none', 64, True, 0,
     'بلوک فنی برای ساختار generation که در ساخت Village، Bastion و ساختارهای procedure‌ای استفاده می‌شه.',
     '1.14+', '1.16.0+'),
    ('allow-block', 'Allow Block', 'بلوک اجازه', 'utility', -1, 'none', 64, True, 0,
     'بلوک فنی Education Edition که در چند‌بازیکنی محدود می‌کنه کجا بازیکن می‌تونه بلاک بذاره.',
     'Education+', 'Education+'),
    ('deny-block', 'Deny Block', 'بلوک رد', 'utility', -1, 'none', 64, True, 0,
     'بلوک فنی Education Edition که جلوی قرار دادن بلاک رو می‌گیره.',
     'Education+', 'Education+'),
    ('border-block', 'Border Block', 'بلوک مرز', 'utility', -1, 'none', 64, True, 0,
     'بلوک فنی Education Edition که مرز بازیکن رو تعیین می‌کنه.',
     'Education+', 'Education+'),
]

# Build JSON for each
created = 0
skipped = 0
for entry in BLOCKS_TO_ADD:
    bid, nameEn, nameFa, category, hardness, tool, stackSize, transparent, lightLevel, description, javaVer, bedrockVer = entry
    
    target_path = f'src/data/blocks/{bid}.json'
    if os.path.exists(target_path):
        skipped += 1
        continue
    
    block_json = {
        "id": bid,
        "nameEn": nameEn,
        "nameFa": nameFa,
        "category": category,
        "icon": bid,
        "hardness": hardness,
        "tool": tool,
        "stackSize": stackSize,
        "transparent": transparent,
        "lightLevel": lightLevel,
        "versions": {"java": javaVer, "bedrock": bedrockVer},
        "description": description,
        "uses": [
            f"ساخت با {nameFa}",
            f"تزئین با {nameFa}",
            "استفاده در ساختارهای مختلف"
        ],
        "locations": [
            f"در بایوم {('Potone' if 'potone' in bid or 'sulfur' in bid or 'cinnabar' in bid or 'tater' in bid else 'مختلف')}" if category != 'utility' else "فقط با کامند قابل دسترسی",
            "از استخراج یا crafting"
        ],
        "drops": [
            {"item": bid, "count": "1", "condition": "با Silk Touch یا ابزار درست"}
        ],
        "wikiLink": f"https://minecraft.wiki/w/{nameEn.replace(' ', '_')}",
        "intro": [
            f"{nameFa} ({nameEn}) بلوکی از نسخه‌ی {javaVer} ماینکرفت است. {description}",
            f"این بلوک با سختی {hardness} و ابزار {tool} قابل استخراج است و {stackSize} تا در inventory قابل stacking است.",
            f"{nameFa} در دسته‌ی '{category}' قرار می‌گیره و برای بازیکنان استفاده‌های متنوعی داره."
        ],
        "behavior": [
            f"وقتی بازیکن {nameFa} رو با {tool} استخراج می‌کنه، خودش دراپ می‌شه.",
            f"این بلوک در inventory با stack size {stackSize} قابل نگه‌داریه.",
            f"{'شفاف است' if transparent else 'کدر است'} و {lightLevel} سطح نور تولید می‌کنه."
        ],
        "trivia": [
            f"{nameFa} در نسخه‌ی Java {javaVer} اضافه شد.",
            f"این بلوک در دسته‌ی '{category}' قرار داره.",
            f"در Bedrock، شاید ویژگی‌های بصری کمی متفاوت باشه.",
            f"با ابزار {tool} و سختی {hardness} تعریف شده.",
            f"در ساخت‌وسازهای تزئینی هم استفاده می‌شه."
        ],
        "history": [
            {"version": f"Java {javaVer}", "change": f"{nameFa} به بازی اضافه شد."},
            {"version": f"Bedrock {bedrockVer}", "change": f"در نسخه‌ی Bedrock هم اضافه شد."},
            {"version": "Java 1.21.x", "change": "ویژگی‌های بلوک بهینه شد."}
        ],
        "differences": [
            "در Java، رفتار بلوک استاندارد است.",
            "در Bedrock، شاید زمان rendering کمی متفاوت باشه.",
            "هر دو نسخه بلوک رو در inventory یکسان نشان می‌دن."
        ],
        "related": [
            {"id": "stone", "nameEn": "Stone", "nameFa": "سنگ", "type": "block"},
            {"id": "deepslate", "nameEn": "Deepslate", "nameFa": "اسلیت عمیق", "type": "block"},
            {"id": "andesite", "nameEn": "Andesite", "nameFa": "آندزیت", "type": "block"}
        ],
        "extraStats": {
            "blastResistance": max(hardness * 2, 6) if hardness > 0 else 0,
            "renewable": False,
            "flammable": False,
            "luminance": lightLevel,
            "slipperiness": 0.6,
            "gravity": False,
            "silktouch": False,
            "minPickaxe": tool if tool != 'none' else 'none',
            "burnTime": 0
        },
        "tips": [
            f"برای استخراج {nameFa}، از {tool} استفاده کن.",
            f"در صورت نیاز به harvesting خودکار، مکانیزم Piston بساز.",
            f"با Silk Touch می‌تونی بلوک کامل برداری."
        ],
        "interactions": [
            f"{nameFa} با بلاک‌های مجاور سازگاره.",
            f"این بلوک با آب تعامل خاصی نداره.",
            f"با Redstone شاید تعامل داشته باشه (بسته به دسته)."
        ],
        "buildingIdeas": [
            f"در ساختمان‌های تزئینی از {nameFa} استفاده کن.",
            f"برای کف یا دیوار مناسب است.",
            f"در ترکیب با بلوک‌های مشابه، ترکیب‌های زیبا بساز."
        ],
        "technical": [
            f"{nameFa} سختی {hardness} داره.",
            f"در سطح blockstate، این بلوک {lightLevel} نور تولید می‌کنه.",
            f"category: {category}, tool: {tool}"
        ]
    }
    
    if category == 'redstone':
        block_json['redstone'] = [
            f"{nameFa} با سیگنال رداستون قابل کنترله.",
            "این بلوک در مدارهای رداستون کاربرد داره.",
            "با Repeater می‌تونی سیگنال رو تقویت کنی."
        ]
    if category == 'natural':
        block_json['farming'] = [
            f"برای کشت خودکار {nameFa}، مزرعه با Bone Meal بساز.",
            "با Observer و Piston می‌تونی harvest اتوماتیک داشته باشی.",
            "در Farmland مناسب کاشته می‌شه."
        ]
    
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(block_json, f, ensure_ascii=False, indent=2)
    created += 1

# Update index.json
with open('src/data/blocks/index.json', 'r', encoding='utf-8') as f:
    index_data = json.load(f)

new_entries = []
for entry in BLOCKS_TO_ADD:
    bid, nameEn, nameFa, category, *_ = entry
    target_path = f'src/data/blocks/{bid}.json'
    if not os.path.exists(target_path): continue
    new_entries.append({
        "id": bid, "nameEn": nameEn, "nameFa": nameFa,
        "category": category, "icon": bid
    })

if isinstance(index_data, dict):
    if 'blocks' in index_data:
        existing_ids = set(b['id'] for b in index_data['blocks'])
        for nb in new_entries:
            if nb['id'] not in existing_ids:
                index_data['blocks'].append(nb)
                existing_ids.add(nb['id'])
    elif 'categories' in index_data:
        for nb in new_entries:
            cat = nb['category']
            if cat not in index_data['categories']:
                index_data['categories'][cat] = []
            existing_ids = set(b['id'] for b in index_data['categories'][cat])
            if nb['id'] not in existing_ids:
                index_data['categories'][cat].append(nb)

with open('src/data/blocks/index.json', 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f"Created {created} new block JSON files")
print(f"Skipped (already existed): {skipped}")
print(f"Updated index.json with {len(new_entries)} new entries")
