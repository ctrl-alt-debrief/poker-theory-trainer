import pytest
from unittest.mock import patch
from trainer import generate_hand, evaluate_answer, RANKS
from engine.scenario import Scenario, Situation


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
