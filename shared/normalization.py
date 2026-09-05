from __future__ import annotations

import re
import unicodedata

# Zero-width / invisible / directionality marks that carry no visible meaning:
# soft hyphen (00AD), the 200B-200F block, the 202A-202E block,
# word joiner (2060), BOM (FEFF).
_INVISIBLE_CODEPOINTS = (
    [0x00AD, 0x2060, 0xFEFF]
    + list(range(0x200B, 0x2010))
    + list(range(0x202A, 0x202F))
)
_INVISIBLE = re.compile("[" + "".join(chr(cp) for cp in _INVISIBLE_CODEPOINTS) + "]")
_NON_ALNUM = re.compile(r"[^A-Z0-9\s]")
_SPACE_RUN = re.compile(r"\s+")


def normalize_name(raw: str) -> str:
    """Normaliza um nome para servir de chave única (usado por ``subject`` e ``topic``).

    - remove acentos e cedilha (``ç`` -> ``c``);
    - remove caracteres invisíveis / zero-width;
    - deixa tudo maiúsculo;
    - remove qualquer caractere que não seja ``[A-Z0-9]`` ou espaço;
    - troca sequências de espaço por um único ``_``, sem ``_`` nas pontas.

    O resultado sempre casa ``^[A-Z0-9_]*$``. Uma entrada que não sobra nada
    (ex.: ``"!!!"``) devolve ``""``.
    """
    text = unicodedata.normalize("NFKD", raw)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = _INVISIBLE.sub("", text)
    text = text.upper()
    text = _NON_ALNUM.sub(" ", text)
    return _SPACE_RUN.sub("_", text.strip())


def normalize_many(raw_names: list[str], *, entity_label: str) -> dict[str, str]:
    """Mapeia cada nome cru distinto (ordem preservada) para sua forma normalizada.

    Levanta ``ValueError`` se algum nome normalizar para string vazia —
    ``entity_label`` identifica a entidade na mensagem (ex.: ``"matéria"``,
    ``"tópico"``).
    """
    normalized_name_by_raw_name = {
        raw_name: normalize_name(raw_name) for raw_name in dict.fromkeys(raw_names)
    }
    for raw_name, normalized_name in normalized_name_by_raw_name.items():
        if not normalized_name:
            raise ValueError(
                f"nome de {entity_label} inválido (normaliza para vazio): {raw_name!r}"
            )
    return normalized_name_by_raw_name
