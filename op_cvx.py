import cvxpy as cp
import pandas as pd
import numpy as np

def optimize_with_cvxpy(platforms, min_royalty_diff=0.5):
    n = len(platforms)

    # Extract data
    margins = np.array([p['margin'] for p in platforms])
    bounds = np.array([p['bounds'] for p in platforms])
    names = [p['name'] for p in platforms]

    # Create variables
    prices = cp.Variable(n)

    # Objective: maximize total royalty
    royalty = cp.multiply(margins, prices)
    objective = cp.Maximize(cp.sum(royalty))

    # Constraints
    constraints = []

    # Price bounds
    for i in range(n):
        constraints += [
            prices[i] >= bounds[i, 0],
            prices[i] <= bounds[i, 1]
        ]

    # Group margin indices
    margin_groups = {}
    for i, m in enumerate(margins):
        margin_groups.setdefault(m, []).append(i)

    # Enforce royalty separation between different margin tiers
    unique_margins = sorted(set(margins), reverse=True)
    for i in range(len(unique_margins) - 1):
        hi = unique_margins[i]
        lo = unique_margins[i + 1]
        idx_hi = margin_groups[hi][0]
        idx_lo = margin_groups[lo][0]
        constraints += [
            margins[idx_hi] * prices[idx_hi] >= margins[idx_lo] * prices[idx_lo] + min_royalty_diff
        ]

    # Optional: encourage price variation within same margin group
    max_variation = 5.0
    for indices in margin_groups.values():
        if len(indices) > 1:
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    constraints += [
                        cp.abs(prices[indices[i]] - prices[indices[j]]) <= max_variation
                    ]

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve()

    # Output
    final_prices = prices.value
    royalty_values = margins * final_prices

    min_prices = bounds[:, 0]
    max_prices = bounds[:, 1]
    
    df = pd.DataFrame({
        'Platform': names,
        'Margin': margins,
        'Min Price': min_prices,
        'Max Price': max_prices,
        'Price': final_prices.round(2),
        'Royalty': royalty_values.round(2)
    })

    df['Ranking'] = df['Royalty'].rank(ascending=False).astype(int)
    df = df.sort_values('Royalty', ascending=False).reset_index(drop=True)
    return df


platforms = [
    {'name': 'MoKa Reads Shop', 'margin': 0.87, 'bounds': (10, 25)},
    {'name': 'KDP Paperback', 'margin': 0.60, 'bounds': (15, 50)},
    {'name': 'KDP Ebook', 'margin': 0.35, 'bounds': (10, 40)},
    {'name': 'Leanpub', 'margin': 0.80, 'bounds': (10, 28)},
    {'name': 'Kobo', 'margin': 0.70, 'bounds': (10, 28)},
    {'name': 'Google Books', 'margin': 0.70, 'bounds': (10, 28)},
    {'name': 'B&N Ebook', 'margin': 0.70, 'bounds': (10, 28)},
    {'name': 'B&N Print', 'margin': 0.55, 'bounds': (15, 50)},
]

df = optimize_with_cvxpy(platforms)
print("CVXPY Optimized Pricing:")
print(df)
df.to_csv("cvxpy_optimized_pricing.csv", index=False)
