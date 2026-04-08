import pytest
from unittest.mock import patch
from engine.range_loader import get_strategy, available_stacks
from engine.actions import MixedStrategy


# --- available_stacks ---

class TestAvailableStacks:
    def test_returns_sorted_list(self):
        stacks = available_stacks()
        assert stacks == sorted(stacks)

    def test_includes_known_stacks(self):
        stacks = available_stacks()
        for expected in [25, 30, 80]:
            assert expected in stacks, f"{expected}bb missing from available_stacks()"

    def test_returns_integers(self):
        for stack in available_stacks():
            assert isinstance(stack, int)


# --- get_strategy ---

class TestGetStrategy:
    def test_returns_mixed_strategy_for_valid_spot(self):
        result = get_strategy("UTG", "RFI", 25, "AA")
        assert isinstance(result, MixedStrategy)

    def test_premium_hand_is_not_fold(self):
        result = get_strategy("UTG", "RFI", 25, "AA")
        assert result.dominant_action() != "fold"

    def test_hand_not_in_range_defaults_to_pure_fold(self):
        # 72o is never in any RFI range — engine returns fold rather than KeyError
        result = get_strategy("UTG", "RFI", 25, "72o")
        assert result is not None
        assert result.dominant_action() == "fold"
        assert result.is_pure()

    def test_returns_none_for_missing_range_file(self):
        # 30bb has no VS_SHOVE data — should return None, not raise
        result = get_strategy("UTG", "VS_SHOVE", 30, "AA")
        assert result is None

    def test_returns_none_for_nonexistent_stack(self):
        result = get_strategy("UTG", "RFI", 999, "AA")
        assert result is None

    def test_repeated_calls_for_missing_file_do_not_crash(self):
        # Calls the same missing spot twice — guards against any future regression
        # where a None result causes an exception on second access.
        # NOTE: this does NOT assert caching — see known issue in CLAUDE.md.
        result1 = get_strategy("UTG", "VS_SHOVE", 30, "AA")
        result2 = get_strategy("UTG", "VS_SHOVE", 30, "AA")
        assert result1 is None
        assert result2 is None

    def test_80bb_rfi_spot_is_accessible(self):
        # Sanity check that the 80bb migration landed correctly
        result = get_strategy("BTN", "RFI", 80, "AA")
        assert isinstance(result, MixedStrategy)
        assert result.dominant_action() != "fold"

    def test_position_lookup_is_case_insensitive(self):
        # range_loader lowercases internally — "utg" and "UTG" should resolve the same file
        result_upper = get_strategy("UTG", "RFI", 25, "AA")
        result_lower = get_strategy("utg", "RFI", 25, "AA")
        assert result_upper is not None
        assert result_lower is not None
        assert result_upper.dominant_action() == result_lower.dominant_action()
