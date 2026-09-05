import re

from subject.normalization import normalize_subject_name


def test_removes_accents_and_uppercases():
    assert normalize_subject_name("Matemática") == "MATEMATICA"
    assert normalize_subject_name("História") == "HISTORIA"


def test_converts_cedilla_lower_and_upper():
    assert normalize_subject_name("Educação") == "EDUCACAO"
    assert normalize_subject_name("EDUCAÇÃO") == "EDUCACAO"


def test_spaces_become_single_underscore_and_are_trimmed():
    result = normalize_subject_name("  Matemática   Financeira  ")
    assert result == "MATEMATICA_FINANCEIRA"


def test_punctuation_is_removed_not_kept():
    assert (
        normalize_subject_name("Português: Interpretação de Texto")
        == "PORTUGUES_INTERPRETACAO_DE_TEXTO"
    )
    assert normalize_subject_name("História  --  Geral") == "HISTORIA_GERAL"
    assert normalize_subject_name("Física/Química") == "FISICA_QUIMICA"


def test_strips_zero_width_and_invisible_characters():
    raw = "Ma​temática﻿­"
    assert normalize_subject_name(raw) == "MATEMATICA"


def test_non_breaking_space_is_treated_as_space():
    assert normalize_subject_name("Matemática Financeira") == "MATEMATICA_FINANCEIRA"


def test_no_leading_or_trailing_underscore():
    result = normalize_subject_name("- História -")
    assert result == "HISTORIA"
    assert not result.startswith("_")
    assert not result.endswith("_")


def test_result_only_contains_allowed_characters():
    assert re.fullmatch(
        r"[A-Z0-9_]*", normalize_subject_name("Raciocínio Lógico-Matemático (2024)")
    )


def test_is_idempotent():
    once = normalize_subject_name("Língua Portuguesa & Literatura")
    assert normalize_subject_name(once) == once


def test_string_that_normalizes_to_empty():
    assert normalize_subject_name("!!!") == ""
    assert normalize_subject_name("   ") == ""
