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

= Python Interpretation

The `optimizer.py` Python program is an interpretation of the previously stated problem, and uses the `uv` package manager to
run the program.
#v(10pt)
```bash
$ uv sync # syncs the dependencies
$ uv run optimizer.py # runs the optimizer script
```

The `optimize_pricing` function in the `optimizer` program expects two arguments, the platforms and price bounds.
The price bounds acts as the minimum and maximum price ranges a book of a particular platform can fall in.

#figure(
table(
  columns: 2, rows: 4, [*Platform Name*], [*Margin*], "Ebook (Direct)", $0.95$, "Paperback", $0.55$, "Ebook Other", $0.35$
), caption: "Example Platforms"
)

The example pricing bounds used were $(5, 20)$, $(10, 30)$ and $(15, 40)$. With these bounds the following summary is generated:

#table(columns: 5,..csv("summary.csv").flatten())
