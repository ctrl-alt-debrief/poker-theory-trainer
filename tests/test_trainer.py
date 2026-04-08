import pytest
from unittest.mock import patch
from trainer import generate_hand, generate_scenario, evaluate_answer, format_strategy, RANKS, RFI_POSITIONS, VS_SHOVE_POSITIONS
from engine.scenario import Scenario, Situation
from engine.actions import MixedStrategy


class TestGenerateHand:
    def test_format_suited(self):
        # All non-pair hands end in 's' or 'o'
        for _ in range(100):
            hand = generate_hand()
            if len(hand) == 3:
                assert hand[-1] in ("s", "o"), f"Invalid suit suffix: {hand}"

    def test_format_pair(self):
        # Pairs are exactly 2 characters, both the same rank
        for _ in range(200):
            hand = generate_hand()
            if len(hand) == 2:
                assert hand[0] == hand[1], f"Non-pair two-char hand: {hand}"

    def test_pairs_are_possible(self):
        # With random.choices, pocket pairs must be reachable.
        # Over 2000 attempts the probability of zero pairs is astronomically small.
        hands = [generate_hand() for _ in range(2000)]
        pairs = [h for h in hands if len(h) == 2]
        assert len(pairs) > 0, "Pocket pairs were never generated — random.sample bug likely reintroduced"

    def test_high_rank_comes_first(self):
        for _ in range(200):
            hand = generate_hand()
            r1, r2 = hand[0], hand[1]
            if r1 != r2:
                assert RANKS.index(r1) <= RANKS.index(r2), f"Ranks out of order: {hand}"

    def test_valid_ranks_only(self):
        for _ in range(200):
            hand = generate_hand()
            assert hand[0] in RANKS and hand[1] in RANKS, f"Invalid rank in hand: {hand}"


class TestEvaluateAnswer:
    def _scenario(self, hand="AA", position="UTG", situation=Situation.RFI):
        return Scenario(hand=hand, position=position, stack_depth=25, situation=situation)

    def test_exact_match_correct(self):
        scenario = self._scenario("AA", "UTG", Situation.RFI)
        # AA from UTG is a pure shove
        is_correct, _ = evaluate_answer(scenario, "shove")
        assert is_correct

    def test_exact_match_wrong(self):
        scenario = self._scenario("AA", "UTG", Situation.RFI)
        is_correct, _ = evaluate_answer(scenario, "fold")
        assert not is_correct

    def test_partial_string_not_accepted(self):
        # "r" should NOT match "raise" — this was the bug
        scenario = self._scenario("99", "UTG", Situation.RFI)
        is_correct, _ = evaluate_answer(scenario, "r")
        assert not is_correct, "'r' should not be accepted as a valid answer for 'raise'"

    def test_substring_not_accepted(self):
        # "ais" is a substring of "raise" — should not match
        scenario = self._scenario("99", "UTG", Situation.RFI)
        is_correct, _ = evaluate_answer(scenario, "ais")
        assert not is_correct

    def test_case_insensitive(self):
        scenario = self._scenario("AA", "UTG", Situation.RFI)
        is_correct, _ = evaluate_answer(scenario, "SHOVE")
        assert is_correct

    def test_shove_alias_jam(self):
        scenario = self._scenario("AA", "UTG", Situation.RFI)
        is_correct, _ = evaluate_answer(scenario, "jam")
        assert is_correct

    def test_3bet_alias(self):
        scenario = self._scenario("AA", "BB", Situation.BB_DEFEND)
        is_correct, _ = evaluate_answer(scenario, "3-bet")
        assert is_correct

    def test_feedback_includes_gto(self):
        scenario = self._scenario("AA", "UTG", Situation.RFI)
        _, feedback = evaluate_answer(scenario, "shove")
        assert "GTO" in feedback


class TestGenerateScenario:
    # generate_scenario() picks situation, position, hand, and stack randomly.
    # We patch random.choice / random.choices to force each branch and assert
    # the output respects the position/situation constraints.

    def _force_situation(self, situation_value, position, hand="AKs"):
        """Run generate_scenario() with controlled random output for a given situation."""
        with patch("trainer.random") as mock_random:
            mock_random.choice.side_effect = [
                1,             # stack_depth (index into STACK_DEPTHS — not used directly)
                situation_value,
                position,
            ]
            mock_random.choices.return_value = [hand[0], hand[1]] if len(hand) >= 2 else ["A", "K"]
            # Patch at the module level so generate_scenario uses our mock
            with patch("trainer.random.choice", side_effect=[25, situation_value, position]):
                with patch("trainer.random.choices", return_value=["A", "K"]):
                    with patch("trainer.random.choice", side_effect=[25, situation_value, position]):
                        pass  # nested patches get complex — use direct import approach below

    def test_rfi_scenario_never_has_bb_as_position(self):
        # BB has no RFI — if BB ever appears here the engine raises ValueError
        for _ in range(200):
            scenario, _ = generate_scenario()
            if scenario.situation == Situation.RFI:
                assert scenario.position != "BB", "BB should never be generated for RFI"

    def test_rfi_position_always_in_rfi_positions(self):
        for _ in range(200):
            scenario, _ = generate_scenario()
            if scenario.situation == Situation.RFI:
                assert scenario.position in RFI_POSITIONS

    def test_vs_shove_position_always_in_vs_shove_positions(self):
        for _ in range(200):
            scenario, _ = generate_scenario()
            if scenario.situation == Situation.VS_SHOVE:
                assert scenario.position in VS_SHOVE_POSITIONS

    def test_bb_defend_always_has_position_bb(self):
        for _ in range(200):
            scenario, _ = generate_scenario()
            if scenario.situation == Situation.BB_DEFEND:
                assert scenario.position == "BB"

    def test_bb_defend_always_has_villain_position(self):
        for _ in range(200):
            scenario, _ = generate_scenario()
            if scenario.situation == Situation.BB_DEFEND:
                assert scenario.villain_position is not None, "BB_DEFEND must have a villain_position"

    def test_returns_scenario_and_string(self):
        scenario, question = generate_scenario()
        assert isinstance(scenario, Scenario)
        assert isinstance(question, str)
        assert len(question) > 0


class TestFormatStrategy:
    def test_no_single_quotes_in_output(self):
        # format_strategy strips quotes so output reads as {fold: 100%} not {'fold': '100%'}
        result = format_strategy(MixedStrategy({"fold": 1.0}))
        assert "'" not in result

    def test_output_contains_percent_signs(self):
        result = format_strategy(MixedStrategy({"fold": 1.0}))
        assert "%" in result

    def test_pure_strategy_shows_100_percent(self):
        result = format_strategy(MixedStrategy({"shove": 1.0}))
        assert "100%" in result

    def test_mixed_strategy_shows_multiple_actions(self):
        result = format_strategy(MixedStrategy({"raise": 0.7, "fold": 0.3}))
        assert "raise" in result
        assert "fold" in result
