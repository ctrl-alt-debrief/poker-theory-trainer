# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

---

## [0.2.0] — 2026-04-07

### Added

- **30bb RFI range data** (`data/ranges/30bb/`)
  Solver-sourced 9-handed MTT ranges from Pokerati.com for all 7 open-raise positions:
  UTG, UTG+1, UTG+2, HJ, CO, BTN, SB. Binary raise/fold (pure actions), consistent with
  the tighter structure of 30bb tournament play.

- **9-handed position support** (`engine/decision_engine.py`, `trainer.py`)
  Expanded `VALID_POSITIONS` and `POSITIONS` from 6-max (`UTG → BB`) to full 9-handed
  (`UTG, UTG+1, UTG+2, HJ, CO, BTN, SB, BB`). Collapsing UTG+1/UTG+2 into UTG would
  have meaningfully distorted ranges — 9-handed data warrants 9 positions.

- **BB + RFI guard** (`engine/decision_engine.py`)
  Explicit `ValueError` when BB is passed with `Situation.RFI`. BB is last to act preflop
  and always faces a live blind — there is no RFI from BB. Previously would have produced
  a silent `FileNotFoundError`; now fails fast with a clear message.

- **Graceful missing-situation handling** (`engine/range_loader.py`)
  `get_strategy()` now returns `None` instead of raising `FileNotFoundError` when no range
  file exists for a position/situation/stack combo. `decide()` converts this to a
  `NotImplementedError` with an actionable message. New situation data (e.g. 30bb vs_open)
  drops in as a JSON file with zero code changes to the resolver.

- **`scripts/migrate_30bb_rfi.py`**
  Reproducible migration script that converts the source `files(1)/` solver exports to
  the project's standard JSON format (`{position}_{situation}.json` with `"strategy"` key,
  zero-value actions stripped). Documents the source, field mapping, and position slug
  conventions.

### Changed

- **`RFI_POSITIONS` constant** (`trainer.py`)
  RFI scenario generation now draws from `RFI_POSITIONS` (all positions except BB) rather
  than the full `POSITIONS` list. Prevents the trainer from generating structurally invalid
  scenarios before they reach the engine.

- **`test_unknown_position_raises`** (`tests/test_decision_engine.py`)
  Updated from `"UTG+1"` (now a valid position) to `"MP"` (genuinely invalid).

### Tests

- Added `TestRFI30bb` (6 tests) covering:
  - UTG+1 and UTG+2 resolve correctly at 30bb
  - 30bb UTG opens wider than 25bb UTG (solver data reflects deeper stacks)
  - BTN at 30bb opens very wide (e.g. 98o raises)
  - Trash still folds pure at 30bb
  - BB + RFI raises `ValueError` with descriptive message
  - Missing situation (30bb vs_shove) raises `NotImplementedError` cleanly

---

## [0.1.1] — 2026-04-06

### Fixed

- **`generate_hand()` never produced pocket pairs** (`trainer.py`)
  `random.sample` draws without replacement, making it impossible for both ranks to be equal.
  Switched to `random.choices` (with replacement) so pairs like AA, KK, 22 can be generated.
  Pocket pairs represent a significant portion of preflop decisions and were entirely absent from training scenarios.

- **`evaluate_answer()` accepted partial string matches** (`trainer.py`)
  The previous check (`user_action in dominant or dominant in user_action`) meant inputs like
  `"r"`, `"ais"`, or `"old"` would incorrectly pass for `"raise"` or `"fold"`.
  Replaced with exact matching against a `VALID_INPUTS` whitelist per action.
  Common aliases are still supported (`"jam"` → shove, `"3-bet"` → 3bet).

### Changed

- **Removed redundant `list()` wrapping** in `generate_scenario()` (`trainer.py`)
  `random.choice(list([...]))` simplified to `random.choice([...])`.

### Tests

- Added `tests/test_trainer.py` with 13 new tests covering:
  - `generate_hand()` — pair generation, rank ordering, valid ranks, suit suffixes
  - `evaluate_answer()` — exact match, partial string rejection, case insensitivity, action aliases

---

## [0.1.0] — 2026-04-06

### Added

- Initial project scaffold — `engine/`, `data/`, `tests/`, `trainer.py`
- `Scenario` dataclass and `Situation` enum covering 7 preflop spot types
- `MixedStrategy` class — GTO frequency distributions per hand
- `decide(scenario)` — single engine entry point returning a `MixedStrategy`
- JSON-based range storage under `data/ranges/{stack}bb/` — new stack depths require no code changes
- File-based range loader with in-memory caching (`engine/range_loader.py`)
- Seed range data for all 6 positions at 25bb across RFI, vs shove, and BB defend situations
- Interactive terminal trainer with per-session scoring
- 23 unit tests across engine and scenario validation
- `CLAUDE.md` — persistent project context for Claude Code sessions
