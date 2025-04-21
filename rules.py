import pandas as pd

def enforce_royalty_separation(platforms, min_diff=0.3):
    # Step 1: Sort platforms by descending margin
    platforms_sorted = sorted(platforms, key=lambda x: -x['margin'])

    results = []
    previous_royalty = None

    for i, p in enumerate(platforms_sorted):
        name = p['name']
        margin = p['margin']
        min_price, max_price = p['bounds']

        # Step 2: Determine price to satisfy royalty gap
        if previous_royalty is None:
            # First platform: use highest price allowed
            price = max_price
        else:
            # Determine max price that keeps royalty below previous_royalty - min_diff
            target_royalty = previous_royalty - min_diff
            price = target_royalty / margin
            price = min(price, max_price)

        # Clamp to lower bound
        price = max(price, min_price)
        royalty = round(margin * price, 2)
        previous_royalty = royalty

        results.append({
            'Platform': name,
            'Margin': margin,
            'Price': round(price, 2),
            'Royalty': royalty
        })

    df = pd.DataFrame(results)
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

df = enforce_royalty_separation(platforms)
print(df)
