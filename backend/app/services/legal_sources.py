from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LegalSourceDefinition:
    key: str
    title: str
    lex_id: str
    category: str = "code"
    search_terms: tuple[str, ...] = ()

    @property
    def source_id(self) -> str:
        return f"lex-{self.lex_id.lstrip('-')}"

    @property
    def url(self) -> str:
        return f"https://lex.uz/docs/{self.lex_id}"


LEGAL_SOURCES: tuple[LegalSourceDefinition, ...] = (
    LegalSourceDefinition(
        "administrative_liability",
        "Ma'muriy javobgarlik to'g'risidagi kodeks",
        "-97664",
    ),
    LegalSourceDefinition("criminal", "Jinoyat kodeksi", "-111453"),
    LegalSourceDefinition("civil_part_1", "Fuqarolik kodeksi, birinchi qism", "-111189"),
    LegalSourceDefinition("civil_part_2", "Fuqarolik kodeksi, ikkinchi qism", "-180552"),
    LegalSourceDefinition("civil_procedure", "Fuqarolik protsessual kodeksi", "-3517337"),
    LegalSourceDefinition("economic_procedure", "Iqtisodiy protsessual kodeksi", "-3523891"),
    LegalSourceDefinition("family", "Oila kodeksi", "-104720"),
    LegalSourceDefinition("land", "Yer kodeksi", "-152653"),
    LegalSourceDefinition("housing", "Uy-joy kodeksi", "-106136"),
    LegalSourceDefinition("labor", "Mehnat kodeksi", "-6257288"),
    LegalSourceDefinition("criminal_procedure", "Jinoyat-protsessual kodeksi", "-111460"),
    LegalSourceDefinition("penal_enforcement", "Jinoyat-ijroiya kodeksi", "-163629"),
    LegalSourceDefinition(
        "administrative_court",
        "Ma'muriy sud ishlarini yuritish to'g'risidagi kodeks",
        "-3527353",
    ),
    LegalSourceDefinition("tax", "Soliq kodeksi", "-4674902"),
    LegalSourceDefinition("budget", "Budjet kodeksi", "-2304138"),
    LegalSourceDefinition("customs", "Bojxona kodeksi", "-2876354"),
    LegalSourceDefinition(
        "water",
        "Suv va suvdan foydalanish to'g'risida",
        "-12328",
        category="law",
    ),
    LegalSourceDefinition("urban_planning", "Shaharsozlik kodeksi", "-5307951"),
    LegalSourceDefinition(
        "advocacy",
        "Advokatura to'g'risida",
        "-54503",
        category="law",
        search_terms=("advokatura", "advokatlar to'g'risida"),
    ),
    LegalSourceDefinition(
        "prosecutor_office",
        "Prokuratura to'g'risida",
        "-106197",
        category="law",
        search_terms=("prokuratura",),
    ),
    LegalSourceDefinition(
        "courts",
        "Sudlar to'g'risida",
        "-5534923",
        category="law",
        search_terms=("sudlar to'g'risida",),
    ),
)

LEGAL_SOURCE_BY_KEY = {source.key: source for source in LEGAL_SOURCES}


def get_legal_sources(keys: list[str] | None = None) -> list[LegalSourceDefinition]:
    if not keys:
        return list(LEGAL_SOURCES)
    return [LEGAL_SOURCE_BY_KEY[key] for key in keys]
