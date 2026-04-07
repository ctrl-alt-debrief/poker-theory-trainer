# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

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
