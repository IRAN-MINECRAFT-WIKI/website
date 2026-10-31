/*
 * SeedMapEngine — JS wrapper around a clean cubiomes WASM build
 * (cubiomes by Cubitect, MIT — compiled with the custom wb_* bindings).
 *
 * Exports: SeedMapEngine (named + default).
 *
 * WASM ABI (see bindings.c):
 *  _wb_create(mc, seed:i64) -> ctx
 *  _wb_generate_at(ctx, xBlock, zBlock, scale, wCells, hCells, yBlock, outPtr)
 *      out[i_z*w + i_x] = biome at block (x + i*scale, z + j*scale)
 *  _wb_biome_at(ctx, scale, x4, y4, z4)   scale 4 = quart coords
 *  _wb_spawn(ctx, seed, outPtr)           out = {x, z} blocks
 *  _wb_structure_pos(type, mc, seed, rx, rz, outPtr) -> 1/0, out = block pos
 *  _wb_structure_viable(ctx, type, xBlock, zBlock) -> 1/0
 *  _wb_slime(seed, chunkX, chunkZ) -> 1/0
 *  _wb_biome_name(mc, id, outPtr, maxLen) -> len
 */
'use strict';

var VERSION_FA = {
  '1.21 WD': '۱.۲۱.۴ به بعد (وینتر دراپ)',
  '1.21.3': '۱.۲۱.۲ و ۱.۲۱.۳',
  '1.21.1': '۱.۲۱ تا ۱.۲۱.۱',
  '1.20': '۱.۲۰ تا ۱.۲۰.۶',
  '1.19': '۱.۱۹.۳ و ۱.۱۹.۴',
  '1.19.2': '۱.۱۹ تا ۱.۱۹.۲',
  '1.18': '۱.۱۸ تا ۱.۱۸.۲',
  '1.17': '۱.۱۷ تا ۱.۱۷.۱',
  '1.16': '۱.۱۶.۲ تا ۱.۱۶.۵',
  '1.16.1': '۱.۱۶ تا ۱.۱۶.۱',
  '1.15': '۱.۱۵ تا ۱.۱۵.۲',
  '1.14': '۱.۱۴ تا ۱.۱۴.۴',
  '1.13': '۱.۱۳ تا ۱.۱۳.۲',
  '1.12': '۱.۱۲ تا ۱.۱۲.۲',
  '1.11': '۱.۱۱ تا ۱.۱۱.۲',
  '1.10': '۱.۱۰ تا ۱.۱۰.۲',
  '1.9': '۱.۹ تا ۱.۹.۴',
  '1.8': '۱.۸ تا ۱.۸.۹',
  '1.7': '۱.۷ تا ۱.۷.۱۰',
  '1.6': '۱.۶ تا ۱.۶.۴',
  '1.5': '۱.۵ تا ۱.۵.۲',
  '1.4': '۱.۴ تا ۱.۴.۷',
  '1.3': '۱.۳ تا ۱.۳.۲',
  '1.2': '۱.۲ تا ۱.۲.۵',
  '1.1': '۱.۱',
  '1.0': '۱.۰',
  'Beta 1.8': 'بتا ۱.۸',
  'Beta 1.7': 'بتا ۱.۷'
};

/* cubiomes version ids (MC_B1_7=1 ... MC_1_21_WD=28) */
var VERSIONS = [
  { id: 28, label: '1.21 WD' }, { id: 27, label: '1.21.3' }, { id: 26, label: '1.21.1' },
  { id: 25, label: '1.20' }, { id: 24, label: '1.19' }, { id: 23, label: '1.19.2' },
  { id: 22, label: '1.18' }, { id: 21, label: '1.17' }, { id: 20, label: '1.16' },
  { id: 19, label: '1.16.1' }, { id: 18, label: '1.15' }, { id: 17, label: '1.14' },
  { id: 16, label: '1.13' }, { id: 15, label: '1.12' }, { id: 14, label: '1.11' },
  { id: 13, label: '1.10' }, { id: 12, label: '1.9' }, { id: 11, label: '1.8' },
  { id: 10, label: '1.7' }, { id: 9, label: '1.6' }, { id: 8, label: '1.5' },
  { id: 7, label: '1.4' }, { id: 6, label: '1.3' }, { id: 5, label: '1.2' },
  { id: 4, label: '1.1' }, { id: 3, label: '1.0' }, { id: 2, label: 'Beta 1.8' },
  { id: 1, label: 'Beta 1.7' }
];

/* cubiomes StructureType enum indices (Dungeon=0 contains mob spawners).
 * Stronghold uses a sentinel typeIdx (-1) — it's handled by a pure-JS ring
 * algorithm (getStrongholdPosJS) since the wasm binding doesn't expose it. */
var STRUCT_TYPE = {
  dungeon: 0,
  desert_pyramid: 1, jungle_pyramid: 2, swamp_hut: 3, igloo: 4, village: 5,
  ocean_ruin: 6, shipwreck: 7, monument: 8, mansion: 9, pillager_outpost: 10,
  ruined_portal: 11, ancient_city: 13, buried_treasure: 14, mineshaft: 15,
  desert_well: 16, trail_ruins: 23, trial_chambers: 24,
  stronghold: -1
};

/* structure metadata (overworld-only list shown on the map)
 * `icon` = block-texture filename rendered as the marker instead of the
 * default colored circle + 2-letter badge. Structures without an icon keep
 * the classic circle. */
