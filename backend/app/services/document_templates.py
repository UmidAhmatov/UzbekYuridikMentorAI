from __future__ import annotations

from dataclasses import dataclass

from app.models import DocumentType


@dataclass(frozen=True)
class DocumentField:
    name: str
    label: str
    field_type: str = "text"
    required: bool = True
    placeholder: str | None = None
    help_text: str | None = None
    options: tuple[str, ...] = ()


@dataclass(frozen=True)
class DocumentTemplate:
    type: DocumentType
    title: str
    description: str
    legal_focus: str
    fields: tuple[DocumentField, ...]


DOCUMENT_TEMPLATES: dict[DocumentType, DocumentTemplate] = {
    DocumentType.davo_arizasi: DocumentTemplate(
        type=DocumentType.davo_arizasi,
        title="Da'vo arizasi",
        description="Fuqarolik nizosi bo'yicha sudga taqdim etiladigan da'vo arizasi.",
        legal_focus="fuqarolik sudi da'vo arizasi, da'vo talablari va dalillar",
        fields=(
            DocumentField("sud_nomi", "Sud nomi", placeholder="Masalan: Chilonzor tumanlararo fuqarolik sudi"),
            DocumentField("davogar", "Da'vogar F.I.Sh. yoki tashkilot nomi"),
            DocumentField("davogar_manzili", "Da'vogar manzili"),
            DocumentField("javobgar", "Javobgar F.I.Sh. yoki tashkilot nomi"),
            DocumentField("javobgar_manzili", "Javobgar manzili"),
            DocumentField("nizo_holati", "Nizo tafsilotlari", "textarea", help_text="Voqealarni sana va ketma-ketlikda bayon qiling."),
            DocumentField("talab", "Suddan so'raladigan talab", "textarea"),
            DocumentField("dalillar", "Dalillar va ilovalar", "textarea"),
            DocumentField("davo_qiymati", "Da'vo qiymati", required=False, placeholder="Masalan: 12 500 000 so'm"),
        ),
    ),
    DocumentType.shikoyat: DocumentTemplate(
        type=DocumentType.shikoyat,
        title="Shikoyat",
        description="Davlat organi, tashkilot yoki mansabdor shaxs qarori va harakati ustidan shikoyat.",
        legal_focus="murojaat va shikoyat berish tartibi, muddatlar va vakolatli organ",
        fields=(
            DocumentField("qabul_qiluvchi", "Shikoyat yuboriladigan organ yoki mansabdor shaxs"),
            DocumentField("shikoyatchi", "Shikoyatchi F.I.Sh. yoki tashkilot nomi"),
            DocumentField("aloqa", "Manzil va aloqa ma'lumotlari"),
            DocumentField("shikoyat_predmeti", "Shikoyat qilinayotgan qaror yoki harakat", "textarea"),
            DocumentField("holatlar", "Holatlar", "textarea", help_text="Muhim sanalar va avvalgi murojaatlarni kiriting."),
            DocumentField("talab", "So'raladigan yechim", "textarea"),
            DocumentField("ilovalar", "Ilovalar", "textarea", required=False),
        ),
    ),
    DocumentType.ishonchnoma: DocumentTemplate(
        type=DocumentType.ishonchnoma,
        title="Ishonchnoma",
        description="Boshqa shaxsga muayyan harakatlarni bajarish vakolatini beruvchi hujjat.",
        legal_focus="ishonchnoma shakli, vakolatlar, amal qilish muddati va notarial tasdiq",
        fields=(
            DocumentField("ishonch_bildiruvchi", "Ishonch bildiruvchi F.I.Sh."),
            DocumentField("beruvchi_hujjat", "Pasport yoki ID ma'lumotlari"),
            DocumentField("beruvchi_manzil", "Yashash manzili"),
            DocumentField("vakil", "Vakil F.I.Sh."),
            DocumentField("vakil_hujjat", "Vakilning pasport yoki ID ma'lumotlari"),
            DocumentField("vakolatlar", "Beriladigan vakolatlar", "textarea"),
            DocumentField("amal_muddati", "Amal qilish muddati", placeholder="Masalan: 2027-yil 1-iyungacha"),
            DocumentField(
                "qayta_ishonish",
                "Qayta ishonib topshirish huquqi",
                "select",
                options=("Berilmaydi", "Beriladi"),
            ),
        ),
    ),
    DocumentType.mehnat_shartnomasi: DocumentTemplate(
        type=DocumentType.mehnat_shartnomasi,
        title="Mehnat shartnomasi",
        description="Ish beruvchi va xodim o'rtasidagi mehnat munosabatlarini belgilovchi shartnoma.",
        legal_focus="mehnat shartnomasi, ish vaqti, ish haqi, ta'til va bekor qilish asoslari",
        fields=(
            DocumentField("ish_beruvchi", "Ish beruvchi nomi va rekvizitlari"),
            DocumentField("xodim", "Xodim F.I.Sh."),
            DocumentField("xodim_hujjat", "Xodimning pasport yoki ID ma'lumotlari"),
            DocumentField("lavozim", "Lavozim"),
            DocumentField("ish_joyi", "Ish joyi"),
            DocumentField("vazifalar", "Asosiy mehnat vazifalari", "textarea"),
            DocumentField("ish_haqi", "Ish haqi va to'lov tartibi"),
            DocumentField("ish_vaqti", "Ish vaqti va dam olish tartibi"),
            DocumentField("boshlanish_sanasi", "Ish boshlash sanasi", "date"),
            DocumentField("muddat", "Shartnoma muddati", "select", options=("Nomuayyan muddatga", "Muayyan muddatga")),
            DocumentField("maxsus_shartlar", "Qo'shimcha shartlar", "textarea", required=False),
        ),
    ),
    DocumentType.ijara_shartnomasi: DocumentTemplate(
        type=DocumentType.ijara_shartnomasi,
        title="Ijara shartnomasi",
        description="Ko'chmas mulk yoki boshqa mol-mulkni vaqtincha foydalanishga berish shartnomasi.",
        legal_focus="ijara shartnomasi, ijara haqi, mulkni topshirish va taraflar javobgarligi",
        fields=(
            DocumentField("ijaraga_beruvchi", "Ijaraga beruvchi F.I.Sh. yoki tashkilot"),
            DocumentField("ijarachi", "Ijarachi F.I.Sh. yoki tashkilot"),
            DocumentField("obyekt", "Ijara obyekti"),
            DocumentField("obyekt_manzili", "Obyekt manzili va tavsifi"),
            DocumentField("muddat", "Ijara muddati"),
            DocumentField("ijara_haqi", "Ijara haqi"),
            DocumentField("tolov_tartibi", "To'lov muddati va usuli"),
            DocumentField("depozit", "Depozit", required=False),
            DocumentField("kommunal_tolovlar", "Kommunal va boshqa xarajatlar kim tomonidan to'lanadi"),
            DocumentField("maxsus_shartlar", "Qo'shimcha shartlar", "textarea", required=False),
        ),
    ),
    DocumentType.sud_arizasi: DocumentTemplate(
        type=DocumentType.sud_arizasi,
        title="Sudga ariza",
        description="Da'vo bo'lmagan masala yuzasidan sudga taqdim etiladigan ariza.",
        legal_focus="sudga ariza berish, alohida tartibda ish yuritish, talab va ilovalar",
        fields=(
            DocumentField("sud_nomi", "Sud nomi"),
            DocumentField("arizachi", "Arizachi F.I.Sh. yoki tashkilot nomi"),
            DocumentField("arizachi_manzili", "Arizachi manzili va aloqa ma'lumotlari"),
            DocumentField("manfaatdor_shaxslar", "Manfaatdor shaxslar", "textarea", required=False),
            DocumentField("ariza_mazmuni", "Masala va holatlar", "textarea"),
            DocumentField("talab", "Suddan so'raladigan talab", "textarea"),
            DocumentField("dalillar", "Dalillar va ilovalar", "textarea"),
        ),
    ),
}


