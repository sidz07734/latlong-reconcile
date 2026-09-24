"""CLI entry point: python reconcile.py --csv X --geojson Y --out ./report/"""
import argparse
import logging
import sys
from pathlib import Path

from recon.pipeline import run
from recon.report import summary_line, write_csv, write_geojson

log = logging.getLogger("reconcile")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Reconcile parcel CSV records with GeoJSON polygons.")
    p.add_argument("--csv", required=True, help="Parcel records CSV")
    p.add_argument("--geojson", required=True, help="Parcel polygons GeoJSON")
    p.add_argument("--out", default="./report/", help="Output folder (default: ./report/)")
    p.add_argument("--tolerance", type=float, default=10.0,
                   help="Allowed area difference in percent (default: 10)")
    p.add_argument("--max-distance", type=int, default=2,
                   help="Max Levenshtein distance for fuzzy ID match (default: 2)")
    args = p.parse_args(argv)
    if args.tolerance < 0 or args.max_distance < 0:
        p.error("--tolerance and --max-distance must be non-negative")
    return args


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logging.getLogger("pyogrio").setLevel(logging.WARNING)  # silence "Created N records"
    args = parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        rows, polygons = run(args.csv, args.geojson,
                             tolerance=args.tolerance / 100, max_distance=args.max_distance)
    except (FileNotFoundError, ValueError) as exc:
        log.error(exc)
        return 1

    log.info("Wrote %s", write_csv(rows, out_dir))
    log.info("Wrote %s", write_geojson(polygons, out_dir))
    log.info("Summary: %s", summary_line(rows, polygons))
    return 0


if __name__ == "__main__":
    sys.exit(main())