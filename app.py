"""Streamlit UI for the calculation pipeline defined in orchestration.py."""

import pandas as pd
import streamlit as st

from final_data_output import create_society_summary_report
from qlty_assumption import (
    Fat_level_pipeline,
    SNF_level_pipeline,
    qlty_wqlty,
    set_W_assumption,
)
from qlty_optimization import solve_qlty_nudge


# These values must remain identical to the level names used in qlty_assumption.py.
LEVELS = ("highest", "higher", "high", "average", "below average", "low", "lowest")
TABLE_COLUMNS = ["Society Name", "Level", "Quantity"]
INITIAL_SOCIETIES = pd.DataFrame(
    [
        {"Society Name": "A", "Level": "average", "Quantity": 100},
        {"Society Name": "B", "Level": "high", "Quantity": 150},
        {"Society Name": "C", "Level": "higher", "Quantity": 555},
        {"Society Name": "D", "Level": "below average", "Quantity": 253},
        {"Society Name": "E", "Level": "low", "Quantity": 102},
        {"Society Name": "F", "Level": "lowest", "Quantity": 75},
        {"Society Name": "G", "Level": "average", "Quantity": 165},
        {"Society Name": "H", "Level": "highest", "Quantity": 608}
    ],
    columns=TABLE_COLUMNS,
)


def prepare_societies(table: pd.DataFrame) -> tuple[dict, dict, pd.DataFrame]:
    """Validate UI data and construct the two inputs expected by orchestration.py."""
    rows = table.copy().reindex(columns=TABLE_COLUMNS).dropna(how="all")
    if rows.empty:
        raise ValueError("Add at least one society.")

    rows["Society Name"] = rows["Society Name"].fillna("").astype(str).str.strip()
    rows["Level"] = rows["Level"].fillna("").astype(str).str.strip().str.lower()
    rows["Quantity"] = pd.to_numeric(rows["Quantity"], errors="coerce")

    if (rows["Society Name"] == "").any():
        raise ValueError("Every society must have a name.")
    if rows["Society Name"].duplicated().any():
        raise ValueError("Society names must be unique.")
    if (~rows["Level"].isin(LEVELS)).any():
        raise ValueError("Choose one of the listed levels for every society.")
    if rows["Quantity"].isna().any() or (rows["Quantity"] <= 0).any():
        raise ValueError("Each quantity must be a positive whole number.")
    if (rows["Quantity"] % 1 != 0).any():
        raise ValueError("Each quantity must be a whole number.")

    rows["Quantity"] = rows["Quantity"].astype(int)

    # Exact structures produced by get_name_level() and the quantity input loop.
    society_details = {}
    quantities = {}
    for record in rows.to_dict("records"):
        name = record["Society Name"]
        society_details[name] = [record["Level"]]
        quantities[name] = record["Quantity"]
    return society_details, quantities, rows


def generate_report(table: pd.DataFrame, overall_fat: float, overall_snf: float) -> pd.DataFrame:
    """Execute the unmodified orchestration.py sequence using Streamlit inputs."""
    society_details, quantities, _ = prepare_societies(table)

    fat_details, weighted_fat, _ = set_W_assumption(
        society_details, overall_fat, quantities, Fat_level_pipeline
    )
    snf_details, weighted_snf, _ = set_W_assumption(
        society_details, overall_snf, quantities, SNF_level_pipeline
    )

    qty = [details[1] for details in fat_details.values()]
    fat_pre = [details[2] * 10 for details in fat_details.values()]
    snf_pre = [details[2] * 10 for details in snf_details.values()]

    fat_result = solve_qlty_nudge(
        qty, fat_pre, weighted_fat * 1000 - 1, weighted_fat * 1000 + 1, max_step=2
    )
    snf_result = solve_qlty_nudge(
        qty, snf_pre, weighted_snf * 1000 - 1, weighted_snf * 1000 + 1, max_step=2
    )
    if fat_result is None or snf_result is None:
        raise ValueError(
            "The requested targets cannot be met with the current society quantities and ±0.2 adjustment limit."
        )

    # solve_qlty_nudge returns (solution, scipy_result); only solution is used next.
    fat_solution = fat_result[0]
    snf_solution = snf_result[0]
    final_fat = qlty_wqlty(fat_details, fat_solution)
    final_snf = qlty_wqlty(snf_details, snf_solution)
    return create_society_summary_report(final_fat, final_snf)


st.set_page_config(page_title="DMR Quality Optimizer", page_icon="🥛", layout="wide")
st.title("🥛 Daily Milk Report Quality Optimizer")
st.caption("Enter society details, then generate a Fat and SNF optimized DMR.")

if "society_rows" not in st.session_state:
    st.session_state.society_rows = INITIAL_SOCIETIES.copy()

left, right = st.columns(2)
with left:
    overall_fat = st.number_input("Overall Fat", min_value=3.3, value=4.0, step=0.1, format="%.1f")
with right:
    overall_snf = st.number_input("Overall SNF", min_value=7.7, value=8.0, step=0.1, format="%.1f")

st.subheader("Societies")
st.info("Names and levels stay unchanged between calculations. Edit a cell only when you want to change it.")
edited_rows = st.data_editor(
    st.session_state.society_rows,
    key="society_table_v3",
    num_rows="dynamic",
    hide_index=True,
    width="stretch",
    column_config={
        "Society Name": st.column_config.TextColumn("Society Name", required=True),
        "Level": st.column_config.SelectboxColumn("Level", options=LEVELS, required=True),
        "Quantity": st.column_config.NumberColumn("Quantity", min_value=1, step=1, required=True),
    },
)

# Store every table edit so the same names and levels are used until the user changes them.
st.session_state.society_rows = edited_rows.copy()

if st.button("Generate optimized DMR", type="primary"):
    try:
        with st.spinner("Running the allocation and MILP optimization..."):
            report = generate_report(edited_rows, float(overall_fat), float(overall_snf))
        st.session_state.report = report
        st.success("DMR generated successfully.")
    except (ValueError, KeyError, TypeError) as error:
        st.session_state.pop("report", None)
        st.error(str(error))
    except Exception:
        st.session_state.pop("report", None)
        st.error("The optimizer could not complete this calculation. Check the society values and try again.")

if "report" in st.session_state:
    st.subheader("Optimized DMR")
    report = st.session_state.report
    st.dataframe(report, width="stretch")
    st.download_button(
        "Download report as CSV",
        report.to_csv().encode("utf-8"),
        file_name="optimized_dmr_report.csv",
        mime="text/csv",
    )
