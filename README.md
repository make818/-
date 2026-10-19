# Su Chess (素棋)

Su Chess is an experimental two-player hidden-information board game for strategic decision-making and AI research. It uses a 10×10 board, a central portal, three hidden Kings per side, sequential Shield attacks, Bomb risk, and Hunter promotion.

## Current release

**v0.1.0-experimental** — playable rules engine and command-line prototype. The rules and implementation are still being tested for balance and clarity. The baseline AI is intentionally weak.

## Run locally

From the repository root:

```bash
python -m unittest discover -s su_chess/tests -v
python -m su_chess.cli                 # two human players
python -m su_chess.cli --ai            # human vs baseline AI
python -m su_chess.cli --save game.json
python -m su_chess.cli --load game.json
python -m su_chess.webapp              # local landing page at http://127.0.0.1:8000
```

CLI moves use `row,col row,col`, for example `1,2 2,3`. Type `save` or `quit` during play.

## Rules and implementation

- [`Su_Chess_Complete_Rules_and_Audit.docx`](Su_Chess_Complete_Rules_and_Audit.docx) — complete English rules and design audit.
- [`su_chess/engine.py`](su_chess/engine.py) — rules, hidden identities, portal, Shield timing, terminal states, and repetition.
- [`su_chess/tests/`](su_chess/tests/) — automated regression tests.
- [`su_chess/ai.py`](su_chess/ai.py) — capture-preferring baseline AI.
- [`su_chess/storage.py`](su_chess/storage.py) — JSON save/load.

There are three decisive outcomes: capturing the opponent's True King, activating a Bomb (the attacker loses), and occupying the opponent's throne with the True King. A surrounded True King is safe. If neither side has any legal capture, the game is drawn; fourfold repetition is also a draw.

## Status and roadmap

The project is ready for public rules-engine playtesting. It still needs a stronger AI, a fully interactive board UI, broader perft/property testing, and human balance studies. Treat the current release as experimental.

## License

MIT. See [`su_chess/LICENSE`](su_chess/LICENSE).
