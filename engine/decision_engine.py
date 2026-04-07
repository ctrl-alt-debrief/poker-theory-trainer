from engine.actions import MixedStrategy
from engine.scenario import Scenario, Situation
from engine.range_loader import get_strategy, available_stacks

VALID_POSITIONS = {"UTG", "UTG+1", "UTG+2", "HJ", "CO", "BTN", "SB", "BB"}

IMPLEMENTED_SITUATIONS = {Situation.RFI, Situation.VS_SHOVE, Situation.BB_DEFEND}


def _validate(scenario: Scenario) -> None:
    if scenario.position not in VALID_POSITIONS:
        raise ValueError(
            f"Unknown position: '{scenario.position}'. Valid: {sorted(VALID_POSITIONS)}"
        )
    if scenario.stack_depth not in available_stacks():
        raise NotImplementedError(
            f"{scenario.stack_depth}bb ranges not yet implemented. "
            f"Available: {available_stacks()}"
        )
    if scenario.situation not in IMPLEMENTED_SITUATIONS:
        raise NotImplementedError(
            f"Situation '{scenario.situation.value}' not yet implemented. "
            f"Implemented: {[s.value for s in IMPLEMENTED_SITUATIONS]}"
        )
    if scenario.situation == Situation.RFI and scenario.position == "BB":
        raise ValueError(
            "BB has no RFI — BB is last to act preflop and always faces a live blind."
        )
    if scenario.situation == Situation.BB_DEFEND and scenario.position != "BB":
        raise ValueError(
            f"BB_DEFEND requires position='BB', got '{scenario.position}'"
        )


def decide(scenario: Scenario) -> MixedStrategy:
    """
    Single entry point for all preflop decisions.
    Loads the relevant range file from disk and returns a MixedStrategy.

    Example:
        from engine.scenario import Scenario, Situation
        result = decide(Scenario(hand="AKs", position="UTG", stack_depth=25, situation=Situation.RFI))
        # MixedStrategy({shove: 100%})
    """
    _validate(scenario)
    strategy = get_strategy(
        position=scenario.position,
        situation=scenario.situation.value,
        stack_depth=scenario.stack_depth,
        hand=scenario.hand,
    )
    if strategy is None:
        raise NotImplementedError(
            f"No range data for {scenario.position} / {scenario.situation.value} / {scenario.stack_depth}bb. "
            f"Add a range file to data/ranges/{scenario.stack_depth}bb/ to enable this spot."
        )
    return strategy
