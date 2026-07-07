from __future__ import annotations

from app.schemas.mentor import ResponseLanguage


RU_TRANSLATIONS = {
    "Da'vo arizasi": "Исковое заявление",
    "Fuqarolik nizosi bo'yicha sudga taqdim etiladigan da'vo arizasi.": "Исковое заявление в суд по гражданскому спору.",
    "Sud nomi": "Наименование суда",
    "Masalan: Chilonzor tumanlararo fuqarolik sudi": "Например: Чиланзарский межрайонный суд по гражданским делам",
    "Da'vogar F.I.Sh. yoki tashkilot nomi": "Ф.И.О. истца или наименование организации",
    "Da'vogar manzili": "Адрес истца",
    "Javobgar F.I.Sh. yoki tashkilot nomi": "Ф.И.О. ответчика или наименование организации",
    "Javobgar manzili": "Адрес ответчика",
    "Nizo tafsilotlari": "Обстоятельства спора",
    "Voqealarni sana va ketma-ketlikda bayon qiling.": "Опишите события по датам и в хронологическом порядке.",
    "Suddan so'raladigan talab": "Требование к суду",
    "Dalillar va ilovalar": "Доказательства и приложения",
    "Da'vo qiymati": "Цена иска",
    "Masalan: 12 500 000 so'm": "Например: 12 500 000 сумов",
    "Shikoyat": "Жалоба",
    "Davlat organi, tashkilot yoki mansabdor shaxs qarori va harakati ustidan shikoyat.": "Жалоба на решение или действие государственного органа, организации или должностного лица.",
    "Shikoyat yuboriladigan organ yoki mansabdor shaxs": "Орган или должностное лицо, которому направляется жалоба",
    "Shikoyatchi F.I.Sh. yoki tashkilot nomi": "Ф.И.О. заявителя или наименование организации",
    "Manzil va aloqa ma'lumotlari": "Адрес и контактные данные",
    "Shikoyat qilinayotgan qaror yoki harakat": "Обжалуемое решение или действие",
    "Holatlar": "Обстоятельства",
    "Muhim sanalar va avvalgi murojaatlarni kiriting.": "Укажите важные даты и предыдущие обращения.",
    "So'raladigan yechim": "Просимое решение",
    "Ilovalar": "Приложения",
    "Ishonchnoma": "Доверенность",
    "Boshqa shaxsga muayyan harakatlarni bajarish vakolatini beruvchi hujjat.": "Документ, предоставляющий другому лицу полномочия на совершение определённых действий.",
    "Ishonch bildiruvchi F.I.Sh.": "Ф.И.О. доверителя",
    "Pasport yoki ID ma'lumotlari": "Паспортные или ID-данные",
    "Yashash manzili": "Адрес проживания",
    "Vakil F.I.Sh.": "Ф.И.О. представителя",
    "Vakilning pasport yoki ID ma'lumotlari": "Паспортные или ID-данные представителя",
    "Beriladigan vakolatlar": "Предоставляемые полномочия",
    "Amal qilish muddati": "Срок действия",
    "Masalan: 2027-yil 1-iyungacha": "Например: до 1 июня 2027 года",
    "Qayta ishonib topshirish huquqi": "Право передоверия",
    "Berilmaydi": "Не предоставляется",
    "Beriladi": "Предоставляется",
    "Mehnat shartnomasi": "Трудовой договор",
    "Ish beruvchi va xodim o'rtasidagi mehnat munosabatlarini belgilovchi shartnoma.": "Договор, регулирующий трудовые отношения между работодателем и работником.",
    "Ish beruvchi nomi va rekvizitlari": "Наименование и реквизиты работодателя",
    "Xodim F.I.Sh.": "Ф.И.О. работника",
    "Xodimning pasport yoki ID ma'lumotlari": "Паспортные или ID-данные работника",
    "Lavozim": "Должность",
    "Ish joyi": "Место работы",
    "Asosiy mehnat vazifalari": "Основные трудовые обязанности",
    "Ish haqi va to'lov tartibi": "Заработная плата и порядок выплаты",
    "Ish vaqti va dam olish tartibi": "Режим рабочего времени и отдыха",
    "Ish boshlash sanasi": "Дата начала работы",
    "Shartnoma muddati": "Срок договора",
    "Nomuayyan muddatga": "На неопределённый срок",
    "Muayyan muddatga": "На определённый срок",
    "Qo'shimcha shartlar": "Дополнительные условия",
    "Ijara shartnomasi": "Договор аренды",
    "Ko'chmas mulk yoki boshqa mol-mulkni vaqtincha foydalanishga berish shartnomasi.": "Договор о передаче недвижимости или иного имущества во временное пользование.",
    "Ijaraga beruvchi F.I.Sh. yoki tashkilot": "Ф.И.О. или организация арендодателя",
    "Ijarachi F.I.Sh. yoki tashkilot": "Ф.И.О. или организация арендатора",
    "Ijara obyekti": "Объект аренды",
    "Obyekt manzili va tavsifi": "Адрес и описание объекта",
    "Ijara muddati": "Срок аренды",
    "Ijara haqi": "Арендная плата",
    "To'lov muddati va usuli": "Срок и способ оплаты",
    "Depozit": "Депозит",
    "Kommunal va boshqa xarajatlar kim tomonidan to'lanadi": "Кто оплачивает коммунальные и иные расходы",
    "Sudga ariza": "Заявление в суд",
    "Da'vo bo'lmagan masala yuzasidan sudga taqdim etiladigan ariza.": "Заявление в суд по вопросу, не являющемуся исковым спором.",
    "Arizachi F.I.Sh. yoki tashkilot nomi": "Ф.И.О. заявителя или наименование организации",
    "Arizachi manzili va aloqa ma'lumotlari": "Адрес и контактные данные заявителя",
    "Manfaatdor shaxslar": "Заинтересованные лица",
    "Masala va holatlar": "Вопрос и обстоятельства",
}