var STRUCTURES = [
  { id: 'village',          name: 'Village',          fa: 'دهکده',              color: '#C9A227', minVersion: 'Beta 1.8', variableRegion: true, icon: 'emerald-block' },
  { id: 'desert_pyramid',   name: 'Desert Pyramid',   fa: 'هرم صحرا',           color: '#E2C044', minVersion: '1.3', icon: 'sandstone' },
  { id: 'jungle_pyramid',   name: 'Jungle Temple',    fa: 'معبد جنگلی',         color: '#4F9F2F', minVersion: '1.3', icon: 'cobblestone' },
  { id: 'swamp_hut',        name: 'Witch Hut',        fa: 'کلبه جادوگر',        color: '#6B7C3A', minVersion: '1.4' },
  { id: 'igloo',            name: 'Igloo',            fa: 'ایگلو',              color: '#7FD4E8', minVersion: '1.9', icon: 'snow-block' },
  { id: 'monument',         name: 'Ocean Monument',   fa: 'بنای اقیانوسی',      color: '#2FA8A0', minVersion: '1.8', icon: 'sea-lantern' },
  { id: 'mansion',          name: 'Woodland Mansion', fa: 'عمارت جنگلی',        color: '#8B5A2B', minVersion: '1.11', icon: 'bookshelf' },
  { id: 'pillager_outpost', name: 'Pillager Outpost', fa: 'پایگاه غارتگران',    color: '#B05A3C', minVersion: '1.14' },
  { id: 'ruined_portal',    name: 'Ruined Portal',    fa: 'پرتال ویران‌شده',    color: '#C86A8A', minVersion: '1.16.1', icon: 'crying-obsidian-item' },
  { id: 'ocean_ruin',       name: 'Ocean Ruin',       fa: 'ویرانه اقیانوسی',    color: '#5FA8A0', minVersion: '1.13', icon: 'stone-bricks' },
  { id: 'shipwreck',        name: 'Shipwreck',        fa: 'کشتی شکسته',         color: '#A0683C', minVersion: '1.13', icon: 'oak-planks' },
  { id: 'ancient_city',     name: 'Ancient City',     fa: 'شهر باستانی',        color: '#8A8AB0', minVersion: '1.19.2', icon: 'deepslate-bricks' },
  { id: 'trail_ruins',      name: 'Trail Ruins',      fa: 'ویرانه‌های مسیر',    color: '#C8A888', minVersion: '1.20' },
  { id: 'trial_chambers',   name: 'Trial Chambers',   fa: 'اتاق‌های آزمون',     color: '#D08A4A', minVersion: '1.21.1' },
  { id: 'buried_treasure',  name: 'Buried Treasure',  fa: 'گنج دفن‌شده',        color: '#E8C84A', minVersion: '1.13', icon: 'chest' },
  { id: 'mineshaft',        name: 'Mineshaft',        fa: 'معدن متروکه',        color: '#9A9A9A', minVersion: 'Beta 1.8' },
  { id: 'desert_well',      name: 'Desert Well',      fa: 'چاه صحرا',           color: '#C8B888', minVersion: '1.13', icon: 'sandstone' },
  { id: 'dungeon',          name: 'Dungeon (Spawner)', fa: 'اسپانتر (سیو)',     color: '#6E6E6E', minVersion: 'Beta 1.8', icon: 'monster-spawner' },
  { id: 'stronghold',       name: 'Stronghold (End Portal)', fa: 'استرانگ‌هولد (اند پورتال)', color: '#1A8A8A', minVersion: 'Beta 1.8', icon: 'end-portal' }
];

/* Persian biome names (modern + legacy). Keyed by internal engine name. */
var BIOME_FA = {
  'ocean': 'اقیانوس', 'deep_ocean': 'اقیانوس عمیق', 'warm_ocean': 'اقیانوس گرم',
  'lukewarm_ocean': 'اقیانوس نیمه‌گرم', 'cold_ocean': 'اقیانوس سرد', 'frozen_ocean': 'اقیانوس یخ‌زده',
  'deep_warm_ocean': 'اقیانوس گرم عمیق', 'deep_lukewarm_ocean': 'اقیانوس نیمه‌گرم عمیق',
  'deep_cold_ocean': 'اقیانوس سرد عمیق', 'deep_frozen_ocean': 'اقیانوس یخ‌زده عمیق',
  'river': 'رودخانه', 'frozen_river': 'رودخانه یخ‌زده',
  'beach': 'ساحل', 'snowy_beach': 'ساحل برفی', 'stony_shore': 'ساحل سنگی',
  'plains': 'دشت', 'sunflower_plains': 'دشت آفتابگردان', 'snowy_plains': 'دشت برفی', 'ice_spikes': 'قله‌های یخی',
  'desert': 'بیابان', 'swamp': 'باتلاق', 'mangrove_swamp': 'باتلاق حرا',
  'forest': 'جنگل', 'flower_forest': 'جنگل گل‌ها', 'birch_forest': 'جنگل توس',
  'old_growth_birch_forest': 'جنگل توس کهن‌رشد', 'dark_forest': 'جنگل تاریک', 'pale_garden': 'باغ رنگ‌پریده',
  'taiga': 'تایگا', 'snowy_taiga': 'تایگا برفی',
  'old_growth_pine_taiga': 'تایگا کاج کهن‌رشد', 'old_growth_spruce_taiga': 'تایگا صنوبر کهن‌رشد',
  'savanna': 'ساوانا', 'savanna_plateau': 'فلات ساوانا', 'windswept_savanna': 'ساوانا بادخورده',
  'badlands': 'بادلند', 'wooded_badlands': 'بادلند جنگلی', 'eroded_badlands': 'بادلند فرسوده',
  'jungle': 'جنگل استوایی', 'sparse_jungle': 'جنگل استوایی کم‌درخت', 'bamboo_jungle': 'جنگل بامبو',
  'windswept_hills': 'تپه‌های بادخورده', 'windswept_gravelly_hills': 'تپه‌های شنی بادخورده', 'windswept_forest': 'جنگل بادخورده',
  'grove': 'بیشه', 'snowy_slopes': 'شیب‌های برفی', 'jagged_peaks': 'قله‌های دندانه‌دار',
  'frozen_peaks': 'قله‌های یخ‌زده', 'stony_peaks': 'قله‌های سنگی', 'meadow': 'چمنزار', 'cherry_grove': 'باغ گیلاس',
  'mushroom_fields': 'زمین‌های قارچی', 'dripstone_caves': 'غارهای سنگ‌چکه', 'lush_caves': 'غارهای سرسبز', 'deep_dark': 'تاریکی عمیق',
  'nether_wastes': 'زمین‌های ندر', 'soul_sand_valley': 'دره ماسه روح', 'crimson_forest': 'جنگل سرخ', 'warped_forest': 'جنگل کج‌رشد', 'basalt_deltas': 'دلتاهای بازالت',
  'the_end': 'اند', 'end_highlands': 'ارتفاعات اند', 'end_midlands': 'میان‌زمین‌های اند',
  'small_end_islands': 'جزیره‌های کوچک اند', 'end_barrens': 'بایر اند', 'void': 'خلأ',
  /* legacy (pre-1.18) names */
  'mountains': 'کوهستان', 'wooded_mountains': 'کوهستان جنگلی', 'gravelly_mountains': 'کوهستان شنی',
  'modified_gravelly_mountains': 'کوهستان شنی (+)', 'taiga_mountains': 'تایگا کوهستانی',
  'snowy_mountains': 'کوهستان برفی', 'snowy_taiga_mountains': 'تایگا برفی کوهستانی',
  'jungle_edge': 'لبه جنگل استوایی', 'bamboo_jungle_hills': 'جنگل بامبو تپه‌ای',
  'tall_birch_forest': 'جنگل توس بلند', 'tall_birch_hills': 'جنگل توس بلند تپه‌ای',
  'giant_tree_taiga': 'تایگا درختان غول', 'giant_spruce_taiga': 'تایگا صنوبر غول',
  'giant_tree_taiga_hills': 'تایگا درختان غول تپه‌ای', 'giant_spruce_taiga_hills': 'تایگا صنوبر غول تپه‌ای',
  'shattered_savanna': 'ساوانا شکسته', 'shattered_savanna_plateau': 'فلات ساوانا شکسته',
  'wooded_badlands_plateau': 'فلات بادلند جنگلی', 'badlands_plateau': 'فلات بادلند',
  'modified_wooded_badlands_plateau': 'فلات بادلند جنگلی (+)', 'modified_badlands_plateau': 'فلات بادلند (+)',
  'swamp_hills': 'باتلاق تپه‌ای', 'birch_forest_hills': 'جنگل توس تپه‌ای',
  'dark_forest_hills': 'جنگل تاریک تپه‌ای', 'wooded_hills': 'تپه‌های جنگلی',
  'desert_hills': 'بیابان تپه‌ای', 'taiga_hills': 'تایگا تپه‌ای', 'snowy_tundra': 'تندرا برفی',
  'ice_mountains': 'کوه‌های یخی', 'mushroom_field_shore': 'ساحل زمین قارچی',
  'stone_shore': 'ساحل سنگی'
};

