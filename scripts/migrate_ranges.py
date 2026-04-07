"""
One-time migration script: converts Python range dicts → JSON files under data/ranges/
Run from the project root: python3 scripts/migrate_ranges.py
"""
import json
import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.ranges import utg_25bb, hj_25bb, co_25bb, btn_25bb, sb_25bb, bb_25bb

MODULES = {
    "UTG": utg_25bb,
    "HJ":  hj_25bb,
    "CO":  co_25bb,
    "BTN": btn_25bb,
    "SB":  sb_25bb,
    "BB":  bb_25bb,
}

# (situation value, module attribute name)
SITUATIONS = [
    ("RFI",      "OPEN_STRATEGY"),
    ("vs_shove", "CALL_SHOVE_STRATEGY"),
]

output_dir = Path("data/ranges/25bb")
output_dir.mkdir(parents=True, exist_ok=True)

for position, module in MODULES.items():
    for situation, attr in SITUATIONS:
        strategy = getattr(module, attr, {})
        if not strategy:
            continue

        payload = {
            "position":    position,
            "stack_depth": 25,
            "situation":   situation,
            "strategy":    strategy,
        }

        filename = f"{position.lower()}_{situation.lower()}.json"
        path = output_dir / filename
        path.write_text(json.dumps(payload, indent=2))
        print(f"  written: {path}")

# BB defend is its own situation — position is always BB
bb_defend_payload = {
    "position":    "BB",
    "stack_depth": 25,
    "situation":   "bb_defend",
    "strategy":    bb_25bb.DEFEND_STRATEGY,
}
path = output_dir / "bb_bb_defend.json"
path.write_text(json.dumps(bb_defend_payload, indent=2))
print(f"  written: {path}")

print("\nMigration complete.")
