from dataclasses import dataclass
from enum import Enum


class Situation(str, Enum):
    RFI        = "RFI"        # Raise First In — no action before hero
    VS_3BET    = "vs_3bet"    # Hero opened, facing a re-raise
    VS_4BET    = "vs_4bet"    # Hero 3-bet, facing a re-raise
    VS_SHOVE   = "vs_shove"   # Facing an all-in
    BB_DEFEND  = "bb_defend"  # In BB facing an open
    SQUEEZE    = "squeeze"    # Open + caller(s), hero can squeeze
    COLD_CALL  = "cold_call"  # Facing an open from position, not BB


@dataclass
class Scenario:
    hand:             str
    position:         str
    stack_depth:      int
    situation:        Situation
    villain_position: str | None   = None  # who opened/3-bet — matters for defense ranges
    facing_size:      float | None = None  # size of raise in BBs (for pot odds later)

    def __post_init__(self):
        self.position = self.position.upper()
        if self.villain_position:
            self.villain_position = self.villain_position.upper()
        # Allow passing situation as a plain string
        if isinstance(self.situation, str):
            self.situation = Situation(self.situation)

    def __repr__(self):
        parts = [
            f"hand={self.hand}",
            f"position={self.position}",
            f"stack_depth={self.stack_depth}bb",
            f"situation={self.situation.value}",
        ]
        if self.villain_position:
            parts.append(f"villain={self.villain_position}")
        if self.facing_size is not None:
            parts.append(f"facing={self.facing_size}bb")
        return f"Scenario({', '.join(parts)})"