def get_document_template(document_type: DocumentType) -> DocumentTemplate:
    return DOCUMENT_TEMPLATES[document_type]


def validate_document_values(
    template: DocumentTemplate,
    values: dict[str, str],
) -> dict[str, str]:
    allowed_fields = {field.name: field for field in template.fields}
    normalized: dict[str, str] = {}

    for name, value in values.items():
        if name not in allowed_fields:
            continue
        clean_value = str(value).strip()
        if len(clean_value) > 8000:
            raise ValueError(f"'{allowed_fields[name].label}' maydoni juda uzun.")
        if clean_value:
            normalized[name] = clean_value

    missing = [
        field.label
        for field in template.fields
        if field.required and not normalized.get(field.name)
    ]
    if missing:
        raise ValueError(f"Majburiy maydonlarni to'ldiring: {', '.join(missing)}.")

    return normalized


def build_document_input(template: DocumentTemplate, values: dict[str, str]) -> str:
    field_map = {field.name: field for field in template.fields}
    lines = [
        f"Hujjat turi: {template.title}",
        f"Maqsad: {template.description}",
        "",
        "Foydalanuvchi ma'lumotlari:",
    ]
    for name, value in values.items():
        lines.append(f"- {field_map[name].label}: {value}")
    return "\n".join(lines)

