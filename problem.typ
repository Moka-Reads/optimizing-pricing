#import "@preview/unequivocal-ams:0.1.2": ams-article

#show: ams-article.with(
  title: [Optimizing Pricing Strategy with Royalty Constraints],
  authors: (
    (
      name: "Mustafif Khan",
    ),
  ),
  abstract: none,
  bibliography: none,
)

= Problem Formulation
<problem-formulation>
Suppose there are $n$ platforms or sales formats (e.g., Ebook, Paperback, Retail), each with:

- A unit price $p_i$ for format $i$

- A royalty margin $m_i in [0 , 1]$ such that you receive $m_i dot.op p_i$ as earnings per unit

We seek to determine the optimal price vector $upright(bold(p)) = [p_1 , p_2 , dots.h , p_n]$ that:

+ Maximizes total royalty revenue per unit: $ max_(upright(bold(p))) quad R (upright(bold(p))) = sum_(i = 1)^n m_i p_i $

+ Subject to price ordering to reflect increasing value or production cost: $ p_1 < p_2 < dots.h < p_n $

+ And royalty-per-unit support to reflect preference for higher-margin formats: $ m_1 p_1 gt.eq m_2 p_2 gt.eq dots.h gt.eq m_n p_n $

+ With bounds: $ p_i in [underline(p)_i , overline(p)_i] quad forall i = 1 , dots.h , n $

This is a constrained nonlinear optimization problem that can be solved using numerical methods (e.g., Sequential Least Squares Programming).

= Interpretation
<interpretation>
The resulting prices ${ p_i }$ ensure:

- Readers save more by choosing digital or direct options

- Your royalty per sale does not decrease as price increases

- The price structure aligns with perceived value and incentivizes support

// = Python Interpretation

// The `optimizer.py` Python program is an interpretation of the previously stated problem, and uses the `uv` package manager to
// run the program.
// #v(10pt)
// ```bash
// $ uv sync # syncs the dependencies
// $ uv run optimizer.py # runs the optimizer script
// ```

// The `optimize_pricing` function in the `optimizer` program expects two arguments, the platforms and price bounds.
// The price bounds acts as the minimum and maximum price ranges a book of a particular platform can fall in.

// #figure(
// table(
//   columns: 2, rows: 4, [*Platform Name*], [*Margin*], "Ebook (Direct)", $0.95$, "Paperback", $0.55$, "Ebook Other", $0.35$
// ), caption: "Example Platforms"
// )

// The example pricing bounds used were $(5, 20)$, $(10, 30)$ and $(15, 40)$. With these bounds the following summary is generated:

// #table(columns: 5,..csv("summary.csv").flatten())


= Algorithmic Extensions for Practical Pricing Optimization <algorithmic-extensions-for-practical-pricing-optimization>
To address the real-world challenges of fair and strategic pricing across multiple publishing platforms, we enhance the core optimization model with several algorithmic improvements. These adjustments ensure that the model remains robust, interpretable, and aligned with both business constraints and reader incentives.

== Grouped Margin Constraints <grouped-margin-constraints>
We group platforms by their royalty margins $m_i$ and enforce ordering only between different groups. This reduces constraint complexity while ensuring that higher-margin platforms receive no less royalty per unit than lower-margin ones.

$ m_i p_i gt.eq m_j p_j + epsilon quad upright("if ") m_i > m_j $

Here, $epsilon gt.eq 0$ is a small slack variable used to relax the constraint. Only a representative platform from each group is selected to avoid over-constraining the model.

*Why this helps*: <why-this-helps>
- Reduces redundant comparisons (e.g., Kobo vs. B&N if both have 70% margin)

- Preserves interpretable tiering of platforms

- Scales better with many distribution channels

== Slack-Relaxed Constraint Design <slack-relaxed-constraint-design>
Constraints between groups are softened using a margin-specific slack term $epsilon$, chosen adaptively depending on the closeness of the margins.

$ m_i p_i - m_j p_j gt.eq epsilon_(i j) $

This prevents infeasibility in near-equal margin scenarios.

Why this helps: <why-this-helps-1>
- Avoids optimization failure when margins are close (e.g., 0.70 vs. 0.68)

- Allows minor trade-offs while preserving intended ranking

- Encourages feasible and realistic solutions

== Penalty and Reward Adjustment in Objective Function <penalty-and-reward-adjustment-in-objective-function>
To strengthen the incentive structure, we define a modified objective function:

$ max [sum_(i = 1)^n m_i p_i + lambda_r dot.op upright("Reward") (p) - lambda_p dot.op upright("Penalty") (p)] $

Where:

- $upright("Reward") (p)$: encourages good separation between royalty tiers

- $upright("Penalty") (p)$: discourages near-equal royalties across tiers

- $lambda_r , lambda_p$: tunable coefficients controlling influence

Why this helps: <why-this-helps-2>
- Avoids scenarios where high-margin formats yield similar or lower royalties

- Promotes meaningful separation in earnings

- Reinforces incentive-aligned pricing structures

== Intra-Group Price Differentiation <intra-group-price-differentiation>
For platforms within the same margin group, we allow soft variability in pricing, while bounding the maximum price difference:

$ lr(|p_i - p_j|) lt.eq Delta quad upright("for ") i , j in upright("same group") $

With $Delta approx 5$ dollars.

Why this helps: <why-this-helps-3>
- Reflects real-world variation across similarly-royaltied stores

- Prevents artificially flat or uniform pricing

- Provides flexibility to account for user base, store UX, etc.

== Smart Initialization Based on Margin Rank <smart-initialization-based-on-margin-rank>
The initial guess for pricing is informed by royalty margin rank: $ p_i^((0)) = underline(p)_i + (frac(r (m_i), R)) (overline(p)_i - underline(p)_i) $ Where $r (m_i)$ is the rank of margin $m_i$ and $R$ is the total number of unique margin levels.

Why this helps: <why-this-helps-4>
- Improves convergence of the solver

- Reduces likelihood of landing in poor local minima

- Encourages desirable separation right from initialization

== Constraint Diagnostics and Validation <constraint-diagnostics-and-validation>
The model logs constraint values, satisfaction status, and relative royalty differences between groups to ensure solution validity. This supports both verification and transparency for adoption in academic, open-access, or educational publishing models.

Why this helps: <why-this-helps-5>
- Confirms correctness of solution

- Aids interpretability and justification for pricing tiers

- Facilitates deployment in systems with trust or auditing needs

== Summary <summary>
Together, these enhancements ensure that the optimization model:

- Maintains structural fairness (higher margin $arrow.r.double$ higher royalty)

- Encourages readers to support authors while still saving money

- Produces robust, explainable, and incentive-aligned pricing strategies