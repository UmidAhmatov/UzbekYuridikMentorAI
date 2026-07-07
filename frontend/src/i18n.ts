export type Language = "uz-latin" | "uz-cyrillic" | "ru";

const uzLatin = {
  brandSubtitle: "Huquqiy va karyera mentori",
  mainNavigation: "Asosiy bo'limlar",
  chat: "Chat",
  documents: "Hujjatlar",
  roadmap: "Yo'l xaritasi",
  career: "Karyera",
  language: "Til",
  aiMentor: "AI mentor",
  chatTitle: "Huquqiy va karyera chat",
  ready: "Tayyor",
  writing: "Yozmoqda",
  greeting: "Assalomu alaykum. Huquqiy savol, hujjat loyihasi yoki karyera masalasi bo'yicha yozing.",
  legalSources: "Lex.uz manbalari",
  message: "Xabar",
  messagePlaceholder: "Savolingizni yozing...",
  send: "Yuborish",
  loading: "Yuklanmoqda",
  retry: "Qayta urinish",
  documentType: "Hujjat turi",
  newDocument: "Yangi hujjat",
  generateDocument: "Hujjat yaratish",
  generating: "Tayyorlanmoqda",
  select: "Tanlang",
  readyDocument: "Tayyor hujjat",
  newAgain: "Yangidan",
  copy: "Nusxalash",
  copied: "Nusxalandi",
  downloadPdf: "PDF yuklab olish",
  legalNotice: "Huquqiy ogohlantirish",
  roadmapEyebrow: "Huquqiy jarayon",
  roadmapTitle: "Aniq yo'l xaritasini tuzing",
  roadmapDescription: "Vaziyatingizni yozing. AI kerakli hujjatlar, organlar va muddatlarni Lex.uz asosida tartiblaydi.",
  situation: "Vaziyat",
  situationPlaceholder: "Nima sodir bo'ldi? Muhim tafsilotlarni ketma-ket yozing.",
  goal: "Maqsad",
  goalPlaceholder: "Qanday natijaga erishmoqchisiz?",
  region: "Hudud",
  regionPlaceholder: "Masalan: Toshkent shahri",
  eventDate: "Muhim sana",
  eventDatePlaceholder: "Masalan: buyruq 2026-yil 15-iyunda berildi",
  availableDocuments: "Mavjud hujjatlar",
  availableDocumentsPlaceholder: "Shartnoma, buyruq, yozishmalar va boshqa dalillar",
  generateRoadmap: "Yo'l xaritasini tuzish",
  roadmapGenerating: "Yo'l xaritasi tuzilmoqda",
  careerEyebrow: "Kasbiy rivojlanish",
  careerTitle: "Karyera harakat rejasini oling",
  careerDescription: "Profilingiz va maqsadingiz asosida O'zbekiston mehnat bozoriga mos 30/60/90 kunlik reja oling.",
  currentRole: "Hozirgi rol yoki holat",
  currentRolePlaceholder: "Masalan: junior buxgalter yoki talaba",
  experienceLevel: "Tajriba darajasi",
  experienceLevelPlaceholder: "Masalan: 2 yil",
  targetRole: "Maqsadli rol",
  targetRolePlaceholder: "Masalan: moliyaviy tahlilchi",
  skills: "Ko'nikmalar",
  skillsPlaceholder: "Dasturlar, tillar, texnik va yumshoq ko'nikmalar",
  employmentType: "Ish shakli",
  employmentTypePlaceholder: "Ofis, masofaviy, gibrid yoki farqi yo'q",
  notes: "Qo'shimcha ma'lumot",
  notesPlaceholder: "Cheklovlar, muddat, ta'lim yoki portfolio haqida",
  generateCareer: "Karyera rejasini tuzish",
  careerGenerating: "Karyera rejasi tuzilmoqda",
  adviceResult: "AI tavsiyasi",
  startOver: "Qayta boshlash",
  unexpectedError: "Sahifada kutilmagan xato yuz berdi.",
} as const;

type TranslationKey = keyof typeof uzLatin;