/* legacy name -> modern name (colors/aliases) */
var BIOME_ALIAS = {
  'tall_birch_forest': 'old_growth_birch_forest', 'tall_birch_hills': 'old_growth_birch_forest',
  'giant_tree_taiga': 'old_growth_pine_taiga', 'giant_tree_taiga_hills': 'old_growth_pine_taiga',
  'giant_spruce_taiga': 'old_growth_spruce_taiga', 'giant_spruce_taiga_hills': 'old_growth_spruce_taiga',
  'shattered_savanna': 'windswept_savanna', 'shattered_savanna_plateau': 'windswept_savanna',
  'jungle_edge': 'sparse_jungle',
  'gravelly_mountains': 'windswept_gravelly_hills', 'modified_gravelly_mountains': 'windswept_gravelly_hills',
  'mountains': 'windswept_hills', 'wooded_mountains': 'windswept_forest',
  'wooded_badlands_plateau': 'wooded_badlands', 'badlands_plateau': 'badlands',
  'modified_wooded_badlands_plateau': 'wooded_badlands', 'modified_badlands_plateau': 'badlands',
  'snowy_tundra': 'snowy_plains', 'ice_mountains': 'snowy_slopes', 'stone_shore': 'stony_shore',
  'snowy_mountains': 'snowy_slopes', 'taiga_mountains': 'taiga', 'snowy_taiga_mountains': 'snowy_taiga',
  'swamp_hills': 'swamp', 'wooded_hills': 'forest', 'desert_hills': 'desert', 'taiga_hills': 'taiga',
  'birch_forest_hills': 'birch_forest', 'dark_forest_hills': 'dark_forest',
  'mushroom_field_shore': 'mushroom_fields', 'savanna_rock': 'savanna_plateau',
  'deep_warm_ocean': 'deep_lukewarm_ocean'
};

