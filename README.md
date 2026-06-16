# Type Fact

**A terminal typing game that teaches you CS, ML, AI, and computational biology — one keystroke at a time.**

No AI autocomplete. No copy-paste. No shortcuts. **You type every character yourself.**

In a world where AI can write essays, code, and emails for you, typing practice is one of the few activities where *your fingers must do the work*. Every sentence in this game is a real fact about computer science, machine learning, artificial intelligence, or AI for biology — so while you build speed and accuracy, you're absorbing knowledge that no LLM can internalize for you.

## Quick start

```bash
python3 typing_game.py
```

That's it. No dependencies beyond Python 3 and a terminal. Works on Linux and macOS out of the box.

## What you get

- **574 curated facts** across CS fundamentals, ML, AI, computational biology, and bash tricks
- **Real-time feedback** — green for correct, red for wrong, yellow cursor
- **Live WPM and accuracy** as you type
- **Progress bar** per sentence
- **10 random sentences per session** with a results summary at the end

## Topics covered

| Category | Count | Examples |
|---|---|---|
| **CS Fundamentals** | 153 | Algorithms, data structures, networking, OS, cryptography, compilers, architecture, databases, concurrency, information theory |
| **Machine Learning** | 113 | Optimization, regularization, loss functions, Bayesian methods, GNNs, fairness, time series, self-supervised learning |
| **Artificial Intelligence** | 143 | Transformers, NLP, computer vision, RL, generative models, scaling laws, interpretability, AI safety, robotics |
| **Cross-domain** | 25 | ML hardware, distributed training, numerical methods, bioinformatics |
| **AI for Biology** | 70 | Protein structure (AlphaFold), genomics, single-cell, protein language models, drug discovery, medical imaging, clinical AI |
| **Bash & Shell Tricks** | 70 | History expansion, parameter manipulation, process substitution, globs, job control, set options, arrays, traps, file descriptors, SSH |

## Controls

| Key | Action |
|---|---|
| Any key | Start typing |
| Backspace | Delete last character |
| Esc | Skip current sentence |
| q | Quit (from title or results screen) |

## Why this exists

AI can generate text, but it can't type for you. This game is deliberate practice for your fingers *and* your brain:

1. **You must type it** — there is no autocomplete, no suggestion bar, no AI finishing your sentence. Every character comes from your muscle memory.
2. **You learn by doing** — reading a fact about backpropagation is one thing; typing it character by character forces a different kind of engagement.
3. **Speed and accuracy matter** — WPM and accuracy are tracked live, giving you concrete metrics to improve.

## Requirements

- Python 3.6+
- A terminal with color support (virtually all modern terminals)
- `curses` (included with Python on Linux/macOS)

## License

MIT
