"""Match CSV parcel IDs to map IDs: exact first, then fuzzy (Levenshtein)."""
from dataclasses import dataclass, field

MAX_FUZZY_DISTANCE = 2


@dataclass
class MatchResult:
    kind: str                      # "exact" | "fuzzy" | "ambiguous" | "none"
    parcel_id: str | None = None   # the map ID we matched to
    distance: int = 0              # edit distance (0 for exact)
    candidates: list[str] = field(default_factory=list)


def levenshtein(a: str, b: str) -> int:
    """Minimum single-character edits (insert/delete/substitute) to turn a into b."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            curr.append(min(
                prev[j] + 1,               # delete
                curr[j - 1] + 1,           # insert
                prev[j - 1] + (ca != cb),  # substitute (free if same char)
            ))
        prev = curr
    return prev[-1]


def fuzzy_match(csv_id: str, pool: set[str], max_distance: int) -> MatchResult:
    """Closest ID within max_distance. A tie for closest is 'ambiguous'."""
    scored = [(levenshtein(csv_id, pid), pid) for pid in pool]
    close = [(d, pid) for d, pid in scored if d <= max_distance]
    if not close:
        return MatchResult("none")

    best = min(d for d, _ in close)
    winners = sorted(pid for d, pid in close if d == best)
    if len(winners) > 1:
        return MatchResult("ambiguous", distance=best, candidates=winners)
    return MatchResult("fuzzy", parcel_id=winners[0], distance=best)


def match_all(csv_ids: list[str], map_ids: set[str],
              max_distance: int = MAX_FUZZY_DISTANCE) -> list[MatchResult]:
    """Match every CSV ID. Polygons already claimed by an exact match are
    excluded from fuzzy search: a typo shouldn't steal a parcel that has an owner."""
    exact_claimed = set(csv_ids) & map_ids
    fuzzy_pool = map_ids - exact_claimed

    results = []
    for cid in csv_ids:
        if cid in map_ids:
            results.append(MatchResult("exact", parcel_id=cid))
        else:
            results.append(fuzzy_match(cid, fuzzy_pool, max_distance))
    return results