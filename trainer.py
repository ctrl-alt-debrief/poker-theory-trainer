import random
from engine.decision_engine import decide
from engine.scenario import Scenario, Situation
from engine.actions import MixedStrategy

POSITIONS = ["UTG", "HJ", "CO", "BTN", "SB", "BB"]
STACK_DEPTHS = [25]

RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
SUITS = ["s", "o"]


def generate_hand() -> str:
    r1, r2 = random.sample(RANKS, 2)
    if RANKS.index(r1) > RANKS.index(r2):
        r1, r2 = r2, r1
    if r1 == r2:
        return f"{r1}{r2}"
    return f"{r1}{r2}{random.choice(SUITS)}"


def generate_scenario() -> tuple[Scenario, str]:
    """
    Generate a random training scenario.
    Returns the Scenario and a question string for the user.
    """
    stack_depth = random.choice(STACK_DEPTHS)
    situation = random.choice(list([Situation.RFI, Situation.VS_SHOVE, Situation.BB_DEFEND]))
    hand = generate_hand()

    if situation == Situation.RFI:
        position = random.choice(POSITIONS)
        question = (
            f"Hand: {hand} | Position: {position} | Stack: {stack_depth}bb | Situation: RFI\n"
            f"No action before you — FOLD, RAISE, or SHOVE?"
        )
        scenario = Scenario(hand=hand, position=position, stack_depth=stack_depth, situation=situation)

    elif situation == Situation.VS_SHOVE:
        position = random.choice(POSITIONS)
        question = (
            f"Hand: {hand} | Position: {position} | Stack: {stack_depth}bb | Situation: vs Shove\n"
            f"Villain shoves all-in — CALL or FOLD?"
        )
        scenario = Scenario(hand=hand, position=position, stack_depth=stack_depth, situation=situation)

    else:  # BB_DEFEND
        villain_position = random.choice(["UTG", "HJ", "CO", "BTN", "SB"])
        question = (
            f"Hand: {hand} | Position: BB | Stack: {stack_depth}bb | Situation: BB Defend\n"
            f"Villain ({villain_position}) opens — FOLD, CALL, or 3BET?"
        )
        scenario = Scenario(
            hand=hand,
            position="BB",
            stack_depth=stack_depth,
            situation=situation,
            villain_position=villain_position,
        )

    return scenario, question


def format_strategy(strategy: MixedStrategy) -> str:
    return str({a: f"{f:.0%}" for a, f in strategy.frequencies.items()}).replace("'", "")


def evaluate_answer(scenario: Scenario, user_answer: str) -> tuple[bool, str]:
    strategy = decide(scenario)
    user_action = user_answer.strip().lower()
    dominant = strategy.dominant_action()

    is_correct = user_action == dominant or user_action in dominant or dominant in user_action
    gto_display = format_strategy(strategy)

    if strategy.is_pure():
        verdict = "Correct!" if is_correct else f"Wrong. GTO says {dominant.upper()} (pure)."
    else:
        verdict = (
            f"{'Correct!' if is_correct else 'Wrong.'} "
            f"GTO mixes here — dominant: {dominant.upper()}."
        )

    return is_correct, f"{verdict} GTO: {gto_display}"


def run_trainer(num_questions: int = 10):
    print("=" * 55)
    print("  POKER GTO TRAINER — 25BB Edition")
    print("=" * 55)
    print(f"Starting a {num_questions}-question session.\n")

    score = 0

    for i in range(1, num_questions + 1):
        scenario, question = generate_scenario()
        print(f"Q{i}: {question}")
        user_input = input("Your answer: ").strip()

        is_correct, feedback = evaluate_answer(scenario, user_input)
        print(feedback)
        if is_correct:
            score += 1
        print()

    print("=" * 55)
    print(f"Session complete! Score: {score}/{num_questions}")
    pct = round(score / num_questions * 100)
    print(f"Accuracy: {pct}%")
    if pct >= 80:
        print("Great work! Strong fundamentals.")
    elif pct >= 60:
        print("Decent — review the ranges you missed.")
    else:
        print("Keep studying those ranges — you'll get there.")
    print("=" * 55)


if __name__ == "__main__":
    run_trainer()
