
# 📘 Pricing Optimization for Multi-Format Publishing

This project provides a mathematical and computational framework for **optimizing the price structure** of published works (ebooks, paperbacks, retail, etc.) across different distribution channels with varying royalty margins.

## 📊 Output

The script returns a ranked summary table showing:
- Optimal price for each platform
- Per-unit royalty (your earnings)
- A “support ranking” showing which format benefits you most

## 🧮 Mathematical Formulation (LaTeX)

See `problem.typ` for the full write-up, including constraints, objective, and rationale.

## 🐍 Code Usage

Install required Python packages:

```bash
uv sync
```

Run the optimizer:

```python
from optimizer import optimize_pricing

platforms = [
    {'name': 'Ebook (Direct)', 'margin': 0.95},
    {'name': 'Paperback (KDP)', 'margin': 0.55},
    {'name': 'Retail (Ingram)', 'margin': 0.35},
]

bounds = [(5, 20), (10, 30), (15, 40)]

result = optimize_pricing(platforms, bounds)
print(result)
# to save csv:
# result.to_csv('summary.csv', index=False)
```

## 📄 Files Included

| File | Description |
|------|-------------|
| `optimize_pricing.py` | Python implementation of the model |
| `problem.typ/pdf`   | Write-up of the math model |

## 🧠 Concepts Involved

- Linear and nonlinear programming
- Royalties and margin modeling
- Consumer pricing psychology
- Optimization under inequality constraints

## 📬 License

MIT License — free for educational, nonprofit, and commercial use. Please cite or credit when used in publications.