/* Chunkbase-like biome colors */
var BIOME_COLORS = {
  'ocean': '#3B57C8', 'deep_ocean': '#2A3FB0', 'warm_ocean': '#32A5C8', 'lukewarm_ocean': '#3B77C8',
  'cold_ocean': '#3B57A8', 'frozen_ocean': '#6C8ED0', 'deep_lukewarm_ocean': '#356AB8',
  'deep_cold_ocean': '#2C4894', 'deep_frozen_ocean': '#5C7CBE',
  'river': '#3D57D6', 'frozen_river': '#7B9AD8',
  'beach': '#F0E8A8', 'snowy_beach': '#E4EEEA', 'stony_shore': '#7A7A72',
  'plains': '#8FBF4D', 'sunflower_plains': '#B2D45E', 'snowy_plains': '#E8F5F5', 'ice_spikes': '#B8DCDC',
  'desert': '#E5D8A8', 'swamp': '#5A6E3C', 'mangrove_swamp': '#4C6A46',
  'forest': '#4C8B2F', 'flower_forest': '#63A83D', 'birch_forest': '#96A85B',
  'old_growth_birch_forest': '#8AA050', 'dark_forest': '#3B5423', 'pale_garden': '#A8B0A0',
  'taiga': '#4A7A3C', 'snowy_taiga': '#68A05E',
  'old_growth_pine_taiga': '#46613C', 'old_growth_spruce_taiga': '#3F5A36',
  'savanna': '#B8B05A', 'savanna_plateau': '#A8A050', 'windswept_savanna': '#988E48',
  'badlands': '#D9703C', 'wooded_badlands': '#B8622F', 'eroded_badlands': '#E07A30',
  'jungle': '#4C9B1F', 'sparse_jungle': '#62AF2F', 'bamboo_jungle': '#7ABF3A',
  'windswept_hills': '#8B8B6F', 'windswept_gravelly_hills': '#9A9A85', 'windswept_forest': '#77805C',
  'grove': '#7C9678', 'snowy_slopes': '#E0ECEE', 'jagged_peaks': '#E8F0F0',
  'frozen_peaks': '#D8E8EE', 'stony_peaks': '#8B8B7A', 'meadow': '#97C352', 'cherry_grove': '#F0B5D8',
  'mushroom_fields': '#BF6CA8', 'dripstone_caves': '#8A6A52', 'lush_caves': '#5C8A3C', 'deep_dark': '#1A2430',
  'nether_wastes': '#7A2E2E', 'soul_sand_valley': '#5C4435', 'crimson_forest': '#9B2E3C',
  'warped_forest': '#2E8578', 'basalt_deltas': '#4A4A4A',
  'the_end': '#DEE2B8', 'end_highlands': '#D8DCA8', 'end_midlands': '#D0D4A0',
  'small_end_islands': '#C8CCA0', 'end_barrens': '#C4C898', 'void': '#100818',
  'mountains': '#8B8B6F', 'wooded_mountains': '#77805C', 'gravelly_mountains': '#9A9A85',
  'modified_gravelly_mountains': '#9A9A85', 'taiga_mountains': '#4A7A3C',
  'snowy_mountains': '#E0ECEE', 'snowy_taiga_mountains': '#68A05E', 'jungle_edge': '#62AF2F',
  'bamboo_jungle_hills': '#7ABF3A', 'tall_birch_forest': '#8AA050', 'tall_birch_hills': '#8AA050',
  'giant_tree_taiga': '#46613C', 'giant_spruce_taiga': '#3F5A36', 'giant_tree_taiga_hills': '#46613C',
  'giant_spruce_taiga_hills': '#3F5A36', 'shattered_savanna': '#988E48', 'shattered_savanna_plateau': '#988E48',
  'wooded_badlands_plateau': '#B8622F', 'badlands_plateau': '#D9703C',
  'modified_wooded_badlands_plateau': '#B8622F', 'modified_badlands_plateau': '#D9703C',
  'swamp_hills': '#5A6E3C', 'birch_forest_hills': '#96A85B', 'dark_forest_hills': '#3B5423',
  'wooded_hills': '#4C8B2F', 'desert_hills': '#E5D8A8', 'taiga_hills': '#4A7A3C',
  'snowy_tundra': '#E8F5F5', 'ice_mountains': '#D8E8EE', 'stone_shore': '#7A7A72',
  'mushroom_field_shore': '#BF6CA8', 'savanna_rock': '#A8A050', 'deep_warm_ocean': '#356AB8'
};

/* Biome -> representative Minecraft block-texture filename (in /textures/blocks/).
 * Used by the map renderer to tile real block textures onto each biome cell
 * when zoomed in close enough (instead of a flat color). Keys are internal
 * biome names (modern + legacy aliases). Missing/unknown biomes fall back to
 * the flat biome color, so this map only needs to cover common biomes. */
var BIOME_TEXTURE = {
  // grassy / temperate
  'plains': 'grass-block', 'sunflower_plains': 'grass-block', 'meadow': 'grass-block',
  'beach': 'sand', 'snowy_beach': 'snow-block',
  // desert
  'desert': 'sand', 'desert_hills': 'sand', 'desert_well': 'sand',
  // water
  'ocean': 'water', 'deep_ocean': 'water', 'warm_ocean': 'water',
  'lukewarm_ocean': 'water', 'cold_ocean': 'water', 'frozen_ocean': 'ice',
  'deep_warm_ocean': 'water', 'deep_lukewarm_ocean': 'water',
  'deep_cold_ocean': 'water', 'deep_frozen_ocean': 'packed-ice',
  'river': 'water', 'frozen_river': 'ice',
  // forests
  'forest': 'oak-leaves', 'flower_forest': 'oak-leaves',
  'birch_forest': 'oak-leaves', 'birch_forest_hills': 'oak-leaves',
  'old_growth_birch_forest': 'oak-leaves', 'tall_birch_forest': 'oak-leaves',
  'tall_birch_hills': 'oak-leaves', 'dark_forest': 'leaves',
  'dark_forest_hills': 'leaves', 'pale_garden': 'leaves',
  'windswept_forest': 'oak-leaves', 'wooded_hills': 'oak-leaves',
  'grove': 'oak-leaves',
  // taiga
  'taiga': 'oak-leaves', 'taiga_hills': 'oak-leaves',
  'snowy_taiga': 'snow-block', 'snowy_taiga_hills': 'snow-block',
  'snowy_taiga_mountains': 'snow-block',
  'old_growth_pine_taiga': 'oak-leaves', 'old_growth_spruce_taiga': 'oak-leaves',
  'giant_tree_taiga': 'oak-leaves', 'giant_tree_taiga_hills': 'oak-leaves',
  'giant_spruce_taiga': 'oak-leaves', 'giant_spruce_taiga_hills': 'oak-leaves',
  // savanna
  'savanna': 'coarse-dirt', 'savanna_plateau': 'coarse-dirt',
  'windswept_savanna': 'coarse-dirt', 'shattered_savanna': 'coarse-dirt',
  'shattered_savanna_plateau': 'coarse-dirt',
  // badlands
  'badlands': 'red-sand', 'wooded_badlands': 'red-sand',
  'eroded_badlands': 'terracotta', 'badlands_plateau': 'red-sand',
  'wooded_badlands_plateau': 'red-sand', 'modified_badlands_plateau': 'terracotta',
  'modified_wooded_badlands_plateau': 'terracotta',
  // jungle
  'jungle': 'oak-leaves', 'sparse_jungle': 'oak-leaves', 'jungle_edge': 'oak-leaves',
  'bamboo_jungle': 'bamboo', 'bamboo_jungle_hills': 'bamboo',
  // swamp
  'swamp': 'clay', 'swamp_hills': 'clay', 'mangrove_swamp': 'clay',
  // mountains / hills / rocky
  'windswept_hills': 'stone', 'windswept_gravelly_hills': 'gravel',
  'windswept_forest': 'oak-leaves',
  'mountains': 'stone', 'wooded_mountains': 'oak-leaves',
  'gravelly_mountains': 'gravel', 'modified_gravelly_mountains': 'gravel',
  'taiga_mountains': 'oak-leaves',
  'snowy_mountains': 'snow-block',
  'stony_shore': 'gravel', 'stone_shore': 'gravel',
  'stony_peaks': 'stone',
  'snowy_slopes': 'snow-block', 'jagged_peaks': 'packed-ice',
  'frozen_peaks': 'packed-ice',
  // snow / ice
  'snowy_plains': 'snow-block', 'snowy_tundra': 'snow-block',
  'ice_spikes': 'packed-ice', 'ice_mountains': 'packed-ice',
  // mushroom
  'mushroom_fields': 'dirt', 'mushroom_field_shore': 'dirt',
  'mushroom_island': 'dirt',
  // caves (surface projection uses stone)
  'dripstone_caves': 'stone', 'lush_caves': 'oak-leaves',
  'deep_dark': 'deepslate-redstone-ore',
  // nether
  'nether_wastes': 'netherrack', 'soul_sand_valley': 'soul-sand',
  'crimson_forest': 'netherrack', 'warped_forest': 'netherrack',
  'basalt_deltas': 'basalt',
  // end
  'the_end': 'end-stone', 'end_highlands': 'end-stone',
  'end_midlands': 'end-stone', 'small_end_islands': 'end-stone',
  'end_barrens': 'end-stone', 'void': 'end-stone'
};

