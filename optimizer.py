from scipy.optimize import minimize
import numpy as np
import pandas as pd

# Define general function for pricing optimization
def optimize_pricing(platforms, bounds, initial_guess=None):
    """
    platforms: list of dicts, each with keys 'name' and 'margin' (0–1)
    bounds: list of (min_price, max_price) tuples for each platform
    initial_guess: optional starting prices
    """
    n = len(platforms)
    margins = np.array([p['margin'] for p in platforms])
    names = [p['name'] for p in platforms]

    # Objective: maximize total royalty
    def objective(prices):
        royalties = margins * prices
        return -np.sum(royalties)  # negative for minimization

    # Constraints:
    constraints = []

    # Price order: p1 < p2 < ... < pn
    for i in range(n - 1):
        constraints.append({'type': 'ineq', 'fun': lambda x, i=i: x[i + 1] - x[i]})

    # Royalty order: r1 >= r2 >= ... >= rn
    for i in range(n - 1):
        constraints.append({'type': 'ineq', 'fun': lambda x, i=i: margins[i] * x[i] - margins[i + 1] * x[i + 1]})

    # Initial guess
    if not initial_guess:
        initial_guess = [(low + high) / 2 for (low, high) in bounds]

    # Solve
    result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

    # Prepare output summary
    if result.success:
        prices = result.x
        royalties = margins * prices
        summary = pd.DataFrame({
            'Platform': names,
            'Price': np.round(prices, 2),
            'Royalty Margin': margins,
            'Royalty per Unit': np.round(royalties, 2)
        })
        summary['Ranking'] = summary['Royalty per Unit'].rank(ascending=False).astype(int)
        summary = summary.sort_values('Price').reset_index(drop=True)
    else:
        summary = pd.DataFrame({'Error': [result.message]})

    return summary

# Example use:
platforms = [
    {'name': 'Ebook (Direct)', 'margin': 0.95},
    {'name': 'Paperback', 'margin': 0.55},
    {'name': 'Ebook Other', 'margin': 0.35},
]

price_bounds = [(5, 20), (10, 30), (15, 40)]

summary_df = optimize_pricing(platforms, price_bounds)

# Print the results
print("Optimized Pricing Summary:")
print(summary_df)
summary_df.to_csv('summary.csv', index=False)
