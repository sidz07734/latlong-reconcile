"""Turn a MatchResult + areas into one of the four verdicts, with a reason."""
import math

from recon.matcher import MatchResult

MATCH = "Match"
ID_MATCH_AREA_MISMATCH = "IdMatchAreaMismatch"
FUZZY_MATCH = "FuzzyMatch"
NO_MATCH = "NoMatch"
DEFAULT_TOLERANCE = 0.10  # ±10%


def _is_missing(value: float) -> bool:
    return value is None or math.isnan(value)


def area_check(csv_area: float, map_area: float, tolerance: float) -> tuple[bool, str]:
    """Compare CSV area to map area. Returns (ok, human-readable explanation)."""
    if _is_missing(csv_area):
        return False, "area_sqm missing or non-numeric in CSV, cannot verify"
    diff_pct = (csv_area - map_area) / map_area * 100
    ok = abs(diff_pct) <= tolerance * 100
    word = "within" if ok else "outside"
    return ok, (f"CSV {csv_area:g} m² vs map {map_area:g} m² "
                f"({diff_pct:+.1f}%, {word} ±{tolerance * 100:g}%)")


def decide(match: MatchResult, csv_area: float, map_areas: dict[str, float],
           tolerance: float = DEFAULT_TOLERANCE) -> tuple[str, str]:
    """Return (verdict, reason) for one CSV row."""
    if match.kind == "exact":
        ok, detail = area_check(csv_area, map_areas[match.parcel_id], tolerance)
        return (MATCH if ok else ID_MATCH_AREA_MISMATCH), f"Exact ID match; {detail}"

    if match.kind == "fuzzy":
        ok, detail = area_check(csv_area, map_areas[match.parcel_id], tolerance)
        if not ok and not _is_missing(csv_area):
            # Similar ID but clearly different size: not enough evidence it's the same parcel
            return NO_MATCH, (f"Closest ID {match.parcel_id} (edit distance {match.distance}) "
                              f"rejected: {detail}")
        return FUZZY_MATCH, (f"Fuzzy ID match to {match.parcel_id} "
                             f"(edit distance {match.distance}); {detail}; needs human review")

    if match.kind == "ambiguous":
        return NO_MATCH, (f"Ambiguous: {len(match.candidates)} map IDs at edit distance "
                          f"{match.distance} ({', '.join(match.candidates)}); not guessing")

    return NO_MATCH, "No unclaimed map ID within the fuzzy edit-distance limit"