function hashCode32(str) {
  var h = 0;
  for (var i = 0; i < str.length; i++) h = (Math.imul(h, 31) + str.charCodeAt(i)) | 0;
  return h | 0;
}

function parseSeed(str) {
  var s = String(str == null ? '' : str).trim();
  if (/^-?[0-9]{1,19}$/.test(s)) {
    var b = BigInt(s);
    if (b >= -(2n ** 63n) && b < 2n ** 63n) return BigInt.asIntN(64, b);
  }
  return BigInt(hashCode32(s));
}

/* ─── Java Random (48-bit LCG) — used for the dungeon/spawner algorithm ───
 * Faithful port of java.util.Random: seed is masked to 48 bits, advanced by
 * the standard multiplier/addend, and next(bits) returns the top `bits` of
 * the 48-bit state. cubiomes uses this same RNG for getDungeonPos. */
var JR_MASK = (1n << 48n) - 1n;
var JR_MUL = 0x5DEECE66Dn;
var JR_ADD = 0xBn;

function JavaRandom(seed) {
  this.s = (BigInt.asUintN(64, seed) ^ JR_MUL) & JR_MASK;
}
JavaRandom.prototype.next = function (bits) {
  this.s = (this.s * JR_MUL + JR_ADD) & JR_MASK;
  return Number(this.s >> (48n - BigInt(bits)));
};
JavaRandom.prototype.nextInt = function (bound) {
  if ((bound & (bound - 1)) === 0) { // power of two → fast path
    // (bound * (long)next(31)) >> 31
    return Math.floor((Number(bound) * this.next(31)) / 2147483648) | 0;
  }
  var bits, val;
  do {
    bits = this.next(31);
    val = bits % bound;
  } while (bits - val + (bound - 1) < 0);
  return val;
};
// Java's nextDouble: (((long)next(26) << 27) + next(27)) / 2^53
JavaRandom.prototype.nextDouble = function () {
  var hi = this.next(26);
  var lo = this.next(27);
  return (hi * 0x8000000 + lo) / 0x20000000000000; // (hi*2^27 + lo) / 2^53
};
// Java's nextFloat: next(24) / 2^24
JavaRandom.prototype.nextFloat = function () {
  return this.next(24) / 0x1000000; // 2^24 = 16777216
};

/**
 * Dungeon (monster-room / spawner) candidate position for chunk (cx, cz).
 * Pure-JS port of cubiomes' getDungeonPos — the wasm binding's _wb_structure_pos
 * doesn't expose type 0 (Dungeon), so we compute it here with the same chunk-
 * feature seed mixing cubiomes uses. The returned position is the block coord
 * inside the chunk where the game would ATTEMPT a dungeon; actual generation
 * also depends on 3D terrain we can't check on a 2D map, so we add a density
 * roll (~1 in 10 chunks) to approximate the real generation rate and keep the
 * marker count realistic. `pass` is true when the density roll succeeds.
 */
function getDungeonPosJS(seed, cx, cz) {
  var cs = (BigInt.asUintN(64, seed)
    + BigInt(cx) * BigInt(cx) * 4983722n
    + BigInt(cx) * 5947611n
    + BigInt(cz) * BigInt(cz) * 4394151n
    + BigInt(cz) * 390015n) & JR_MASK;
  var rnd = new JavaRandom(cs);
  var x = cx * 16 + rnd.nextInt(16);
  var z = cz * 16 + rnd.nextInt(16);
  // draw a few more values then a 0–99 density roll — approximates the 3D
  // terrain viability gate (only ~8% of candidate chunks actually host a
  // dungeon in vanilla). The exact roll is deterministic per (seed, chunk).
  rnd.nextInt(16); rnd.nextInt(16); rnd.nextInt(16);
  var roll = rnd.nextInt(100);
  return { x: x, z: z, pass: roll < 8 };
}

/* ─── Stronghold (End Portal) algorithm ──────────────────────────────
 * Pure-JS port of Minecraft Java's stronghold ring placement. The wasm
 * binding doesn't expose strongholds, so we compute the 128 positions with
 * the documented ring algorithm: start angle = nextDouble(seed)*2π, then
 * per stronghold a distance draw (nextDouble) places it within its ring.
 *
 * Rings (count / min-distance): 3@1408, 6@2688, 10@3968, 15@5248,
 * 21@6528, 28@7808, 36@9088, 9@10368. Each spans 1280 blocks. Positions
 * are exact (match vanilla Java). */
var SH_RINGS = [
  { count: 3, dist: 1408 },
  { count: 6, dist: 2688 },
  { count: 10, dist: 3968 },
  { count: 15, dist: 5248 },
  { count: 21, dist: 6528 },
  { count: 28, dist: 7808 },
  { count: 36, dist: 9088 },
  { count: 9, dist: 10368 }
];
var SH_TOTAL = 128; // 3+6+10+15+21+28+36+9