def localize_text(text: str | None, language: ResponseLanguage) -> str | None:
    if text is None or language is ResponseLanguage.uz_latin:
        return text
    if language is ResponseLanguage.ru:
        return RU_TRANSLATIONS.get(text, text)
    return uzbek_latin_to_cyrillic(text)


def uzbek_latin_to_cyrillic(text: str) -> str:
    digraphs = {
        "O‘": "Ў",
        "O'": "Ў",
        "Oʻ": "Ў",
        "o‘": "ў",
        "o'": "ў",
        "oʻ": "ў",
        "G‘": "Ғ",
        "G'": "Ғ",
        "Gʻ": "Ғ",
        "g‘": "ғ",
        "g'": "ғ",
        "gʻ": "ғ",
        "Sh": "Ш",
        "sh": "ш",
        "Ch": "Ч",
        "ch": "ч",
        "Yo": "Ё",
        "yo": "ё",
        "Yu": "Ю",
        "yu": "ю",
        "Ya": "Я",
        "ya": "я",
        "Ye": "Е",
        "ye": "е",
    }
    letters = str.maketrans(
        {
            "A": "А", "a": "а", "B": "Б", "b": "б", "D": "Д", "d": "д",
            "E": "Е", "e": "е", "F": "Ф", "f": "ф", "H": "Ҳ", "h": "ҳ",
            "I": "И", "i": "и", "J": "Ж", "j": "ж", "K": "К", "k": "к",
            "L": "Л", "l": "л", "M": "М", "m": "м", "N": "Н", "n": "н",
            "O": "О", "o": "о", "P": "П", "p": "п", "Q": "Қ", "q": "қ",
            "R": "Р", "r": "р", "S": "С", "s": "с", "T": "Т", "t": "т",
            "U": "У", "u": "у", "V": "В", "v": "в", "X": "Х", "x": "х",
            "Y": "Й", "y": "й", "Z": "З", "z": "з",
        }
    )
    localized = text
    for latin, cyrillic in digraphs.items():
        localized = localized.replace(latin, cyrillic)
    localized = localized.replace("'", "ъ").replace("’", "ъ").replace("‘", "ъ")
    return localized.translate(letters)
