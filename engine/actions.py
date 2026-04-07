from enum import Enum


class Action(Enum):
    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"
    SHOVE = "shove"


class MixedStrategy:
    """
    Represents a GTO mixed strategy for a given spot.
    Frequencies are probabilities that sum to 1.0.

    Example:
        MixedStrategy({"raise": 0.65, "call": 0.20, "fold": 0.15})
    """

    def __init__(self, frequencies: dict[str, float]):
        total = sum(frequencies.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Frequencies must sum to 1.0, got {total}")
        self.frequencies = frequencies

    def dominant_action(self) -> str:
        """Return the action with the highest frequency."""
        return max(self.frequencies, key=self.frequencies.get)

    def is_pure(self) -> bool:
        """Return True if one action has 100% frequency."""
        return any(f == 1.0 for f in self.frequencies.values())

    def __repr__(self):
        parts = ", ".join(f"{a}: {f:.0%}" for a, f in self.frequencies.items())
        return f"MixedStrategy({{{parts}}})"