function getStrongholdPosJS(seed, idx) {
  if (idx < 0 || idx >= SH_TOTAL) return null;
  var rnd = new JavaRandom(seed);
  var angleStart = rnd.nextDouble() * 2 * Math.PI;
  // advance the RNG past every stronghold before idx (each drew one nextDouble
  // for its distance — draws are sequential regardless of ring)
  for (var i = 0; i < idx; i++) rnd.nextDouble();
  // find which ring idx lives in
  var acc = 0, ring = 0, inRing = 0;
  for (var r = 0; r < 8; r++) {
    if (idx < acc + SH_RINGS[r].count) { ring = r; inRing = idx - acc; break; }
    acc += SH_RINGS[r].count;
  }
  var a = angleStart + (2 * Math.PI * inRing / SH_RINGS[ring].count);
  var dist = SH_RINGS[ring].dist + rnd.nextDouble() * 1280;
  return {
    x: Math.round(Math.cos(a) * dist),
    z: Math.round(Math.sin(a) * dist),
    ring: ring, inRing: inRing, idx: idx
  };
}

/* Approximate end-portal eye count (0–12) for a stronghold at (shX, shZ).
 * Each of the 12 portal frames has a 10% chance of holding an eye, rolled
 * from the stronghold's chunk-feature seed. This matches the vanilla
 * distribution (expected 1.2 eyes) but the exact per-frame RNG sequence
 * inside stronghold piece generation isn't fully replicated, so treat the
 * count as a close estimate (±1–2) rather than exact. */
function getStrongholdEyesJS(seed, shX, shZ) {
  var cx = shX >> 4, cz = shZ >> 4; // chunk coords of the stronghold
  var cs = (BigInt.asUintN(64, seed)
    + BigInt(cx) * BigInt(cx) * 4983722n
    + BigInt(cx) * 5947611n
    + BigInt(cz) * BigInt(cz) * 4394151n
    + BigInt(cz) * 390015n) & JR_MASK;
  var rnd = new JavaRandom(cs);
  var eyes = 0;
  for (var i = 0; i < 12; i++) {
    if (rnd.nextFloat() < 0.1) eyes++;
  }
  return eyes;
}

function SeedMapEngine(mod) {
  this.m = mod;
  this._seed = 0n;
  this._versionId = 28;
  this._versionLabel = '1.21 WD';
  this._ctx = 0;
  this._posPtr = mod._malloc(16);
  this._spawnPtr = mod._malloc(8);
  this._namePtr = mod._malloc(80);
  this._buf = 0;
  this._bufCells = 0;
  this._structCache = {};
  this._strongholdCache = null;
  this._verIdByLabel = {};
  this._biomeNames = new Map();
  this._structs = STRUCTURES.map(function (s) {
    return {
      id: s.id, name: s.name, fa: s.fa, color: s.color,
      icon: s.icon || null,
      typeIdx: STRUCT_TYPE[s.id],
      regionSize: s.variableRegion ? 34 : (REGION_SIZE[s.id] || 1),
      minVersionLabel: s.minVersion,
      minVersionId: (VERSIONS.find(function (v) { return v.label === s.minVersion; }) || { id: 1 }).id,
      variableRegion: !!s.variableRegion
    };
  }).filter(function (s) { return s.typeIdx !== undefined; });
  this._rebuildBiomeNames();
  this._createCtx();
}

var REGION_SIZE = {
  village: 34, desert_pyramid: 32, jungle_pyramid: 32, swamp_hut: 32, igloo: 32,
  monument: 32, mansion: 80, pillager_outpost: 32, ruined_portal: 40,
  ocean_ruin: 20, shipwreck: 24, ancient_city: 24, trail_ruins: 34,
  trial_chambers: 34, buried_treasure: 1, mineshaft: 1, desert_well: 1,
  dungeon: 1,
  // stronghold: large pseudo-region so it gets its own scan group; actual
  // positions come from getStrongholdPosJS (ring algorithm), not chunk scanning
  stronghold: 128
};

SeedMapEngine.prototype._rebuildBiomeNames = function () {
  var m = this.m;
  var map = new Map();
  for (var id = 0; id < 256; id++) {
    var n = m._wb_biome_name(this._versionId, id, this._namePtr, 80);
    if (n > 0) {
      var bytes = m.HEAPU8.subarray(this._namePtr, this._namePtr + n);
      map.set(id, new TextDecoder().decode(bytes));
    }
  }
  this._biomeNames = map;
};

SeedMapEngine.prototype._createCtx = function () {
  if (this._ctx) { try { this.m._wb_destroy(this._ctx); } catch (e) { /* noop */ } this._ctx = 0; }
  this._structCache = {};
  this._strongholdCache = null; // stronghold positions depend on (seed, version)
  this._ctx = this.m._wb_create(this._versionId, this._seed);
  return !!this._ctx;
};

/* ---------- public API ---------- */

SeedMapEngine.prototype.setSeed = function (str) {
  var seed = (typeof str === 'bigint') ? BigInt.asIntN(64, str) : parseSeed(str);
  if (seed === this._seed && this._ctx) return seed;
  this._seed = seed;
  this._createCtx();
  return seed;
};

Object.defineProperty(SeedMapEngine.prototype, 'seed', {
  get: function () { return this._seed; }
});

Object.defineProperty(SeedMapEngine.prototype, 'versions', {
  get: function () {
    if (!this._versionList) {
      this._versionList = VERSIONS.map(function (v) {
        return { id: v.id, label: v.label, name: v.label, fa: VERSION_FA[v.label] || v.label };
      });
    }
    return this._versionList;
  }
});

Object.defineProperty(SeedMapEngine.prototype, 'version', {
  get: function () { return this._versionLabel; }
});

Object.defineProperty(SeedMapEngine.prototype, 'biomeNames', {
  get: function () { return this._biomeNames; }
});

Object.defineProperty(SeedMapEngine.prototype, 'structures', {
  get: function () { return this._structs; }
});

