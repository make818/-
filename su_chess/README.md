# Su Chess (素棋) — experimental v0.1

Su Chess is a two-player hidden-information board game with a 10×10 board, a central portal, three hidden Kings per side, and sequential Shield attacks. This repository contains a dependency-free Python rules engine, CLI, save/load support, a baseline capture-preferring random AI, tests, and a minimal local web landing page.

## Run

```bash
python -m unittest discover -s su_chess/tests -v
python -m su_chess.cli --ai
python -m su_chess.webapp
```

The CLI accepts `row,col row,col`, `save`, and `quit`. Use `--load FILE` to resume a saved game.

## Scope and experimental status

The engine is a reference implementation for playtesting. The baseline AI is intentionally weak. The three decisive outcomes are True King capture, Bomb activation, and a True King occupying the opponent's throne (the throne owner loses). A surrounded True King is not a loss; no-captures deadlocks are drawn. Balance, first-player advantage, portal geometry, and hidden-information strategy have not been statistically validated. The complete English rules are in `Su_Chess_Complete_Rules_and_Audit.docx`.

## Layout

- `engine.py`: legal moves, setup validation, hidden identities, portal, Shield timing, terminal states, no-captures deadlock draws, and repetition.
- `cli.py`: local human/AI play.
- `storage.py`: JSON save/load.
- `ai.py`: baseline move selector.
- `tests/`: automated rules tests.
- `web/`: minimal local web entry page.

Contributions should add a regression test for every rules change.
