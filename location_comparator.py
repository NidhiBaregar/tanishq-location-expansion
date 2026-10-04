import streamlit as st
import pandas as pd
import joblib
import json
from pathlib import Path

from investment_math import calculate_location


DATA_PATH = Path("candidate_locations.csv")
MODEL_PATH = Path("models/tanishq_sales_model.pkl")
FEATURE_PATH = Path("models/model_features.json")


def _normalise(values):
    minimum = values.min()
    maximum = values.max()

    if maximum == minimum:
        return pd.Series(0.5, index=values.index)

    return (values - minimum) / (maximum - minimum)


def show_location_comparator():

    df = pd.read_csv(DATA_PATH)
    model = joblib.load(MODEL_PATH)

    with open(FEATURE_PATH, "r") as f:
        model_features = json.load(f)

    st.header("Comparison Parameters")

    # ---------------------------------------------------------
    # STEP 1 — NUMBER OF LOCATIONS
    # ---------------------------------------------------------

    number_of_locations = st.selectbox(
        "How many locations do you want to compare?",
        [2, 3, 4],
        index=1,
        key="comparator_number_of_locations"
    )

    st.markdown(
        "Select the locations you want to evaluate side by side."
    )

    # ---------------------------------------------------------
    # STEP 2 — LOCATION SELECTION
    # ---------------------------------------------------------

    selected_locations = []

    cols = st.columns(number_of_locations)

    for i, col in enumerate(cols):
        with col:
            location = st.selectbox(
                f"Location {i + 1}",
                df["location"].tolist(),
                key=f"comparator_location_{i}"
            )
            selected_locations.append(location)

    # Prevent duplicate selections.
    if len(set(selected_locations)) != len(selected_locations):
        st.warning(
            "Please select a different location in each comparison slot."
        )
        return

    # ---------------------------------------------------------
    # STORE FORMAT
    # ---------------------------------------------------------

    store_format = st.selectbox(
        "Store Format",
        ["Tanishq", "Mia", "Zoya"],
        key="comparator_store_format"
    )

    # ---------------------------------------------------------
    # CALCULATE SHARED ECONOMICS
    # ---------------------------------------------------------

    results = []

    for location in selected_locations:

        row = df[df["location"] == location].iloc[0]

        result = calculate_location(
            row,
            model,
            model_features,
            store_format
        )

        result["location"] = location
        results.append(result)

    comparison = pd.DataFrame(results)

    # ---------------------------------------------------------
    # WEIGHTS
    # ---------------------------------------------------------

    st.header("Comparison Weights")

    st.markdown(
        "Adjust the importance of each factor. The weights determine "
        "the final comparison score."
    )

    w1, w2, w3 = st.columns(3)

    with w1:
        demand_weight = st.slider(
            "Revenue Potential",
            0,
            100,
            30,
            5,
            key="comparator_revenue_weight"
        )

    with w2:
        spending_weight = st.slider(
            "Customer Spending",
            0,
            100,
            20,
            5,
            key="comparator_spending_weight"
        )

    with w3:
        gap_weight = st.slider(
            "Network Gap",
            0,
            100,
            20,
            5,
            key="comparator_gap_weight"
        )

    w4, w5, w6 = st.columns(3)

    with w4:
        accessibility_weight = st.slider(
            "Accessibility",
            0,
            100,
            10,
            5,
            key="comparator_accessibility_weight"
        )

    with w5:
        competition_weight = st.slider(
            "Low Competition",
            0,
            100,
            10,
            5,
            key="comparator_competition_weight"
        )

    with w6:
        investment_weight = st.slider(
            "Investment Efficiency",
            0,
            100,
            10,
            5,
            key="comparator_investment_weight"
        )

    total_weight = (
        demand_weight
        + spending_weight
        + gap_weight
        + accessibility_weight
        + competition_weight
        + investment_weight
    )

    if total_weight == 0:
        st.warning("Please assign at least some weight to the comparison factors.")
        return

    # ---------------------------------------------------------
    # BUILD COMPARISON SCORE
    # ---------------------------------------------------------

    revenue_score = _normalise(comparison["revenue"])
    spending_score = _normalise(comparison["customer_spending_index"])
    gap_score = _normalise(comparison["network_gap_index"])
    accessibility_score = _normalise(comparison["accessibility_index"])

    competition_score = 1 - _normalise(
        comparison["competitor_presence_3km"]
    )

    investment_score = 1 - _normalise(
        comparison["total_investment"]
    )

    comparison["comparison_score"] = (
        demand_weight * revenue_score
        + spending_weight * spending_score
        + gap_weight * gap_score
        + accessibility_weight * accessibility_score
        + competition_weight * competition_score
        + investment_weight * investment_score
    ) / total_weight * 100

    comparison = comparison.sort_values(
        "comparison_score",
        ascending=False
    ).reset_index(drop=True)

    comparison["rank"] = range(1, len(comparison) + 1)

    # ---------------------------------------------------------
    # WINNER
    # ---------------------------------------------------------

    winner = comparison.iloc[0]

    st.header("Comparison Result")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "Recommended Location",
            winner["location"]
        )

    with m2:
        st.metric(
            "Comparison Score",
            f"{winner['comparison_score']:.1f}/100"
        )

    with m3:
        st.metric(
            "Predicted Revenue",
            f"₹{winner['revenue']:.1f} Cr"
        )

    with m4:
        st.metric(
            "Estimated ROI",
            f"{winner['roi']:.1f}%"
        )

    # ---------------------------------------------------------
    # SIDE-BY-SIDE COMPARISON
    # ---------------------------------------------------------

    st.header("Location Comparison")

    display = comparison[
        [
            "rank",
            "location",
            "tier",
            "revenue",
            "total_investment",
            "roi",
            "payback",
            "comparison_score"
        ]
    ].copy()

    display.columns = [
        "Rank",
        "Location",
        "Tier",
        "Predicted Revenue (₹ Cr)",
        "Investment (₹ Cr)",
        "ROI (%)",
        "Payback (Years)",
        "Comparison Score"
    ]

    st.dataframe(
        display.style.format(
            {
                "Predicted Revenue (₹ Cr)": "{:.1f}",
                "Investment (₹ Cr)": "{:.1f}",
                "ROI (%)": "{:.1f}",
                "Payback (Years)": "{:.1f}",
                "Comparison Score": "{:.1f}",
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------------------------------------
    # TRADE-OFF EXPLANATION
    # ---------------------------------------------------------

    st.header("Why This Location Ranks First")

    st.info(
        f"{winner['location']} ranks first with a comparison score of "
        f"{winner['comparison_score']:.1f}/100 under the selected weights. "
        f"The score reflects the relative balance of revenue potential, "
        f"customer spending, network gap, accessibility, competition and "
        f"investment efficiency across the selected locations."
    )

    with st.expander("How Is This Comparison Calculated?"):
        st.write(
            "Each selected location is first evaluated using the same "
            "revenue, investment, ROI and payback calculations used in "
            "the Market Explorer and Investment Planner."
        )
        st.write(
            "The selected comparison factors are then normalised across "
            "the locations being compared."
        )
        st.write(
            "Higher revenue, spending, network gap and accessibility "
            "increase the score. Lower competition and lower investment "
            "increase the score."
        )
        st.write(
            "The final score is the weighted average of these factors."
        )
