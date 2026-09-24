from recon.matcher import levenshtein, match_all


def test_levenshtein_basic_edits():
    assert levenshtein("BLR-001", "BLR-001") == 0
    assert levenshtein("BLR-O13", "BLR-013") == 1   # substitute
    assert levenshtein("BLR-14", "BLR-014") == 1    # insert
    assert levenshtein("BLR-0155", "BLR-015") == 1  # delete
    assert levenshtein("", "ABC") == 3


def test_exact_match_wins():
    [r] = match_all(["BLR-001"], {"BLR-001", "BLR-002"})
    assert (r.kind, r.parcel_id) == ("exact", "BLR-001")


def test_unique_fuzzy_match():
    [r] = match_all(["BLR-O13"], {"BLR-013", "BLR-099"})
    assert (r.kind, r.parcel_id, r.distance) == ("fuzzy", "BLR-013", 1)


def test_tie_is_ambiguous_not_guessed():
    [r] = match_all(["BLR-01Z"], {"BLR-012", "BLR-013"})
    assert r.kind == "ambiguous"
    assert r.candidates == ["BLR-012", "BLR-013"]


def test_fuzzy_cannot_steal_exactly_claimed_polygon():
    # BLR-999 is 2 edits from BLR-009, but BLR-009 already has its own row
    results = match_all(["BLR-009", "BLR-999"], {"BLR-009"})
    assert [r.kind for r in results] == ["exact", "none"]


def test_too_far_is_none():
    [r] = match_all(["MYS-101"], {"BLR-001"})
    assert r.kind == "none"
