
# 📘 Pricing Optimization for Multi-Format Publishing

This project provides a mathematical and computational framework for **optimizing the price structure** of published works (ebooks, paperbacks, retail, etc.) across different distribution channels with varying royalty margins.

## 📊 Output

The script returns a ranked summary table showing:
- Optimal price for each platform
- Per-unit royalty (your earnings)
- A “support ranking” showing which format benefits you most

## 🧮 Mathematical Formulation

See `problem.typ` for the full write-up, including constraints, objective, and rationale.

## 🐍 Code Usage

Install required Python packages:

```bash
uv sync
```

You can run `uv run <script_name.py>` to execute the script depending on which one you want to run.

## 📄 Files Included

There are a few implementations that have similar results, our preferred is
`op_cvx.py` as we found it to be the most efficient and accurate. Other ones are also `optimizer.py` and `rules.py` which implement the problem in different ways.

## 🧠 Concepts Involved

- Linear and nonlinear programming
- Royalties and margin modeling
- Consumer pricing psychology
- Optimization under inequality constraints

## 📬 License

MIT License — free for educational, nonprofit, and commercial use. Please cite or credit when used in publications.
