# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

---

## [0.3.0] — 2026-04-08

### Added

- **80bb RFI range data** (`data/ranges/80bb/`)
  9-handed MTT ranges sourced from Pokerati.com for all 7 open-raise positions:
  UTG, UTG+1, UTG+2, HJ, CO, BTN, SB. Wider ranges than 25bb/30bb reflect the
  deeper-stacked nature of 80bb play (e.g. UTG opens 66+, A4s+, KJ+, Q9s+).

- **`scripts/migrate_80bb_ranges.py`**
  Converts raw source files (`80bb/*.json`, `_meta` + `RFI` structure) to the
  project's standard range format (`strategy` key, canonical position names).
  Source files removed after migration; script documents the derivation.

- **`static/js/history.js`** — browser-side session history and weak-spot analysis
  Lays the groundwork for per-session tracking ahead of the future web UI.
  Stores answer records in `localStorage` under `poker_trainer_history`.
  Key functions:
  - `recordAnswer()` — appends one answered hand to localStorage
  - `loadHistory()` — reads the full history array back out
  - `weakSpots(minHands)` — groups history by spot (position + situation + stack),
    returns accuracy stats for any spot with `minHands` or more hands played (default 3)
  - `clearHistory()` — wipes all stored history (for a future "reset progress" UI action)
  Designed so `_loadHistory()` / `_saveHistory()` can be swapped for `fetch()` calls
  when a backend is added, without changing any calling code.

- **`static/js/history.test.js`** — Jest-compatible tests for history.js
  Uses a minimal localStorage mock so tests run in Node without a browser.

- **`tests/test_range_loader.py`** (new file — 11 tests)
  First direct unit tests for `engine/range_loader.py`. Previously covered only
  indirectly through `decide()`. Tests:
  - `available_stacks()` returns sorted integers including 25, 30, 80
  - `get_strategy()` returns `MixedStrategy` for valid spots
  - hands not in a range file default to pure fold (not `KeyError`)
  - missing range files return `None` without crashing
  - repeated calls to a missing spot return `None` both times
  - 80bb migration is accessible through the normal engine path
  - position lookup is case-insensitive

### Known issues added

- **Medium — `STACK_DEPTHS = [25]` silently ignores 30bb and 80bb data** (`trainer.py:10`)
  The trainer hardcodes only 25bb scenarios. Now that 30bb and 80bb RFI data exist,
  players never encounter those ranges. Tracked in `CLAUDE.md`.

### Tests

- Added `TestGenerateScenario` (6 tests) to `tests/test_trainer.py`:
  - BB is never generated as position for RFI (would crash the engine)
  - All RFI positions come from `RFI_POSITIONS`
  - All VS_SHOVE positions come from `VS_SHOVE_POSITIONS`
  - BB_DEFEND always sets `position="BB"` and a non-null `villain_position`
  - Return type is always `(Scenario, str)`

- Added `TestFormatStrategy` (4 tests) to `tests/test_trainer.py`:
  - Output has no single-quotes
  - Output contains `%` symbols
  - Pure strategies display as 100%
  - Mixed strategies display all actions

- **Total tests: 63** (up from 23 at v0.1.0)

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
