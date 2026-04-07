import json
from pathlib import Path
from engine.actions import MixedStrategy

DATA_DIR = Path(__file__).parent.parent / "data" / "ranges"

# In-memory cache: (position, situation, stack_depth) -> strategy dict
_cache: dict[str, dict] = {}


def _file_path(position: str, situation: str, stack_depth: int) -> Path:
    filename = f"{position.lower()}_{situation.lower()}.json"
    return DATA_DIR / f"{stack_depth}bb" / filename


def _load(position: str, situation: str, stack_depth: int) -> dict | None:
    """
    Return the strategy dict for this spot, or None if no range file exists yet.
    None signals 'situation not implemented' — callers decide how to handle it.
    """
    cache_key = f"{position}_{situation}_{stack_depth}"
    if cache_key not in _cache:
        path = _file_path(position, situation, stack_depth)
        if not path.exists():
            return None
        _cache[cache_key] = json.loads(path.read_text())["strategy"]
    return _cache[cache_key]


def get_strategy(position: str, situation: str, stack_depth: int, hand: str) -> MixedStrategy | None:
    """
    Load the GTO mixed strategy for a hand in a given spot.

    Returns:
        MixedStrategy — if a range file exists for this spot.
        None          — if no range file exists for this position/situation/stack combo.
                        The caller should treat this as 'scenario not yet implemented'.
        MixedStrategy({"fold": 1.0}) — if the file exists but the hand is not in the range
                        (i.e. the hand is a pure fold in GTO).
    """
    strategy_map = _load(position, situation, stack_depth)
    if strategy_map is None:
        return None
    if hand in strategy_map:
        return MixedStrategy(strategy_map[hand])
    return MixedStrategy({"fold": 1.0})


def available_stacks() -> list[int]:
    """Return all stack depths that have range data on disk."""
    return sorted(
        int(d.name.replace("bb", ""))
        for d in DATA_DIR.iterdir()
        if d.is_dir() and d.name.endswith("bb")
    )
