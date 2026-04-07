# Poker GTO Trainer

A preflop decision trainer that quizzes you on game-theory optimal poker strategy by position and stack depth.
Decisions are returned as mixed strategy distributions — not just "raise or fold" but `{"raise": 0.65, "call": 0.20, "fold": 0.15}` — mirroring how modern GTO solvers actually output strategy.

> Personal project — building toward a browser-based trainer with session tracking and leaderboards.

---

## What it does

- Generates quiz scenarios from real preflop range data (position, stack depth, situation type)
- Returns GTO-accurate mixed strategies for each hand, not binary correct/wrong answers
- Covers 7 situation types: RFI (raise first in), vs shove, BB defend, vs 3-bet, squeeze, cold call, vs 4-bet
- Scores your session and shows the full GTO frequency breakdown after each answer

---

## Project Structure

```
poker-gto-trainer/
├── trainer.py                    # Entry point — runs interactive quiz sessions
├── scripts/
│   └── migrate_ranges.py         # Utility: converts range data into JSON format
├── data/
│   └── ranges/
│       └── 25bb/                 # One JSON file per position/situation combo
│           ├── utg_rfi.json
│           ├── utg_vs_shove.json
│           ├── hj_rfi.json
│           ├── ...
│           └── bb_bb_defend.json
├── tests/
│   └── test_decision_engine.py   # 23 unit tests
└── engine/
    ├── actions.py                 # MixedStrategy class + Action enum
    ├── scenario.py                # Scenario dataclass + Situation enum
    ├── range_loader.py            # Loads JSON range files from disk, caches in memory
    └── decision_engine.py         # Single decide(scenario) → MixedStrategy entry point
```

---

## Quickstart

```bash
git clone <repo-url>
cd poker-gto-trainer
python3 trainer.py
```

```bash
# Run tests
python3 -m pytest tests/ -v
```

---

## How it works

Every quiz question is built from a `Scenario` — a dataclass that captures the full context of a poker decision: hand, position, stack depth, situation type, and (where relevant) the villain's position and bet size. The engine looks up the matching JSON range file, reads the GTO frequencies for that hand, and returns a `MixedStrategy`.

Range data lives in `data/ranges/{stack}bb/` as plain JSON files. Adding a new stack depth means dropping files into a new folder — no code changes required.

---

## Roadmap

✅ **Phase 1 — Foundation**
Core engine with `decide(scenario)` entry point, mixed strategy output, JSON-based range storage, and 23 passing unit tests.

✅ **Phase 2 (partial) — Range data at 25bb**
GTO approximations for all 6 positions across RFI, vs shove, and BB defend situations.

⬜ **Phase 2 (continued) — Range depth**
Add real solver-sourced range charts for 15bb, 20bb, 30bb, and 40bb+ stack depths.

⬜ **Phase 3 — Situation complexity**
Expand to vs 3-bet, squeeze, and cold call spots with pot odds calculation.

⬜ **Phase 4 — Postflop**
Flop texture reading, c-bet decisions by position and range advantage, turn and river scenarios.

⬜ **Phase 5 — Trainer intelligence**
Track weak spots per user, weight scenario generation toward missed hands, persist session history.

⬜ **Phase 6 — Web UI & leaderboards**
FastAPI backend wrapping the existing engine, HTML/JS frontend, SQLite for local dev swappable to Postgres for multi-user leaderboards.

---

## Terminology

| Term | Meaning |
|------|---------|
| GTO | Game Theory Optimal — a strategy that cannot be exploited |
| RFI | Raise First In — no one has acted before you |
| BB | Big Blind — the forced bet; also used as a unit of stack size (e.g. 25bb) |
| UTG | Under the Gun — first to act preflop |
| HJ | Hijack — two seats right of the button |
| CO | Cutoff — one seat right of the button |
| BTN | Button — best position, last to act postflop |
| SB | Small Blind |
| Shove | Go all-in |
| 3-bet | Re-raise over an open raise |
| Squeeze | 3-bet after an open + one or more callers |

---

## Notes

- Current ranges are GTO approximations — real solver data will be imported in Phase 2
- All ranges assume 6-max format
- 25bb is a common tournament stack depth where open-raise and push/fold strategies overlap
