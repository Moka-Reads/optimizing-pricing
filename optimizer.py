from scipy.optimize import minimize
import numpy as np
import pandas as pd

# Define general function for pricing optimization
def optimize_pricing(platforms, bounds, initial_guess=None, slack=0.01, debug=True):
    """
    platforms: list of dicts, each with keys 'name' and 'margin' (0–1)
    bounds: list of (min_price, max_price) tuples for each platform
    initial_guess: optional starting prices
    slack: small value to relax constraints
    debug: whether to print debug information
    """
    margins = np.array([p['margin'] for p in platforms])
    names = [p['name'] for p in platforms]

    if debug:
        print("Platforms and margins:")
        for i, (name, margin) in enumerate(zip(names, margins)):
            print(f"{i}: {name} - Margin: {margin:.2f}")
        print("\nPrice bounds:")
        for i, (low, high) in enumerate(bounds):
            print(f"{i}: ${low:.2f} - ${high:.2f}")

    # Objective: maximize total royalty with penalties to maintain proper separation
    def objective(prices):
        royalties = margins * prices
        total_royalty = np.sum(royalties)

        # Enhanced penalties to enforce proper separation between margin groups
        # and rewards for price differentiation
        penalty = 0
        reward = 0

        # Process margin groups penalties and rewards
        for i, margin_i in enumerate(unique_margins[:-1]):
            margin_j = unique_margins[i + 1]
            if len(margin_groups[margin_i]) > 0 and len(margin_groups[margin_j]) > 0:
                idx_i = margin_groups[margin_i][0]
                idx_j = margin_groups[margin_j][0]
                royalty_i = margin_i * prices[idx_i]
                royalty_j = margin_j * prices[idx_j]
                diff = royalty_i - royalty_j

                # Stronger penalties for small royalty differences
                min_desired_diff = 0.5  # Minimum desired royalty difference
                if diff < min_desired_diff:
                    penalty += (min_desired_diff - diff) * 20  # Increased penalty weight

                # Reward for maintaining good royalty separation
                optimal_diff = 2.0  # Optimal royalty difference
                if diff >= min_desired_diff and diff <= optimal_diff * 2:
                    reward += min(diff, optimal_diff) * 0.5  # Reward for good separation

        # Add rewards for price differentiation within same margin groups
        for margin, indices in margin_groups.items():
            if len(indices) > 1:
                prices_in_group = [prices[i] for i in indices]
                # Reward some price variation within the group
                price_range = max(prices_in_group) - min(prices_in_group)
                if price_range > 0 and price_range <= 5:  # Allow up to $5 difference
                    reward += price_range * 0.2  # Small reward for reasonable price differences

        if debug and np.random.random() < 0.01:  # Only print occasionally to avoid flooding
            print(f"Current prices: {prices.round(2)}")
            print(f"Current royalties: {royalties.round(2)}")
            print(f"Total royalty: ${total_royalty:.2f}, Penalty: {penalty:.2f}, Reward: {reward:.2f}")

        return -(total_royalty + reward - penalty)  # negative for minimization, with rewards and penalties

    # Group platforms with similar margins to simplify constraints
    unique_margins = sorted(set(margins), reverse=True)
    margin_groups = {margin: [i for i, m in enumerate(margins) if m == margin] for margin in unique_margins}

    if debug:
        print("\nMargin groups:")
        for margin, indices in margin_groups.items():
            platforms_in_group = [names[i] for i in indices]
            print(f"Margin {margin:.2f}: {platforms_in_group}")

    # Constraints:
    constraints = []
    constraint_descriptions = []  # For debugging

    # For platforms with different margins, ensure higher margin platforms get higher royalties
    for i, margin_i in enumerate(unique_margins[:-1]):
        margin_j = unique_margins[i + 1]

        # Create one representative constraint between margin groups
        # rather than all pairwise comparisons
        if len(margin_groups[margin_i]) > 0 and len(margin_groups[margin_j]) > 0:
            idx_i = margin_groups[margin_i][0]  # Representative from higher margin group
            idx_j = margin_groups[margin_j][0]  # Representative from lower margin group

            # Use a larger slack variable for specific constraints between margin groups
            # This addresses the constraint violations we observed
            constraint_slack = 0.05 if (margin_i == 0.70 and margin_j == 0.60) else 0.03 if (margin_i == 0.60 and margin_j == 0.55) else slack

            constraints.append({
                'type': 'ineq',
                'fun': lambda x, idx_i=idx_i, idx_j=idx_j, margin_i=margin_i, margin_j=margin_j, constraint_slack=constraint_slack:
                        margin_i * x[idx_i] - margin_j * x[idx_j] - constraint_slack
            })

            constraint_descriptions.append(
                f"Group {margin_i:.2f} ({names[idx_i]}) royalty >= Group {margin_j:.2f} ({names[idx_j]}) royalty"
            )

    # For platforms with identical margins, ensure they have similar prices
    # This makes the problem easier to solve while still being reasonable from a business perspective
    for margin, indices in margin_groups.items():
        if len(indices) > 1:
            primary_idx = indices[0]
            for secondary_idx in indices[1:]:
                # Allow small price differences between platforms with same margin
                # Allow larger price differences between platforms with same margin
                # Using 'eq' constraint type with a tolerance is too strict, so we use two inequality constraints
                max_price_diff = 5.0  # Allow up to $5 difference for greater flexibility
                # |price_i - price_j| <= max_price_diff
                # This is equivalent to: price_i - price_j <= max_price_diff AND price_j - price_i <= max_price_diff

                constraints.append({
                    'type': 'ineq',
                    'fun': lambda x, i=primary_idx, j=secondary_idx, diff=max_price_diff:
                            diff - (x[i] - x[j])  # price_i - price_j <= max_price_diff
                })

                constraints.append({
                    'type': 'ineq',
                    'fun': lambda x, i=primary_idx, j=secondary_idx, diff=max_price_diff:
                            diff - (x[j] - x[i])  # price_j - price_i <= max_price_diff
                })

                constraint_descriptions.append(
                    f"Similar prices ({names[primary_idx]} and {names[secondary_idx]}): |price difference| <= ${max_price_diff:.2f}"
                )

    # Initial guess - create better separation between margin groups
    if not initial_guess:
        # Create a map of margin to position within its bound range
        # Higher margins get higher positions in their ranges for better royalty separation
        margin_to_position = {}
        for i, margin in enumerate(unique_margins):
            # Position from 0.6 to 0.9 based on margin rank (higher margins get higher positions)
            # Increased range from 0.6-0.9 versus previous 0.7-0.9 for better differentiation
            position = 0.6 + (len(unique_margins) - 1 - i) * 0.3 / (len(unique_margins) - 1)
            margin_to_position[margin] = position

        initial_guess = []
        for i, (low, high) in enumerate(bounds):
            margin = margins[i]
            position = margin_to_position[margin]

            # Add small random variation for platforms with same margin to promote differentiation
            if len(margin_groups[margin]) > 1:
                # Get position within the same-margin group
                group_pos = margin_groups[margin].index(i) if i in margin_groups[margin] else 0
                # Add variation based on position in group
                variation = 0.05 * group_pos
                position = position + variation

            price = low + (high - low) * position
            initial_guess.append(price)

    if debug:
        print("\nInitial guess:")
        for i, price in enumerate(initial_guess):
            print(f"{names[i]}: ${price:.2f}")
            print(f"  Royalty: ${margins[i] * price:.2f}")

        # Check constraint feasibility for initial guess
        print("\nConstraint structure:")
        for i, description in enumerate(constraint_descriptions):
            print(f"C{i}: {description}")

        print("\nInitial constraint violations:")
        has_violations = False
        for i, constraint in enumerate(constraints):
            value = constraint['fun'](initial_guess)
            if value < 0:
                has_violations = True
                desc = constraint_descriptions[i] if i < len(constraint_descriptions) else "Price consistency"
                print(f"Constraint {i} ({desc}): {value:.4f} (violated)")
            elif debug and value < 0.1:
                desc = constraint_descriptions[i] if i < len(constraint_descriptions) else "Price consistency"
                print(f"Constraint {i} ({desc}): {value:.4f} (close to violation)")

        if not has_violations:
            print("No constraint violations in initial guess.")
        print()

    # Solve
    result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints,
                     options={'disp': debug, 'ftol': 1e-6, 'maxiter': 500})

    # Check if all constraints are satisfied with the solution
    if result.success and debug:
        prices = result.x
        print("\nFinal solution:")
        for i, price in enumerate(prices):
            print(f"{names[i]}: ${price:.2f}, Royalty: ${margins[i] * price:.2f}")

        print("\nConstraint satisfaction check:")
        all_satisfied = True
        for i, constraint in enumerate(constraints):
            value = constraint['fun'](prices)
            status = "satisfied" if value >= 0 else "VIOLATED"
            if value < 0:
                all_satisfied = False

            if i < len(constraint_descriptions):
                desc = constraint_descriptions[i]
                print(f"C{i} ({desc}): {value:.4f} - {status}")
            else:
                print(f"C{i}: {value:.4f} - {status}")

        print("\nConstraint satisfaction check:")
        all_satisfied = True
        for i, constraint in enumerate(constraints):
            value = constraint['fun'](prices)
            status = "satisfied" if value >= 0 else "VIOLATED"
            if value < 0:
                all_satisfied = False

            if i < len(constraint_descriptions):
                desc = constraint_descriptions[i]
                print(f"C{i} ({desc}): {value:.4f} - {status}")
            else:
                print(f"C{i}: {value:.4f} - {status}")

        # Add detailed report on royalty differences between margin groups
        print("\nRoyalty separation between margin groups:")
        for i, margin_i in enumerate(unique_margins[:-1]):
            margin_j = unique_margins[i + 1]
            if len(margin_groups[margin_i]) > 0 and len(margin_groups[margin_j]) > 0:
                idx_i = margin_groups[margin_i][0]
                idx_j = margin_groups[margin_j][0]
                royalty_i = margin_i * prices[idx_i]
                royalty_j = margin_j * prices[idx_j]
                diff = royalty_i - royalty_j
                print(f"Group {margin_i:.2f} ({names[idx_i]}, ${prices[idx_i]:.2f}) royalty: ${royalty_i:.2f}")
                print(f"Group {margin_j:.2f} ({names[idx_j]}, ${prices[idx_j]:.2f}) royalty: ${royalty_j:.2f}")
                print(f"Difference: ${diff:.2f}")
                if diff <= 0:
                    print("  WARNING: Higher margin group should have higher royalty")
                elif diff < 0.01:
                    print("  WARNING: Very small royalty difference between groups")
                print()

        print(f"\nAll constraints satisfied: {all_satisfied}")
        print(f"Objective value: ${-result.fun:.2f} (total royalty)")
        print(f"Optimization status: {result.message}")

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
        summary = summary.sort_values('Royalty per Unit', ascending=False).reset_index(drop=True)
    else:
        summary = pd.DataFrame({'Error': [result.message]})
    return summary