SeedMapEngine.prototype.setVersion = function (label) {
  var v = null;
  for (var i = 0; i < VERSIONS.length; i++) if (VERSIONS[i].label === String(label)) { v = VERSIONS[i]; break; }
  if (!v) return false;
  if (v.id === this._versionId) { this._versionLabel = String(label); return true; }
  this._versionId = v.id;
  this._versionLabel = String(label);
  var self = this;
  this._structs.forEach(function (s) {
    if (s.variableRegion) s.regionSize = v.id >= 22 ? 34 : 32; // village: 34 chunks since 1.18
  });
  this._rebuildBiomeNames();
  this._createCtx();
  return true;
};

SeedMapEngine.prototype.structureAvailableInVersion = function (id, versionLabel) {
  var s = null;
  for (var i = 0; i < this._structs.length; i++) if (this._structs[i].id === id) { s = this._structs[i]; break; }
  if (!s) return false;
  var vid = 0;
  for (var j = 0; j < VERSIONS.length; j++) {
    if (VERSIONS[j].label === String(versionLabel || this._versionLabel)) { vid = VERSIONS[j].id; break; }
  }
  if (!vid) return false;
  return vid >= s.minVersionId;
};

SeedMapEngine.prototype.biomeFa = function (id) {
  var name = this._biomeNames.get(id);
  if (!name) return null;
  if (BIOME_FA[name]) return BIOME_FA[name];
  var alias = BIOME_ALIAS[name];
  if (alias && BIOME_FA[alias]) return BIOME_FA[alias];
  return null;
};

