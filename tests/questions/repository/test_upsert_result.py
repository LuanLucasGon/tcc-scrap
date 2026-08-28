from questions.repository.upsert_result import UpsertResult


def test_counts_inserts_when_no_ids_exist_yet():
    result = UpsertResult.from_ids(incoming_ids=["Q1", "Q2", "Q3"], existing_ids=[])

    assert result == UpsertResult(inserted=3, updated=0)


def test_counts_updates_for_ids_already_present():
    result = UpsertResult.from_ids(
        incoming_ids=["Q1", "Q2", "Q3"], existing_ids=["Q2", "Q3"]
    )

    assert result == UpsertResult(inserted=1, updated=2)


def test_deduplicates_repeated_incoming_ids():
    result = UpsertResult.from_ids(
        incoming_ids=["Q1", "Q1", "Q2"], existing_ids=["Q1"]
    )

    assert result == UpsertResult(inserted=1, updated=1)
