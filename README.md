# UzbekYuridikMentorAI
UzbekMentorAI
O'zbekiston bozori uchun o'zbek tilida ishlaydigan huquqiy va karyera AI-mentori.

Bosqich 1 holati
FastAPI backend skeleti yaratildi.
/api/health endpointi qo'shildi.
Vite + React + TypeScript frontend skeleti yaratildi.
PostgreSQL, backend va frontend uchun docker-compose.yml qo'shildi.
Sirlar .env faylida saqlanishi uchun .env.example va .gitignore tayyorlandi.
Bosqich 2 holati
Async SQLAlchemy 2.x baza konfiguratsiyasi qo'shildi.
users, chats, messages, documents modellar qo'shildi.
documents.turi uchun enum qiymatlar: davo_arizasi, shikoyat, ishonchnoma, mehnat_shartnomasi, ijara_shartnomasi, sud_arizasi.
Alembic konfiguratsiyasi va dastlabki migratsiya qo'shildi.
Bosqich 3 holati
pgvector va pg_trgm extensionlari uchun Alembic migratsiyasi qo'shildi.
legal_chunks jadvali va trigram/vector indekslari qo'shildi.
BGE-m3 embedding servisi qo'shildi (BAAI/bge-m3, 1024-dim).
legal_kb.py hybrid retrieval servisi qo'shildi.
scripts/ingest.py Lex.uz hujjatlarini modda bo'yicha yig'ish, chunklash va legal_chunksga yozish uchun qo'shildi.
Bosqich 4 holati
Claude Messages endpoint uchun async streaming client qo'shildi.
/api/chat/stream SSE endpointi qo'shildi.
Chat so'rovida avval legal_kb.retrieve, keyin Claude streaming ishlaydi.
Minimal React chat UI qo'shildi.
Bosqich 5 holati
Oltita hujjat turi uchun dinamik template katalogi qo'shildi.
GET /api/documents/templates endpointi formalar schemasini qaytaradi.
POST /api/documents/generate RAG konteksti bilan hujjat yaratadi va natijani bazaga saqlaydi.
GET /api/documents/{id}/pdf Unicode PDF faylini tayyorlaydi.
Frontendda hujjat turi, dinamik forma, Lex.uz manbalari, disklaymer, nusxalash va PDF yuklab olish oqimi qo'shildi.
Bosqich 6 holati
POST /api/roadmap/generate Lex.uz RAG konteksti bilan bosqichma-bosqich huquqiy yo'l xaritasini yaratadi.
POST /api/career/advise O'zbekiston mehnat bozoriga mos 30/60/90 kunlik karyera rejasini yaratadi.
Frontendda Chat, Hujjatlar, Yo'l xaritasi va Karyera sahifalari qo'shildi.
Lotin, kirill va rus til rejimlari UI hamda AI javoblariga ulandi.
API validatsiyasi, xavfsiz server xatolari, frontend timeout va qayta urinish holatlari qo'shildi.
APScheduler har oyning 1-kuni Mehnat kodeksini qayta ingest qiladi.
Mobil va desktop layoutlar yakuniy moslashtirildi.
Ishga tushirish
cp .env.example .env
docker compose up --build
Servislar:

Frontend: http://localhost:5173
Backend health: http://localhost:8000/api/health
Backend docs: http://localhost:8000/docs
Testlar
docker compose exec -T backend python -m unittest discover -s tests -v
docker compose exec -T frontend npm run build
Migratsiyalar
cd backend
alembic upgrade head
Lex.uz Ingest
Katalogni ko'rish:

docker compose exec -T backend python scripts/ingest.py --list-sources
Barcha kodeks va qonunlarni yig'ish:

docker compose exec -T backend python scripts/ingest.py --all
Tanlangan manbalarni yig'ish:

docker compose exec -T backend python scripts/ingest.py --codes family tax customs
DBga yozmasdan parser smoke-testi:

docker compose exec -T backend python scripts/ingest.py --all --dry-run --skip-embeddings
Yetishmayotgan embeddinglarni uzilib qolsa davom etadigan tarzda to'ldirish:

docker compose exec -T backend python scripts/embed_missing.py --batch-size 16
Manbalar va embedding holati: GET /api/legal/sources.

Eslatma: Fuqarolik kodeksi I va II qism sifatida ikki Lex.uz hujjatidan yig'iladi. 2026-yil 22-iyun holatida alohida kuchga kirgan Suv kodeksi Lex.uz'da mavjud emas; katalogga amaldagi Suv va suvdan foydalanish to'g'risidagi Qonun kiritilgan.

Institutsional qonunlar ham katalogga kiritilgan:

Advokatura to'g'risida;
Prokuratura to'g'risida;
Sudlar to'g'risida.
Oylik ingest
Backend ishga tushganda APScheduler avtomatik boshlanadi. Standart jadval:

hujjatlar: katalogdagi barcha kodekslar va suv qonunchiligi;
vaqt: har oyning 1-kuni, 03:00;
timezone: Asia/Tashkent;
bir vaqtda faqat bitta ingest.
.env orqali boshqarish:

SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Asia/Tashkent
MONTHLY_INGEST_HOUR=3
MONTHLY_INGEST_MINUTE=0
INGEST_BATCH_SIZE=8
Eslatma
ANTHROPIC_API_KEY kabi maxfiy qiymatlar faqat .env ichida turadi. Ularni frontendga yoki kodga yozmang.

My first project on GitHub