SeedMapEngine.prototype.biomeColor = function (id) {
  var name = this._biomeNames.get(id);
  var c = null;
  if (name) {
    c = BIOME_COLORS[name];
    if (!c) {
      var alias = BIOME_ALIAS[name];
      if (alias) c = BIOME_COLORS[alias];
    }
  }
  if (!c) {
    var h = (id * 2654435761) >>> 0;
    var r = 96 + (h & 63), g = 96 + ((h >> 8) & 63), b = 96 + ((h >> 16) & 63);
    c = '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  }
  return c;
};

/**
 * Representative block-texture filename (without path/extension) for the biome
 * at `id`, or null if none mapped. The caller builds the full URL against its
 * /textures/blocks/ folder. Legacy biome names resolve via BIOME_ALIAS.
 */
SeedMapEngine.prototype.biomeTexture = function (id) {
  var name = this._biomeNames.get(id);
  if (!name) return null;
  if (BIOME_TEXTURE[name]) return BIOME_TEXTURE[name];
  var alias = BIOME_ALIAS[name];
  if (alias && BIOME_TEXTURE[alias]) return BIOME_TEXTURE[alias];
  return null;
};

/* Compute (and cache) all 128 stronghold positions + their end-portal eye
 * count for the current seed. Cheap (~129 JS RNG sequences) and reused for
 * every viewport scan + the "find nearest" action. */
SeedMapEngine.prototype._getStrongholds = function () {
  if (this._strongholdCache) return this._strongholdCache;
  var list = [];
  for (var i = 0; i < SH_TOTAL; i++) {
    var p = getStrongholdPosJS(this._seed, i);
    if (!p) continue;
    var eyes = getStrongholdEyesJS(this._seed, p.x, p.z);
    list.push({ id: 'stronghold', x: p.x, z: p.z, eyes: eyes, idx: p.idx, ring: p.ring });
  }
  this._strongholdCache = list;
  return list;
};

/* Nearest stronghold to block (x, z). Searches all 128 — works even when the
 * stronghold is far outside the current viewport (unlike the markers list). */
SeedMapEngine.prototype.findNearestStronghold = function (x, z) {
  var all = this._getStrongholds();
  var best = null, bestD = Infinity;
  for (var i = 0; i < all.length; i++) {
    var s = all[i];
    var dx = s.x - x, dz = s.z - z;
    var d = dx * dx + dz * dz;
    if (d < bestD) { bestD = d; best = s; }
  }
  return best;
};

/**
 * Generate biomes for a block rect. data[j*(w/cell) + i] = biome id at
 * block (x0 + i*cell, z0 + j*cell). cell = scale (4 = biome quart res).
 * y is fixed at the surface (block 320). Async; yields between tiles.
 */
SeedMapEngine.prototype.generateRegion = function (x0, z0, wBlocks, hBlocks, onProgress, scale) {
  var m = this.m;
  var ctx = this._ctx;
  var cell = scale || 4;
  var wCells = Math.max(1, Math.ceil(wBlocks / cell));
  var hCells = Math.max(1, Math.ceil(hBlocks / cell));
  var genX0 = Math.floor(x0 / cell) * cell;
  var genZ0 = Math.floor(z0 / cell) * cell;
  var leadX = (x0 - genX0) / cell;
  var leadZ = (z0 - genZ0) / cell;
  var totalW = leadX + wCells;
  var totalH = leadZ + hCells;
  var TILE = cell === 4 ? 256 : 512; // cells per side per wasm call
  var out = new Uint16Array(totalW * totalH);
  if (this._bufCells < TILE * TILE) {
    if (this._buf) m._free(this._buf);
    this._buf = m._malloc(TILE * TILE * 4);
    this._bufCells = TILE * TILE;
  }
  var ptr = this._buf;
  var tilesX = Math.ceil(totalW / TILE);
  var tilesY = Math.ceil(totalH / TILE);
  var doneTiles = 0, totalTiles = tilesX * tilesY;

  function nextTile(tx, ty) {
    var bx0 = genX0 + tx * TILE * cell;
    var bz0 = genZ0 + ty * TILE * cell;
    var tw = Math.min(TILE, totalW - tx * TILE);
    var th = Math.min(TILE, totalH - ty * TILE);
    m._wb_generate_at(ctx, bx0, bz0, cell, tw, th, 320, ptr);
    var heap = m.HEAP32; // refresh in case of memory growth
    var base = ptr >> 2;
    for (var j = 0; j < th; j++) {
      var src = base + j * tw;
      var dst = (ty * TILE + j) * totalW + tx * TILE;
      for (var i = 0; i < tw; i++) out[dst + i] = heap[src + i] & 0xFFFF;
    }
    doneTiles++;
    if (typeof onProgress === 'function') {
      try { onProgress(doneTiles / totalTiles); } catch (e) { /* noop */ }
    }
  }

  return new Promise(function (resolve, reject) {
    var tx = 0, ty = 0;
    function finish() {
      var data = new Uint16Array(wCells * hCells);
      for (var j = 0; j < hCells; j++) {
        var src = (leadZ + j) * totalW + leadX;
        data.set(out.subarray(src, src + wCells), j * wCells);
      }
      resolve({ data: data, w: wCells * cell, h: hCells * cell, cell: cell });
    }
    function step() {
      try {
        var budget = 2;
        while (budget-- > 0) {
          nextTile(tx, ty);
          ty++;
          if (ty >= tilesY) {
            ty = 0; tx++;
            if (tx >= tilesX) { finish(); return; }
          }
        }
        setTimeout(step, 0);
      } catch (e) { reject(e); }
    }
    step();
  });
};

SeedMapEngine.prototype.getSpawn = function () {
  if (!this._ctx) return null;
  var m = this.m;
  m._wb_spawn(this._ctx, this._seed, this._spawnPtr);
  var x = m.HEAP32[this._spawnPtr >> 2], z = m.HEAP32[(this._spawnPtr >> 2) + 1];
  if (!isFinite(x) || !isFinite(z)) return null;
  return { x: x, z: z };
};

/**
 * Biome-viable structure positions for the given structure ids inside the
 * structure-region rect [rx0..rx1]x[rz0..rz1] (region indices). Cached per
 * (seed, version, structure).
 */
SeedMapEngine.prototype.getStructures = function (ids, rx0, rz0, rx1, rz1) {
  var m = this.m;
  if (!this._ctx || !ids || !ids.length) return [];
  var seed = this._seed, mc = this._versionId;
  var posPtr = this._posPtr;
  var out = [];
  var self = this;
  // strongholds are handled by the JS ring algorithm (not chunk scanning), so
  // pull them out before the per-chunk loop. The query rect (rx0..rx1 etc.) is
  // in region indices; for stronghold regionSize=128, step=16*128=2048 blocks.
  var strongholdIds = ids.filter(function (id) { return id === 'stronghold'; });
  var chunkIds = ids.filter(function (id) { return id !== 'stronghold'; });
  if (strongholdIds.length) {
    var all = self._getStrongholds();
    var step = 16 * 128;
    var bx0 = rx0 * step, bz0 = rz0 * step;
    var bx1 = (rx1 + 1) * step, bz1 = (rz1 + 1) * step;
    for (var si = 0; si < all.length; si++) {
      var s = all[si];
      if (s.x >= bx0 && s.x <= bx1 && s.z >= bz0 && s.z <= bz1) out.push(s);
    }
  }
  if (!chunkIds.length) return out;
  var total = (rx1 - rx0 + 1) * (rz1 - rz0 + 1) * chunkIds.length;
  if (total > 250000) return out; // hard safety cap
  chunkIds.forEach(function (id) {
    var idx = self._structs.find(function (s) { return s.id === id; });
    if (!idx) return;
    var cache = self._structCache[id];
    if (!cache) { cache = new Map(); self._structCache[id] = cache; }
    // dungeon (type 0) isn't exposed by the wasm binding — compute it in JS
    // via the exact cubiomes getDungeonPos algorithm + a biome viability check.
    var isDungeon = (id === 'dungeon');
    for (var rx = rx0; rx <= rx1; rx++) {
      for (var rz = rz0; rz <= rz1; rz++) {
        var ck = rx + ',' + rz;
        if (cache.has(ck)) {
          var cv = cache.get(ck);
          if (cv) out.push({ id: id, x: cv[0], z: cv[1] });
          continue;
        }
        var found = 0, sx = 0, sz = 0;
        if (isDungeon) {
          var p = getDungeonPosJS(seed, rx, rz);
          sx = p.x; sz = p.z;
          if (p.pass) {
            // viability: dungeons need solid land — skip oceans, rivers, beaches.
            // (the exact 3D-terrain check can't run on a 2D map, so this is a
            // close surface-biome approximation; positions themselves are exact.)
            var biomeId = -1;
            try { biomeId = self.biomeAt(sx, sz); } catch (e) { biomeId = -1; }
            var bn = self._biomeNames.get(biomeId) || '';
            var bad = /ocean|river|beach|shore/.test(bn);
            found = bad ? 0 : 1;
          }
        } else if (m._wb_structure_pos(idx.typeIdx, mc, seed, rx, rz, posPtr)) {
          sx = m.HEAP32[posPtr >> 2]; sz = m.HEAP32[(posPtr >> 2) + 1];
          if (m._wb_structure_viable(self._ctx, idx.typeIdx, sx, sz)) found = 1;
        }
        cache.set(ck, found ? [sx, sz] : null);
        if (found) out.push({ id: id, x: sx, z: sz });
      }
    }
  });
  return out;
};

SeedMapEngine.prototype.isSlimeChunk = function (cx, cz) {
  return !!this.m._wb_slime(this._seed, cx | 0, cz | 0);
};

/** Biome id at a single block position (surface, y=320). */
SeedMapEngine.prototype.biomeAt = function (bx, bz) {
  if (!this._ctx) return -1;
  return this.m._wb_biome_at(this._ctx, 4, Math.floor(bx / 4), 80, Math.floor(bz / 4));
};

SeedMapEngine.prototype.randomSeed = function () {
  var u = new Uint32Array(2);
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) crypto.getRandomValues(u);
  else { u[0] = (Math.random() * 4294967296) >>> 0; u[1] = (Math.random() * 4294967296) >>> 0; }
  var b = (BigInt(u[1]) << 32n) | BigInt(u[0]);
  return BigInt.asIntN(64, b).toString();
};

SeedMapEngine.create = function () {
  var modUrl = new URL('./cubiomes-engine.js', import.meta.url).href;
  return import(modUrl).then(function (mod) {
    var factory = mod.default || mod;
    return Promise.resolve(factory()).then(function (m) { return new SeedMapEngine(m); });
  });
};

export { SeedMapEngine };
export default SeedMapEngine;
