"""
migrate_80bb_ranges.py

Converts raw 80bb source files (80bb/*.json) into the engine's range format
and writes them to data/ranges/80bb/.

Source format:
    { "_meta": {...}, "RFI": { "AA": {"raise": 1.0, ...}, ... } }

Target format (matches range_loader.py expectations):
    { "position": "...", "stack_depth": 80, "situation": "RFI",
      "strategy": { "AA": {"raise": 1.0, ...}, ... } }

Position filename mapping:
    UTG.json  -> utg_rfi.json
    UTG1.json -> utg+1_rfi.json
    UTG2.json -> utg+2_rfi.json
    HJ.json   -> hj_rfi.json
    CO.json   -> co_rfi.json
    BTN.json  -> btn_rfi.json
    SB.json   -> sb_rfi.json
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "80bb"
TARGET_DIR = REPO_ROOT / "data" / "ranges" / "80bb"

POSITION_MAP = {
    "UTG":  ("UTG",   "utg"),
    "UTG1": ("UTG+1", "utg+1"),
    "UTG2": ("UTG+2", "utg+2"),
    "HJ":   ("HJ",    "hj"),
    "CO":   ("CO",    "co"),
    "BTN":  ("BTN",   "btn"),
    "SB":   ("SB",    "sb"),
}


def migrate() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    for source_stem, (canonical_position, file_prefix) in POSITION_MAP.items():
        source_path = SOURCE_DIR / f"{source_stem}.json"
        if not source_path.exists():
            print(f"SKIP {source_path} — not found")
            continue

        source = json.loads(source_path.read_text())
        situation = "RFI"

        output = {
            "position": canonical_position,
            "stack_depth": 80,
            "situation": situation,
            "strategy": source[situation],
        }

        target_path = TARGET_DIR / f"{file_prefix}_{situation.lower()}.json"
        target_path.write_text(json.dumps(output, indent=2))
        print(f"OK  {source_path.name} -> {target_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    migrate()