# Example use:
# platforms = [
#     {'name': 'Ebook (Direct)', 'margin': 0.95},
#     {'name': 'Paperback', 'margin': 0.55},
#     {'name': 'Ebook Other', 'margin': 0.35},
# ]
#
platforms = [
    {'name': 'MoKa Reads Shop', 'margin': 0.87},
    {'name': 'KDP Paperback', 'margin': 0.60},
    {'name': 'KDP Ebook', 'margin': 0.35},
    {'name': 'Leanpub', 'margin': 0.80},
    {'name': 'Kobo', 'margin': 0.70},
    {'name': 'Google Books', 'margin': 0.70},
    {'name': 'B&N Ebook', 'margin': 0.70},
    {'name': 'B&N Print', 'margin': 0.55},
]


price_bounds = [
    (10, 25),  # MoKa Reads Shop
    (15, 50),  # KDP Paperback
    (10, 40),  # KDP Ebook
    (10, 28),  # Leanpub
    (10, 28),  # Kobo
    (10, 28),  # Google Books
    (10, 28),  # B&N Ebook
    (15, 50),  # B&N Print
]

summary_df = optimize_pricing(platforms, price_bounds)

# Print the results
print("Optimized Pricing Summary:")
print(summary_df)
summary_df.to_csv('summary.csv', index=False)
