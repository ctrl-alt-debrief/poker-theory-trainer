"""
One-time migration script: converts files(1)/ solver exports → data/ranges/30bb/
Run from the project root: python3 scripts/migrate_30bb_rfi.py

Source files use the situation name as the top-level key (e.g. "RFI") and include
zero-value actions. This script strips zeros and writes to the project standard format
({position}_{situation}.json with a "strategy" key) so the existing range_loader
picks them up without any changes.
"""
import json
import sys
from pathlib import Path

SOURCE_DIR = Path("files(1)")
OUTPUT_DIR = Path("data/ranges/30bb")

# Map source filename stem → canonical position string used by the engine
POSITION_MAP = {
    "UTG":  "UTG",
    "UTG1": "UTG+1",
    "UTG2": "UTG+2",
    "HJ":   "HJ",
    "CO":   "CO",
    "BTN":  "BTN",
    "SB":   "SB",
}


def strip_zeros(hand_dict: dict) -> dict:
    """Remove zero-frequency actions — keeps files concise and consistent with 25bb format."""
    return {action: freq for action, freq in hand_dict.items() if freq > 0}


def migrate():
    if not SOURCE_DIR.exists():
        print(f"ERROR: source directory '{SOURCE_DIR}' not found. Run from project root.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for stem, position in POSITION_MAP.items():
        source_path = SOURCE_DIR / f"{stem}.json"
        if not source_path.exists():
            print(f"  SKIP  {source_path} (not found)")
            continue

        data = json.loads(source_path.read_text())

        # The source files use the situation name as the top-level strategy key
        situation_key = data["_meta"]["situation"]  # e.g. "RFI"
        raw_strategy = data[situation_key]

        strategy = {hand: strip_zeros(freqs) for hand, freqs in raw_strategy.items()}

        payload = {
            "position":    position,
            "stack_depth": 30,
            "situation":   situation_key,
            "strategy":    strategy,
        }

        filename = f"{position.lower()}_{situation_key.lower()}.json"
        out_path = OUTPUT_DIR / filename
        out_path.write_text(json.dumps(payload, indent=2))
        print(f"  written: {out_path}  ({len(strategy)} hands)")

    print("\nMigration complete.")


if __name__ == "__main__":
    migrate()
