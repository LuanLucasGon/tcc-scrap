import re

import pytest

from shared.normalization import normalize_many, normalize_name


def test_removes_accents_and_uppercases():
    assert normalize_name("Matemática") == "MATEMATICA"
    assert normalize_name("História") == "HISTORIA"


def test_converts_cedilla_lower_and_upper():
    assert normalize_name("Educação") == "EDUCACAO"
    assert normalize_name("EDUCAÇÃO") == "EDUCACAO"


def test_spaces_become_single_underscore_and_are_trimmed():
    result = normalize_name("  Matemática   Financeira  ")
    assert result == "MATEMATICA_FINANCEIRA"


def test_punctuation_is_removed_not_kept():
    assert (
        normalize_name("Português: Interpretação de Texto")
        == "PORTUGUES_INTERPRETACAO_DE_TEXTO"
    )
    assert normalize_name("História  --  Geral") == "HISTORIA_GERAL"
    assert normalize_name("Física/Química") == "FISICA_QUIMICA"


def test_strips_zero_width_and_invisible_characters():
    raw = "Ma​temática﻿­"
    assert normalize_name(raw) == "MATEMATICA"


def test_non_breaking_space_is_treated_as_space():
    assert normalize_name("Matemática Financeira") == "MATEMATICA_FINANCEIRA"


def test_no_leading_or_trailing_underscore():
    result = normalize_name("- História -")
    assert result == "HISTORIA"
    assert not result.startswith("_")
    assert not result.endswith("_")


def test_result_only_contains_allowed_characters():
    assert re.fullmatch(
        r"[A-Z0-9_]*", normalize_name("Raciocínio Lógico-Matemático (2024)")
    )


def test_is_idempotent():
    once = normalize_name("Língua Portuguesa & Literatura")
    assert normalize_name(once) == once


def test_string_that_normalizes_to_empty():
    assert normalize_name("!!!") == ""
    assert normalize_name("   ") == ""


def test_normalize_many_maps_each_raw_name_to_its_normalized_form():
    result = normalize_many(["Matemática", "História"], entity_label="matéria")

    assert result == {"Matemática": "MATEMATICA", "História": "HISTORIA"}


def test_normalize_many_dedupes_repeated_raw_names_preserving_first_order():
    result = normalize_many(["Álgebra", "Álgebra", "Geometria"], entity_label="tópico")

    assert list(result.keys()) == ["Álgebra", "Geometria"]


def test_normalize_many_raises_when_a_name_normalizes_to_empty():
    with pytest.raises(ValueError):
        normalize_many(["Matemática", "!!!"], entity_label="matéria")


def test_normalize_many_error_message_includes_the_entity_label():
    with pytest.raises(ValueError, match="tópico"):
        normalize_many(["!!!"], entity_label="tópico")
