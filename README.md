# DMR-Optimizer — Daily Milk Report Optimizer

![DMR Dashboard](assets/dashboard.png)

 DMR-Optimizer simplifies the preparation of a Daily Milk Report (DMR). Given the overall Fat and SNF targets, each society's quantity, and its relative quality level, it creates society-level Fat and SNF values that satisfy the required weighted totals.

The goal is to make DMR preparation fast, repeatable, and practically usable—while retaining the sharp, controlled result expected from an experienced human calculation.

## Why this project exists

An earlier approach used a Ridge Regression model to predict weighted Fat and SNF from historical DMR data. The model achieved high accuracy, but a prediction model cannot guarantee the near-exact result required for operational DMR preparation. It also depends on training data and becomes less practical as configurations, societies, or target conditions change.

This project replaces prediction with mathematical optimization. It does not train a model or depend on historical data. Instead, it uses the target values and the quality level assigned to each society to calculate an optimized allocation for the current report.

The idea was inspired by L1-style minimization: make the smallest necessary changes. That led to a Mixed-Integer Linear Programming (MILP) solution that minimizes unnecessary society-level adjustments while meeting the target within the permitted precision.

## What it does

For every DMR, the application accepts:

- Overall target Fat
- Overall target SNF
- Society name
- Society quantity
- Society quality level

It then generates a report containing each society's optimized Fat, SNF, Total Solids, weighted Fat, weighted SNF, and the final overall totals.

## Quality levels

Each society is assigned one of the following relative levels:

- `highest`
- `higher`
- `high`
- `average`
- `below average`
- `low`
- `lowest`

These levels define an initial Fat and SNF allocation around the overall target. The assumptions are implemented in `qlty_assumption.py`.

## How the optimization works

The workflow follows the same sequence implemented in `orchestration.py`:

1. Read the society names, levels, quantities, and overall Fat/SNF targets.
2. Assign an initial Fat and SNF value to each society according to its selected level.
3. Calculate the required overall weighted Fat and SNF totals.
4. Convert the society values to tenths and run MILP separately for Fat and SNF.
5. Find integer quality values within the allowed adjustment range that meet the weighted target tolerance.
6. Minimize the total absolute change from the initial level-based allocation.
7. Produce the final society-level DMR summary.

In simplified form, the optimizer seeks values that satisfy:

```text
target_low ≤ Σ(quantity × quality_in_tenths) ≤ target_high
```

while minimizing:

```text
Σ |optimized_quality − initial_quality|
```

This produces a target-driven result rather than a model prediction. It is scalable because each calculation is solved from the supplied DMR inputs; no retraining cycle or historical dataset is needed.

## Streamlit application

The Streamlit app keeps the society table available between calculations. Society names and levels remain unchanged until the user edits them.

Run the application from the project folder:

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

The application lets you edit the society table, generate an optimized DMR, review the final report, and download it as a CSV file.

## Project structure

```text
├── app.py                 # Streamlit user interface
├── orchestration.py       # Original command-line calculation flow
├── qlty_assumption.py     # Level-based Fat and SNF assumptions
├── qlty_optimization.py   # MILP optimization logic
├── final_data_output.py   # Final DMR report generation
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Technologies

- Python
- Streamlit
- Pandas and NumPy
- SciPy `milp`

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
