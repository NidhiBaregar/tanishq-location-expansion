import streamlit as st
import pandas as pd
import joblib
import json
from pathlib import Path

from investment_math import calculate_location

DATA_PATH = Path("candidate_locations.csv")
MODEL_PATH = Path("models/tanishq_sales_model.pkl")
FEATURE_PATH = Path("models/model_features.json")


def show_market_explorer():
    df = pd.read_csv(DATA_PATH)
    model = joblib.load(MODEL_PATH)
    with open(FEATURE_PATH, "r") as f:
        model_features = json.load(f)

    

    st.header("Location / Format")
    col1, col2 = st.columns([1, 1], gap="medium")
    with col1:
        location = st.selectbox("Location", df["location"].tolist(), key="market_explorer_location")
    with col2:
        store_format = st.selectbox("Store Format", ["Tanishq", "Mia", "Zoya"], key="market_explorer_store_format")

    row = df[df["location"] == location].iloc[0]

    # Use the shared investment_math module as the single source
    # for tier, revenue, investment and store economics.
    result = calculate_location(
        row,
        model,
        model_features,
        store_format
    )

    revenue = result["revenue"]
    location_tier = result["tier"]
    fitout_cost = result["fitout_cost"]
    inventory_cost = result["inventory_cost"]
    rent_deposit = result["rent_deposit"]
    working_capital = result["working_capital"]
    total_investment = result["total_investment"]
    annual_contribution = result["annual_contribution"]
    roi = result["roi"]
    payback = result["payback"]
    store_area = result["store_area"]

    estimated_monthly_spend = int(row["estimated_monthly_customer_spend_rs"])
    monthly_footfall = (row["footfall_estimate_index"] / 100) * 1_000_000

    st.header("Market Classification")
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Market Tier", location_tier)
    with m2: st.metric("Customer Spending", f"₹{estimated_monthly_spend:,.0f}")
    with m3: st.metric("Recommended Format Size", f"{store_area:,.0f} sq.ft")

    st.header("Existing Group Presence")
    g1, g2, g3 = st.columns(3)
    with g1: st.metric("Tanishq Stores", f"{row['existing_tanishq_stores_3km']:.0f}")
    with g2: st.metric("Mia Stores", f"{row['existing_mia_stores_3km']:.0f}")
    with g3: st.metric("Zoya Stores", f"{row['existing_zoya_stores_3km']:.0f}")

    st.header("Investment Assessment")
    i1, i2, i3, i4 = st.columns(4)
    with i1: st.metric("Fit-out", f"₹{fitout_cost:.1f} Cr")
    with i2: st.metric("Inventory", f"₹{inventory_cost:.1f} Cr")
    with i3: st.metric("Rent Deposit", f"₹{rent_deposit:.1f} Cr")
    with i4: st.metric("Working Capital", f"₹{working_capital:.1f} Cr")
    st.metric("Estimated Total Investment", f"₹{total_investment:.1f} Cr")

    st.header("Store Economics")
    e1, e2, e3, e4 = st.columns(4)
    with e1: st.metric("Predicted Annual Revenue", f"₹{revenue:.1f} Cr")
    with e2: st.metric("Estimated ROI", f"{roi:.1f}%")
    with e3: st.metric("Payback Period", f"{payback:.1f} Years")
    with e4: st.metric("Annual Contribution", f"₹{annual_contribution:.1f} Cr")

    st.header("Why This Location?")
    footfall = row["footfall_estimate_index"]
    spending = row["customer_spending_index"]
    competition = row["competitor_presence_3km"]
    accessibility = row["accessibility_index"]
    network_gap = row["network_gap_index"]
    rent = row["rental_cost_rs_sqft_month"]

    if location_tier == "L1":
        if spending >= 85 and footfall >= 80:
            why_text = f"{location} combines strong customer spending with high retail traffic, supporting a premium-format store. The opportunity comes with higher rental and investment requirements."
        elif spending >= 85:
            why_text = f"{location} has strong customer spending potential, making it well suited to a premium Tanishq presence. Higher market costs are the main trade-off."
        elif footfall >= 80:
            why_text = f"{location} benefits from strong retail traffic and visibility, creating significant customer acquisition potential. The premium market also requires higher capital deployment."
        else:
            why_text = f"{location} is positioned as a premium catchment with strong commercial potential. The main trade-off is the higher cost of establishing a presence."
    elif location_tier == "L2":
        if network_gap >= 70 and competition <= 5:
            why_text = f"{location} offers an attractive network gap with relatively limited competitive pressure. This creates an opportunity to expand the group presence without entering an oversupplied market."
        elif footfall >= 75 and spending >= 75:
            why_text = f"{location} combines healthy retail traffic with good customer spending potential. It offers a balanced expansion opportunity without the cost profile of a premium market."
        elif accessibility >= 85:
            why_text = f"{location} benefits from strong accessibility, making it easier to reach a broad customer base. The opportunity offers a balanced trade-off between market reach and investment."
        elif rent <= 300:
            why_text = f"{location} offers a relatively attractive cost structure while retaining established retail demand. Lower occupancy costs improve the economics of expansion."
        elif competition >= 7:
            why_text = f"{location} has established retail demand but faces relatively strong competitive intensity. Expansion is viable, although differentiation and store positioning will be important."
        else:
            why_text = f"{location} offers a balanced combination of customer demand, accessibility and investment requirements, making it suitable for measured network expansion."
    else:
        if network_gap >= 75 and competition <= 4:
            why_text = f"{location} represents a relatively open market with limited competitive and group presence. It provides an opportunity to build network presence at a lower entry cost."
        elif rent <= 200:
            why_text = f"{location} offers a lower-cost entry point, with relatively affordable retail space. The trade-off is lower premium-market demand compared with established catchments."
        elif footfall >= 60:
            why_text = f"{location} shows promising customer traffic for an emerging catchment. A smaller-format entry could test demand before committing to a larger store."
        else:
            why_text = f"{location} is an emerging catchment with lower entry costs. It offers a network expansion opportunity, although demand potential is more limited than higher-tier markets."

    st.info(why_text)

    st.header("Market Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Population", f"{row['population_3km']:,.0f}")
    with c2: st.metric("Customer Spending", f"₹{estimated_monthly_spend:,.0f}")
    with c3: st.metric("Monthly Footfall", f"{monthly_footfall / 1_000_000:.1f}M")
    with c4: st.metric("Competitors", f"{row['competitor_presence_3km']:.0f}")
    with c5: st.metric("Monthly Rent", f"₹{row['rental_cost_rs_sqft_month']:,.0f}/sq.ft")

    with st.expander("How Is This Estimate Calculated?"):
        st.write("**Revenue:** XGBoost estimates annual revenue using population, income, footfall, competition, rent, accessibility, spending and existing network presence.")
        st.write("**Market Tier:** Locations are grouped into L1, L2 or L3 based on their retail-market characteristics.")
        st.write("**Investment:** Investment is estimated separately using store size, fit-out cost, inventory requirement, rent deposit and working capital assumptions.")
        st.write("**Customer Spending:** Monthly customer spending is taken from the location-level planning estimate in the dataset.")
        st.write("**ROI:** Annual contribution ÷ estimated investment.")
        st.write("**Payback:** Estimated investment ÷ annual contribution.")
