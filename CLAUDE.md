# Context for Claude Code — Poker GTO Trainer
_Last updated: April 2026_

---

## Who I am

Undergraduate student building this project for my software engineering portfolio.
- **Primary goal:** demonstrate real engineering thinking to recruiters and hiring managers
- **Secondary goal:** actually learn GTO poker theory along the way

I am still learning. Prefer explanations alongside code changes, not just the change itself. When you make a non-obvious decision, tell me why.

---

## What this project needs to signal to recruiters

- Clean architecture and separation of concerns
- Test-driven thinking (tests exist alongside features, not after)
- Thoughtful data modeling (`Scenario` dataclass, `MixedStrategy`, `Situation` enum)
- Extensibility by design (adding a stack depth = drop JSON files, no code changes)
- A clear growth arc: CLI → API → web UI (shows I think in systems)

When suggesting changes, keep these signals in mind. Don't over-engineer. Don't under-document.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.x |
| Testing | pytest |
| Range data | JSON files under `data/ranges/{stack}bb/` — seeded manually, to be replaced with solver-sourced charts |
| Future backend | FastAPI |
| Future frontend | HTML/JS — no framework yet, keep it simple |
| Future DB | SQLite locally → Postgres when leaderboards are needed |

Do not introduce new dependencies without flagging them and explaining the tradeoff.

---

## Code style preferences

- Type hints on all function signatures
- Docstrings on all public functions and classes — short, plain English
- Descriptive variable names over clever ones
- No magic numbers — use named constants or enums
- Prefer explicit over implicit
- Keep functions small and single-purpose

---

## Project conventions

- Entry point is `trainer.py`
- All engine logic lives in `engine/`
- Range data lives in `data/ranges/{stack}bb/`
- Tests mirror the module structure under `tests/`
- One JSON file per position/situation combo — filename = `{position}_{situation}.json`

Do not reorganize the folder structure without discussing it first.

---

## Testing expectations

- Every new feature or bug fix should come with a test
- Tests should be readable — test names should explain what they're checking
- Prefer testing behavior over implementation
- Current suite: 23 tests in `tests/test_decision_engine.py`
- Target: keep coverage above 80% as the project grows

---

## Documentation expectations

- README is for recruiters first, developers second — keep it plain English
- Inline comments explain *why*, not *what*
- No local absolute paths anywhere in the codebase or docs
- Commit messages follow the pattern: subject line + bullet points covering what changed, why it matters, and any new tests

---

## Things to flag before doing

- Adding a new dependency (`pip install` anything)
- Changing the public interface of `decide(scenario)`
- Changing the JSON range file format
- Restructuring folders
- Anything that would break existing tests

---

## Learning goals

When introducing a new pattern or concept I haven't used before, briefly explain:
1. What it is
2. Why we're using it here
3. What the alternative would have been

---

## Known issues

Issues identified but not yet fixed. Check here at the start of each session.

### Medium — BB_DEFEND ignores villain position
**Location:** `engine/range_loader.py` + `data/ranges/25bb/bb_bb_defend.json`
**Severity:** Data accuracy — no crash, but wrong answers
The trainer shows "Villain (BTN) opens" but the engine loads a single flat `bb_bb_defend.json`
regardless of who opened. In real GTO, BB defends differently vs UTG (tight range) vs BTN
(wide range). Fix requires either separate files per villain position (`bb_vs_utg_defend.json`
etc.) or a keyed structure inside one file. Needs new range data before it's worth implementing.
**Resolved when:** `tests/test_decision_engine.py::TestBBDefend` includes villain-position-aware
assertions (e.g. BB defends wider vs BTN than vs UTG). Remove this entry in the same commit.

### Medium — Trainer only generates 25bb scenarios
**Location:** `trainer.py:10` — `STACK_DEPTHS = [25]`
**Severity:** Silent data gap — no crash, but 30bb and 80bb ranges are never exercised in play
`generate_scenario()` draws the stack depth from `STACK_DEPTHS`, which is hardcoded to `[25]`.
Now that 30bb and 80bb RFI data exist, players never see those spots. Fix: replace the hardcoded
list with `available_stacks()` from `range_loader`, then filter to stacks that have data for the
chosen situation (30bb and 80bb currently only have RFI).
**Resolved when:** `tests/test_trainer.py::TestGenerateScenario` asserts that multiple stack depths
are reachable from `generate_scenario()`. Remove this entry in the same commit.

### Minor — `_load()` doesn't cache missing files
**Location:** `engine/range_loader.py:24–26`
**Severity:** Performance only — no correctness impact
When a range file doesn't exist, `_load()` returns `None` without writing to `_cache`.
Every subsequent call for that spot re-hits the filesystem with `path.exists()`.
Fix: store a sentinel (e.g. `_cache[cache_key] = None`) before returning, and check
`cache_key not in _cache` vs `_cache[cache_key] is None` separately.
**Resolved when:** `tests/test_range_loader.py` includes a test asserting repeated calls for a
missing file only hit the filesystem once. Remove this entry in the same commit.