const ru: Record<TranslationKey, string> = {
  brandSubtitle: "Правовой и карьерный наставник",
  mainNavigation: "Основные разделы",
  chat: "Чат",
  documents: "Документы",
  roadmap: "Дорожная карта",
  career: "Карьера",
  language: "Язык",
  aiMentor: "AI-наставник",
  chatTitle: "Правовой и карьерный чат",
  ready: "Готов",
  writing: "Печатает",
  greeting: "Здравствуйте. Напишите правовой вопрос, задачу по документу или карьерную цель.",
  legalSources: "Источники Lex.uz",
  message: "Сообщение",
  messagePlaceholder: "Введите вопрос...",
  send: "Отправить",
  loading: "Загрузка",
  retry: "Повторить",
  documentType: "Тип документа",
  newDocument: "Новый документ",
  generateDocument: "Создать документ",
  generating: "Подготовка",
  select: "Выберите",
  readyDocument: "Готовый документ",
  newAgain: "Новый",
  copy: "Копировать",
  copied: "Скопировано",
  downloadPdf: "Скачать PDF",
  legalNotice: "Правовое предупреждение",
  roadmapEyebrow: "Правовой процесс",
  roadmapTitle: "Составьте точную дорожную карту",
  roadmapDescription: "Опишите ситуацию. AI упорядочит документы, органы и сроки на основе Lex.uz.",
  situation: "Ситуация",
  situationPlaceholder: "Что произошло? Опишите важные детали по порядку.",
  goal: "Цель",
  goalPlaceholder: "Какого результата вы хотите достичь?",
  region: "Регион",
  regionPlaceholder: "Например: город Ташкент",
  eventDate: "Важная дата",
  eventDatePlaceholder: "Например: приказ выдан 15 июня 2026 года",
  availableDocuments: "Имеющиеся документы",
  availableDocumentsPlaceholder: "Договор, приказ, переписка и другие доказательства",
  generateRoadmap: "Составить дорожную карту",
  roadmapGenerating: "Составление дорожной карты",
  careerEyebrow: "Профессиональное развитие",
  careerTitle: "Получите карьерный план действий",
  careerDescription: "Получите план на 30/60/90 дней для рынка труда Узбекистана на основе вашего профиля.",
  currentRole: "Текущая роль или статус",
  currentRolePlaceholder: "Например: младший бухгалтер или студент",
  experienceLevel: "Опыт",
  experienceLevelPlaceholder: "Например: 2 года",
  targetRole: "Целевая роль",
  targetRolePlaceholder: "Например: финансовый аналитик",
  skills: "Навыки",
  skillsPlaceholder: "Программы, языки, технические и гибкие навыки",
  employmentType: "Формат работы",
  employmentTypePlaceholder: "Офис, удалённо, гибрид или без разницы",
  notes: "Дополнительная информация",
  notesPlaceholder: "Ограничения, сроки, образование или портфолио",
  generateCareer: "Составить карьерный план",
  careerGenerating: "Составление карьерного плана",
  adviceResult: "Рекомендация AI",
  startOver: "Начать заново",
  unexpectedError: "На странице произошла непредвиденная ошибка.",
};

export function t(language: Language, key: TranslationKey): string {
  if (language === "ru") {
    return ru[key];
  }
  if (language === "uz-cyrillic") {
    return latinToCyrillic(uzLatin[key]);
  }
  return uzLatin[key];
}

export const languageOptions: Array<{ value: Language; label: string }> = [
  { value: "uz-latin", label: "O'zbek" },
  { value: "uz-cyrillic", label: "Ўзбек" },
  { value: "ru", label: "Русский" },
];

function latinToCyrillic(value: string): string {
  const replacements: Array<[RegExp, string]> = [
    [/(O‘|O'|Oʻ)/g, "Ў"], [/(o‘|o'|oʻ)/g, "ў"],
    [/(G‘|G'|Gʻ)/g, "Ғ"], [/(g‘|g'|gʻ)/g, "ғ"],
    [/Sh/g, "Ш"], [/sh/g, "ш"], [/Ch/g, "Ч"], [/ch/g, "ч"],
    [/Yo/g, "Ё"], [/yo/g, "ё"], [/Yu/g, "Ю"], [/yu/g, "ю"],
    [/Ya/g, "Я"], [/ya/g, "я"], [/Ye/g, "Е"], [/ye/g, "е"],
  ];
  let output = value;
  for (const [pattern, replacement] of replacements) {
    output = output.replace(pattern, replacement);
  }
  output = output.replace(/['’‘]/g, "ъ");
  const letters: Record<string, string> = {
    A: "А", a: "а", B: "Б", b: "б", D: "Д", d: "д", E: "Е", e: "е",
    F: "Ф", f: "ф", H: "Ҳ", h: "ҳ", I: "И", i: "и", J: "Ж", j: "ж",
    K: "К", k: "к", L: "Л", l: "л", M: "М", m: "м", N: "Н", n: "н",
    O: "О", o: "о", P: "П", p: "п", Q: "Қ", q: "қ", R: "Р", r: "р",
    S: "С", s: "с", T: "Т", t: "т", U: "У", u: "у", V: "В", v: "в",
    X: "Х", x: "х", Y: "Й", y: "й", Z: "З", z: "з",
  };
  return [...output].map((letter) => letters[letter] ?? letter).join("");
}
