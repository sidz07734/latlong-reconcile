import math

from recon.matcher import MatchResult
from recon.verdict import decide

AREAS = {"BLR-001": 1000.0}


def test_exact_and_area_within_tolerance_is_match():
    verdict, _ = decide(MatchResult("exact", "BLR-001"), 1050, AREAS)
    assert verdict == "Match"


def test_exact_but_area_off_is_mismatch():
    verdict, reason = decide(MatchResult("exact", "BLR-001"), 1500, AREAS)
    assert verdict == "IdMatchAreaMismatch"
    assert "+50.0%" in reason


def test_tolerance_boundary_is_inclusive():
    verdict, _ = decide(MatchResult("exact", "BLR-001"), 1100, AREAS, tolerance=0.10)
    assert verdict == "Match"


def test_missing_area_is_mismatch_with_reason():
    verdict, reason = decide(MatchResult("exact", "BLR-001"), math.nan, AREAS)
    assert verdict == "IdMatchAreaMismatch"
    assert "missing" in reason


def test_fuzzy_is_always_flagged_for_review():
    verdict, reason = decide(MatchResult("fuzzy", "BLR-001", distance=1), 1000, AREAS)
    assert verdict == "FuzzyMatch"
    assert "human review" in reason


def test_ambiguous_becomes_nomatch_listing_candidates():
    m = MatchResult("ambiguous", distance=1, candidates=["BLR-012", "BLR-013"])
    verdict, reason = decide(m, 1000, AREAS)
    assert verdict == "NoMatch"
    assert "BLR-012, BLR-013" in reason
