from main import correlate_answers_by_order, extract_answers_from_html


def _html_with_answers(*, heading: bool = True) -> str:
    respostas_block = (
        "<div>Respostas</div>"
        "<div>1:</div><div>A</div>"
        "<div>2:</div><div>D</div>"
        "<div>8:</div><div>X</div>"
        "<div>9:</div><div>A</div>"
        if heading
        else ""
    )
    return f"""
    <html><body>
    <div>Lista de questões</div>
    {respostas_block}
    </body></html>
    """


def test_extract_answers_from_html_parses_number_letter_pairs():
    answers = extract_answers_from_html(_html_with_answers())

    assert answers == {1: "A", 2: "D", 8: "X", 9: "A"}


def test_extract_answers_from_html_returns_empty_dict_when_no_respostas_block():
    answers = extract_answers_from_html(_html_with_answers(heading=False))

    assert answers == {}


def test_extract_answers_from_html_keeps_non_a_to_e_markers_like_annulled_question():
    answers = extract_answers_from_html(_html_with_answers())

    # "X" (questão anulada) precisa ser mantida — descartá-la desalinharia a
    # correlação por ordem de todas as questões seguintes na mesma página.
    assert answers[8] == "X"


def test_correlate_answers_by_order_maps_by_relative_rank_not_by_number_value():
    answers = {1: "A", 2: "D", 8: "X", 9: "A"}

    result = correlate_answers_by_order(answers, count=4)

    assert result == ["A", "D", "X", "A"]


def test_correlate_answers_by_order_fills_missing_tail_with_none():
    result = correlate_answers_by_order({1: "A"}, count=3)

    assert result == ["A", None, None]


def test_correlate_answers_by_order_returns_empty_list_for_zero_count():
    assert correlate_answers_by_order({}, count=0) == []
