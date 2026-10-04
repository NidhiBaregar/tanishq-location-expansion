import streamlit as st
import pandas as pd
import joblib
import json
from pathlib import Path

from investment_math import get_best_location, calculate_all_locations


DATA_PATH = Path("candidate_locations.csv")
MODEL_PATH = Path("models/tanishq_sales_model.pkl")
FEATURE_PATH = Path("models/model_features.json")


def _format_inr_cr(value):
    return f"₹{value:.1f} Cr"


def _recommendation_reason(best, ranked):
    location = best["location"]
    score = best["investment_score"]
    roi = best["roi"]
    payback = best["payback"]
    revenue = best["revenue"]
    investment = best["total_investment"]

    return (
        f"{location} is the highest-ranked feasible location based on an "
        f"Investment Score of {score:.1f}/100. It combines "
        f"{_format_inr_cr(revenue)} predicted annual revenue with "
        f"{_format_inr_cr(investment)} estimated investment, "
        f"{roi:.1f}% estimated ROI and a {payback:.1f}-year payback."
    )


def show_investment_planner():
    df = pd.read_csv(DATA_PATH)

    model = joblib.load(MODEL_PATH)

    with open(FEATURE_PATH, "r") as f:
        model_features = json.load(f)

    st.header("Investment Parameters")

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        budget = st.number_input(
            "Investment Budget (₹ Cr)",
            min_value=1.0,
            max_value=100.0,
            value=15.0,
            step=1.0,
            key="investment_planner_budget"
        )

    with col2:
        store_format = st.selectbox(
            "Store Format",
            ["Tanishq", "Mia", "Zoya"],
            key="investment_planner_store_format"
        )

    # Calculate all locations once for the selected format.
    best_location, ranked = get_best_location(
        df,
        model,
        model_features,
        store_format,
        budget
    )

    if best_location is None:
        st.warning(
            f"No shortlisted location can be opened within a budget of "
            f"{_format_inr_cr(budget)} for the selected {store_format} format."
        )

        st.info(
            "Increase the investment budget or select a smaller store format "
            "to identify feasible locations."
        )

        return

    # ---------------------------------------------------------
    # RECOMMENDED LOCATION
    # ---------------------------------------------------------

    st.header("Recommended Location")

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.metric(
            "Recommended Location",
            best_location["location"]
        )

    with r2:
        st.metric(
            "Estimated Investment",
            _format_inr_cr(best_location["total_investment"])
        )

    with r3:
        st.metric(
            "Investment Score",
            f"{best_location['investment_score']:.1f}/100"
        )

    with r4:
        st.metric(
            "Payback Period",
            f"{best_location['payback']:.1f} Years"
        )

    st.info(_recommendation_reason(best_location, ranked))

    # ---------------------------------------------------------
    # RECOMMENDATION METRICS
    # ---------------------------------------------------------

    st.header("Investment Assessment")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "Predicted Annual Revenue",
            _format_inr_cr(best_location["revenue"])
        )

    with m2:
        st.metric(
            "Estimated Investment",
            _format_inr_cr(best_location["total_investment"])
        )

    with m3:
        st.metric(
            "Annual Contribution",
            _format_inr_cr(best_location["annual_contribution"])
        )

    with m4:
        st.metric(
            "Market Tier",
            best_location["tier"]
        )

    # ---------------------------------------------------------
    # FEASIBLE LOCATIONS
    # ---------------------------------------------------------

    st.header("Feasible Locations")

    display_df = ranked.head(10)[
        [
            "rank",
            "location",
            "tier",
            "revenue",
            "total_investment",
            "roi",
            "payback",
            "investment_score"
        ]
    ].copy()

    display_df.columns = [
        "Rank",
        "Location",
        "Tier",
        "Predicted Revenue (₹ Cr)",
        "Investment (₹ Cr)",
        "ROI (%)",
        "Payback (Years)",
        "Investment Score"
    ]

    st.dataframe(
        display_df.style.format(
            {
                "Predicted Revenue (₹ Cr)": "{:.1f}",
                "Investment (₹ Cr)": "{:.1f}",
                "ROI (%)": "{:.1f}",
                "Payback (Years)": "{:.1f}",
                "Investment Score": "{:.1f}",
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------------------------------------
    # TOP 3 TRADE-OFFS
    # ---------------------------------------------------------

    st.header("Investment Trade-offs")

    tradeoff_df = ranked.head(3).copy()

    t1, t2, t3 = st.columns(3)

    # Trade-offs are calculated across ALL feasible locations,
    # not only the top 3 ranked locations.
    highest_roi = ranked.sort_values(
        "roi", ascending=False
    ).iloc[0]

    highest_revenue = ranked.sort_values(
        "revenue", ascending=False
    ).iloc[0]

    lowest_investment = ranked.sort_values(
        "total_investment", ascending=True
    ).iloc[0]

    t1, t2, t3 = st.columns(3)

    with t1:
        st.metric(
            "Highest ROI",
            highest_roi["location"],
            f"{highest_roi['roi']:.1f}% ROI"
        )

    with t2:
        st.metric(
            "Highest Revenue",
            highest_revenue["location"],
            _format_inr_cr(highest_revenue["revenue"])
        )

    with t3:
        st.metric(
            "Lowest Investment",
            lowest_investment["location"],
            _format_inr_cr(lowest_investment["total_investment"])
        )

    # ---------------------------------------------------------
    # CALCULATION EXPLANATION
    # ---------------------------------------------------------

    with st.expander("How Is This Recommendation Calculated?"):
        st.write(
            "**Revenue:** XGBoost estimates annual revenue potential from the "
            "location characteristics and selected store format."
        )
        st.write(
            "**Investment:** Estimated from store size, fit-out, inventory, "
            "rent deposit and working capital assumptions. Fit-out benchmarks "
            "are calibrated to the selected L1/L2/L3 planning format."
        )
        st.write(
            "**Feasibility:** Only locations whose estimated total investment "
            "is within the selected budget are considered."
        )
        st.write(
            "**Ranking:** Feasible locations are ranked using an Investment "
            "Score that balances revenue potential, ROI, customer spending, "
            "network gap, accessibility, competition and cannibalisation risk."
        )
