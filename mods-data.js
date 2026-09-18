/* ==================================================
   داده‌های افزونه‌های Bedrock
   ==================================================
   برای اضافه کردن افزونه جدید، یه آبجکت به لیست اضافه کن.
   می‌تونی تصاویر و موسیقی رو از سرورهای خارجی لینک بدی
   تا ترافیک سایتت پایین بمونه.
*/
window.MODS = [
  {
    id: 'furniture',
    name: 'Furniture Addon',
    category: 'decoration',
    catName: 'دکوراسیون',
    tagline: 'صدها وسیله خونگی واقعی برای داخل بازی',
    desc: 'با این افزونه می‌تونی خونه‌ت رو واقعاً مثل یه خونه‌ی واقعی بچینی. مبل، تخت، میز، یخچال، تلویزیون، کولر آبی و... همه با کرفت درست می‌شن و می‌تونی رنگ هرکدوم رو عوض کنی.',
    icon: '🪑',
    version: '1.21',
    format: 'mcaddon',
    size: '4.2 MB',
    author: 'MineTeam',
    downloads: '82K',
    rating: 4.8,
    updated: '1404/05/20',
    featured: true,
    isNew: true,
    cover: 'https://picsum.photos/seed/furniture-a/900/560',
    gallery: [
      'https://picsum.photos/seed/furniture-1/700/440',
      'https://picsum.photos/seed/furniture-2/700/440',
      'https://picsum.photos/seed/furniture-3/700/440'
    ],
    music: {
      title: 'Mice on Venus',
      artist: 'C418',
      cover: 'https://picsum.photos/seed/cover-f/200/200',
      src: 'https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3'
    },
    downloadUrl: 'https://example.com/furniture.mcaddon',
    mirrors: [
      { name: 'MediaFire', url: 'https://example.com/mf/furniture' },
      { name: 'Mega', url: 'https://example.com/mega/furniture' }
    ],
    installSteps: [
      'فایل mcaddon رو دانلود کن',
      'روی فایل بزن تا خودکار با ماینکرفت باز بشه',
      'توی بازی یه دنیای جدید بساز یا وارد یه دنیای قدیمی شو',
      'برو به Settings > Add-Ons و افزونه رو روی دنیا فعال کن',
      'دنیا رو یه بار ببند و باز کن تا همه‌چیز لود بشه'
    ]
  },
  {
    id: 'lucky-blocks',
    name: 'Lucky Blocks',
    category: 'gameplay',
    catName: 'گیم‌پلی',
    tagline: 'بلوک‌های شانسی که زندگیت رو عوض می‌کنن',
    desc: 'با هر شکستن Lucky Block یه اتفاق جدید میفته. ممکنه یه الماس بگیری، ممکنه یه کریپر مسلح بیرون بیاد. برای بازی با دوستا ویدیو چالشی فوق‌العاده‌ست.',
    icon: '🎁',
    version: '1.21',
    format: 'mcaddon',
    size: '2.8 MB',
    author: 'LuckyTeam',
    downloads: '140K',
    rating: 4.6,
    updated: '1404/04/11',
    featured: true,
    isNew: false,
    cover: 'https://picsum.photos/seed/lucky-a/900/560',
    gallery: [
      'https://picsum.photos/seed/lucky-1/700/440',
      'https://picsum.photos/seed/lucky-2/700/440'
    ],
    music: {
      title: 'Sweden',
      artist: 'C418',
      cover: 'https://picsum.photos/seed/cover-l/200/200',
      src: 'https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0c6ff1b1b.mp3'
    },
    downloadUrl: 'https://example.com/lucky.mcaddon',
    mirrors: [
      { name: 'MediaFire', url: 'https://example.com/mf/lucky' }
    ],
    installSteps: [
      'فایل رو دانلود کن',
      'روی فایل بزن تا ماینکرفت باز بشه',
      'افزونه رو توی دنیات فعال کن',
      'با کرفت کردن Lucky Block شروع کن'
    ]
  },
  {
    id: 'modern-city',
    name: 'Modern City Map',
    category: 'maps',
    catName: 'مپ',
    tagline: 'یه شهر مدرن آماده با ماشین و مترو',
    desc: 'یه نقشه‌ی آماده که یه شهر کامل با آسمون‌خراش، جاده، چراغ راهنما، مترو و پارکینگ توش ساخته شده. می‌تونی باهاش نقشه‌های RP بسازی یا فقط بگردی داخلش.',
    icon: '🏙️',
    version: '1.21',
    format: 'mcworld',
    size: '18 MB',
    author: 'CityCraft',
    downloads: '55K',
    rating: 4.9,
    updated: '1404/06/02',
    featured: true,
    isNew: true,
    cover: 'https://picsum.photos/seed/city-a/900/560',
    gallery: [
      'https://picsum.photos/seed/city-1/700/440',
      'https://picsum.photos/seed/city-2/700/440',
      'https://picsum.photos/seed/city-3/700/440'
    ],
    downloadUrl: 'https://example.com/city.mcworld',
    mirrors: [
      { name: 'MediaFire', url: 'https://example.com/mf/city' }
    ],
    installSteps: [
      'فایل mcworld رو دانلود کن',
      'روی فایل بزن تا مستقیم توی ماینکرفت لود بشه',
      'از لیست دنیاها انتخابش کن و بازی رو شروع کن'
    ]
  },
  {
    id: 'rtx-pack',
    name: 'Vanilla RTX',
    category: 'graphics',
    catName: 'گرافیک',
    tagline: 'گرافیک فوق‌العاده با Ray Tracing واقعی',
    desc: 'اگه گوشی یا کارت گرافیکت از رِی‌تریسینگ پشتیبانی می‌کنه، این پک گرافیک بازی رو کامل متحول می‌کنه. سایه‌های واقعی، آب شفاف و انعکاس نور.',
    icon: '✨',
    version: '1.21',
    format: 'mcpack',
    size: '12 MB',
    author: 'RTXStudio',
    downloads: '210K',
    rating: 4.7,
    updated: '1404/05/08',
    featured: false,
    isNew: false,
    cover: 'https://picsum.photos/seed/rtx-a/900/560',
    gallery: [
      'https://picsum.photos/seed/rtx-1/700/440',
      'https://picsum.photos/seed/rtx-2/700/440'
    ],
    downloadUrl: 'https://example.com/rtx.mcpack',
    mirrors: [
      { name: 'MediaFire', url: 'https://example.com/mf/rtx' },
      { name: 'Mega', url: 'https://example.com/mega/rtx' }
    ],
    installSteps: [
      'فایل mcpack رو دانلود کن',
      'روی فایل بزن تا نصب بشه',
      'توی تنظیمات گرافیک بازی، پک رو فعال کن',
      'RTX فقط روی نسخه‌ی Windows و کنسول‌های جدید کار می‌کنه'
    ]
  },
  {
    id: 'dragon-plus',
    name: 'Dragons Plus',
    category: 'mobs',
    catName: 'موجودات',
    tagline: 'اژدهای جدید برای اهلی کردن',
    desc: 'با این افزونه چندین نوع اژدهای جدید به بازی اضافه می‌شه که می‌تونی اهلیشون کنی، روشون سوار بشی و حتی باهاشون بجنگی. هر اژدها یه قدرت خاص داره.',
    icon: '🐉',
    version: '1.21',
    format: 'mcaddon',
    size: '6.5 MB',
    author: 'DragonForge',
    downloads: '98K',
    rating: 4.5,
    updated: '1404/03/27',
    featured: false,
    isNew: false,
    cover: 'https://picsum.photos/seed/dragon-a/900/560',
    gallery: [
      'https://picsum.photos/seed/dragon-1/700/440',
      'https://picsum.photos/seed/dragon-2/700/440'
    ],
    downloadUrl: 'https://example.com/dragons.mcaddon',
    mirrors: [
      { name: 'MediaFire', url: 'https://example.com/mf/dragons' }
    ],
    installSteps: [
      'فایل رو دانلود کن',
      'روی فایل بزن تا ماینکرفت باز شه',
      'افزونه رو توی دنیات فعال کن',
      'دنبال تخم اژدها بگرد تا بتونی پرورشش بدی'
    ]
  },
  {
    id: 'better-tools',
    name: 'Better Tools & Weapons',
    category: 'gameplay',
    catName: 'گیم‌پلی',
    tagline: 'شمشیر و ابزارهای جدید با قابلیت‌های خاص',
    desc: 'ده‌ها شمشیر، تبر و کلنگ جدید با قدرت‌ها و افکت‌های منحصر بفرد. بعضی‌هاشون آتش می‌زنن، بعضی‌ها یخ می‌بندن و بعضی‌ها حتی تلپورت می‌کنن.',
    icon: '⚔️',
    version: '1.21',
    format: 'mcaddon',
    size: '3.4 MB',
    author: 'ForgeLab',
    downloads: '120K',
    rating: 4.7,
    updated: '1404/04/30',
    featured: false,
    isNew: false,
    cover: 'https://picsum.photos/seed/tools-a/900/560',
    gallery: [
      'https://picsum.photos/seed/tools-1/700/440'
    ],
    downloadUrl: 'https://example.com/tools.mcaddon',
    mirrors: [
      { name: 'MediaFire', url: 'https://example.com/mf/tools' }
    ],
    installSteps: [
      'فایل رو دانلود کن',
      'روی فایل بزن تا نصب بشه',
      'افزونه رو فعال کن و از جدول کرفت ابزارها بساز'
    ]
  },
  {
    id: 'morph',
    name: 'Morph Addon',
    category: 'gameplay',
    catName: 'گیم‌پلی',
    tagline: 'خودت رو تبدیل به هر موجودی کن',
    desc: 'با این افزونه می‌تونی به هر موجودی توی بازی تبدیل بشی. زامبی شو، اندرمن شو، کریپر شو یا حتی اژدها. هر موجود قابلیت‌های خودش رو داره.',
    icon: '🔮',
    version: '1.21',
    format: 'mcaddon',
    size: '5.1 MB',
    author: 'MorphTeam',
    downloads: '175K',
    rating: 4.8,
    updated: '1404/06/10',
    featured: true,
    isNew: true,
    cover: 'https://picsum.photos/seed/morph-a/900/560',
    gallery: [
      'https://picsum.photos/seed/morph-1/700/440',
      'https://picsum.photos/seed/morph-2/700/440'
    ],
    downloadUrl: 'https://example.com/morph.mcaddon',
    mirrors: [
      { name: 'MediaFire', url: 'https://example.com/mf/morph' }
    ],
    installSteps: [
      'فایل رو دانلود کن',
      'روی فایل بزن تا ماینکرفت باز شه',
      'افزونه رو فعال کن',
      'از منوی Morph موجود مورد نظرت رو انتخاب کن'
    ]
  },
  {
    id: 'backpack',
    name: 'Backpack Plus',
    category: 'utility',
    catName: 'ابزار',
    tagline: 'کوله‌پشتی قابل حمل برای همه‌ی آیتم‌هات',
    desc: 'دیگه لازم نیست هربار برگردی خونه تا وسایلت رو خالی کنی. یه کوله‌پشتی بساز، آیتم‌هات رو بذار توش و هرجا بری با خودت ببر.',
    icon: '🎒',
    version: '1.21',
    format: 'mcaddon',
    size: '1.8 MB',
    author: 'PackCraft',
    downloads: '65K',
    rating: 4.6,
    updated: '1404/02/18',
    featured: false,
    isNew: false,
    cover: 'https://picsum.photos/seed/bag-a/900/560',
    gallery: [],
    downloadUrl: 'https://example.com/backpack.mcaddon',
    mirrors: [
      { name: 'MediaFire', url: 'https://example.com/mf/backpack' }
    ],
    installSteps: [
      'فایل رو دانلود کن',
      'روی فایل بزن تا نصب بشه',
      'افزونه رو توی دنیات فعال کن',
      'با کرفت کوله‌پشتی بسازش و بزنش روی خودت'
    ]
  }
];