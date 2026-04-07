import pytest
from engine.decision_engine import decide
from engine.scenario import Scenario, Situation
from engine.actions import MixedStrategy


# --- MixedStrategy ---

class TestMixedStrategy:
    def test_frequencies_sum_to_one(self):
        s = MixedStrategy({"raise": 0.7, "fold": 0.3})
        assert abs(sum(s.frequencies.values()) - 1.0) < 0.01

    def test_dominant_action(self):
        s = MixedStrategy({"raise": 0.65, "call": 0.20, "fold": 0.15})
        assert s.dominant_action() == "raise"

    def test_is_pure(self):
        assert MixedStrategy({"fold": 1.0}).is_pure()
        assert not MixedStrategy({"raise": 0.7, "fold": 0.3}).is_pure()

    def test_invalid_frequencies_raise(self):
        with pytest.raises(ValueError):
            MixedStrategy({"raise": 0.5, "fold": 0.3})  # sums to 0.8


# --- Scenario ---

class TestScenario:
    def test_position_uppercased(self):
        s = Scenario(hand="AKs", position="btn", stack_depth=25, situation=Situation.RFI)
        assert s.position == "BTN"

    def test_villain_position_uppercased(self):
        s = Scenario(hand="AKs", position="BB", stack_depth=25, situation=Situation.BB_DEFEND, villain_position="btn")
        assert s.villain_position == "BTN"

    def test_situation_from_string(self):
        s = Scenario(hand="AKs", position="UTG", stack_depth=25, situation="RFI")
        assert s.situation == Situation.RFI

    def test_repr(self):
        s = Scenario(hand="AKs", position="UTG", stack_depth=25, situation=Situation.RFI)
        assert "AKs" in repr(s)
        assert "UTG" in repr(s)
        assert "RFI" in repr(s)


# --- RFI decisions ---

class TestRFI:
    def _scenario(self, hand, position):
        return Scenario(hand=hand, position=position, stack_depth=25, situation=Situation.RFI)

    def test_premium_hands_shove_utg(self):
        for hand in ["AA", "KK", "QQ"]:
            result = decide(self._scenario(hand, "UTG"))
            assert result.dominant_action() == "shove", f"{hand} should shove from UTG"

    def test_trash_folds(self):
        result = decide(self._scenario("72o", "UTG"))
        assert result.dominant_action() == "fold"
        assert result.is_pure()

    def test_btn_wider_than_utg(self):
        btn = decide(self._scenario("77", "BTN"))
        utg = decide(self._scenario("77", "UTG"))
        assert btn.dominant_action() == "raise"
        assert utg.dominant_action() == "fold"

    def test_returns_mixed_strategy(self):
        result = decide(self._scenario("AKs", "BTN"))
        assert isinstance(result, MixedStrategy)

    def test_unknown_position_raises(self):
        with pytest.raises(ValueError):
            decide(self._scenario("AA", "UTG+1"))

    def test_unsupported_stack_raises(self):
        with pytest.raises(NotImplementedError):
            decide(Scenario(hand="AA", position="BTN", stack_depth=100, situation=Situation.RFI))


# --- VS_SHOVE decisions ---

class TestVsShove:
    def _scenario(self, hand, position):
        return Scenario(hand=hand, position=position, stack_depth=25, situation=Situation.VS_SHOVE)

    def test_aces_always_call(self):
        for position in ["UTG", "HJ", "CO", "BTN", "SB"]:
            result = decide(self._scenario("AA", position))
            assert result.dominant_action() == "call"

    def test_weak_hand_folds(self):
        result = decide(self._scenario("72o", "BTN"))
        assert result.dominant_action() == "fold"
        assert result.is_pure()

    def test_returns_mixed_strategy(self):
        result = decide(self._scenario("JJ", "UTG"))
        assert isinstance(result, MixedStrategy)


# --- BB_DEFEND decisions ---

class TestBBDefend:
    def _scenario(self, hand, villain_position="BTN"):
        return Scenario(
            hand=hand,
            position="BB",
            stack_depth=25,
            situation=Situation.BB_DEFEND,
            villain_position=villain_position,
        )

    def test_premium_hands_3bet(self):
        for hand in ["AA", "KK", "AKs"]:
            result = decide(self._scenario(hand))
            assert result.dominant_action() == "3bet", f"{hand} should 3bet from BB"

    def test_trash_folds(self):
        result = decide(self._scenario("72o"))
        assert result.dominant_action() == "fold"

    def test_returns_mixed_strategy(self):
        result = decide(self._scenario("QQ"))
        assert isinstance(result, MixedStrategy)

    def test_wrong_position_raises(self):
        with pytest.raises(ValueError):
            decide(Scenario(hand="AA", position="BTN", stack_depth=25, situation=Situation.BB_DEFEND))


# --- Unimplemented situations ---

class TestUnimplementedSituations:
    def test_vs_3bet_raises(self):
        with pytest.raises(NotImplementedError):
            decide(Scenario(hand="AA", position="UTG", stack_depth=25, situation=Situation.VS_3BET))

    def test_squeeze_raises(self):
        with pytest.raises(NotImplementedError):
            decide(Scenario(hand="AA", position="CO", stack_depth=25, situation=Situation.SQUEEZE))
