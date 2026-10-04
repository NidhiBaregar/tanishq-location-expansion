import pandas as pd


# =========================================================
# L1 / L2 / L3 LOCATION CLASSIFICATION
# =========================================================

L1_LOCATIONS = {
    "Colaba",
    "Cuffe Parade",
    "Navy Nagar",
    "Fort",
    "Kala Ghoda",
    "Churchgate",
    "Marine Lines",
    "Girgaon",
    "Grant Road",
    "Tardeo",
    "Mahalaxmi",
    "Lower Parel",
    "Lower Parel West",
    "Worli",
    "Worli Sea Face",
    "Prabhadevi",
    "Prabhadevi South",
    "Bandra West",
    "Juhu",
    "Bandra Kurla Complex",
    "Hiranandani Gardens",
    "Powai"
}


L3_LOCATIONS = {
    "Mira Road",
    "Bhayandar",
    "Mira Bhayandar",
    "Virar",
    "Panvel",
    "Kharghar",
    "Dombivli",
    "Kalyan West",
    "Kalyan East",
    "Ulhasnagar",
    "Ambernath",
    "Bhiwandi",
    "Mankhurd",
    "Govandi",
    "Deonar",
    "Kurla West",
    "Kurla East",
    "Chunabhatti",
    "Kanjurmarg"
}


def get_location_tier(location):

    if location in L1_LOCATIONS:
        return "L1"

    elif location in L3_LOCATIONS:
        return "L3"

    else:
        return "L2"


# =========================================================
# TIER ASSUMPTIONS
# =========================================================

TIER_ASSUMPTIONS = {

    "L1": {
        "area": 4000,
        "fitout_per_sqft": 13750,
        "inventory_pct": 0.35,
        "working_capital": 0.80,
        "deposit_months": 6
    },

    "L2": {
        "area": 3000,
        "fitout_per_sqft": 13333.33,
        "inventory_pct": 0.28,
        "working_capital": 0.60,
        "deposit_months": 6
    },

    "L3": {
        "area": 2500,
        "fitout_per_sqft": 12000,
        "inventory_pct": 0.20,
        "working_capital": 0.40,
        "deposit_months": 6
    }
}


# =========================================================
# STORE FORMAT ASSUMPTIONS
# =========================================================

FORMAT_ADJUSTMENTS = {

    "Tanishq": {
        "area": 1.00,
        "fitout": 1.00,
        "inventory": 1.00,
        "working_capital": 1.00,
        "revenue": 1.00
    },

    "Mia": {
        "area": 0.20,
        "fitout": 0.35,
        "inventory": 0.25,
        "working_capital": 0.50,
        "revenue": 0.65
    },

    "Zoya": {
        "area": 0.35,
        "fitout": 0.50,
        "inventory": 0.40,
        "working_capital": 0.60,
        "revenue": 0.80
    }
}


# =========================================================
# REVENUE PREDICTION
# =========================================================

def predict_revenue(row, model, model_features, store_format):

    X = pd.DataFrame(
        [row[model_features].values],
        columns=model_features
    )

    base_revenue = float(
        model.predict(X)[0]
    )

    revenue_factor = FORMAT_ADJUSTMENTS[
        store_format
    ]["revenue"]

    revenue = (
        base_revenue
        * revenue_factor
    )

    return revenue


# =========================================================
# STORE INVESTMENT CALCULATION
# =========================================================

def calculate_investment(
    row,
    location_tier,
    store_format,
    revenue
):

    tier = TIER_ASSUMPTIONS[location_tier]

    format_adj = FORMAT_ADJUSTMENTS[store_format]


    # -----------------------------------------------------
    # Store Area
    # -----------------------------------------------------

    store_area = (
        tier["area"]
        * format_adj["area"]
    )


    # -----------------------------------------------------
    # Fit-out Cost
    # -----------------------------------------------------

    fitout_cost = (
        store_area
        * tier["fitout_per_sqft"]
        * format_adj["fitout"]
    ) / 1e7


    # -----------------------------------------------------
    # Inventory
    # -----------------------------------------------------

    inventory_cost = (
        revenue
        * tier["inventory_pct"]
        * format_adj["inventory"]
    )


    # -----------------------------------------------------
    # Annual Rent
    # -----------------------------------------------------

    annual_rent = (
        row["rental_cost_rs_sqft_month"]
        * store_area
        * 12
    )


    # -----------------------------------------------------
    # Rent Deposit
    # -----------------------------------------------------

    rent_deposit = (
        annual_rent
        * tier["deposit_months"]
        / 12
    ) / 1e7


    # -----------------------------------------------------
    # Working Capital
    # -----------------------------------------------------

    working_capital = (
        tier["working_capital"]
        * format_adj["working_capital"]
    )


    # -----------------------------------------------------
    # Total Investment
    # -----------------------------------------------------

    total_investment = (
        fitout_cost
        + inventory_cost
        + rent_deposit
        + working_capital
    )


    return {
        "store_area": store_area,
        "fitout_cost": fitout_cost,
        "inventory_cost": inventory_cost,
        "rent_deposit": rent_deposit,
        "working_capital": working_capital,
        "total_investment": total_investment
    }


# =========================================================
# STORE ECONOMICS
# =========================================================

def calculate_economics(
    revenue,
    total_investment
):

    operating_margin = 0.113


    annual_contribution = (
        revenue
        * operating_margin
    )


    roi = (
        annual_contribution
        / total_investment
    ) * 100


    payback = (
        total_investment
        / annual_contribution
        if annual_contribution > 0
        else 0
    )


    return {
        "annual_contribution": annual_contribution,
        "roi": roi,
        "payback": payback
    }


# =========================================================
# COMPLETE LOCATION CALCULATION
# =========================================================

def calculate_location(
    row,
    model,
    model_features,
    store_format
):

    location = row["location"]


    # Location tier
    location_tier = get_location_tier(
        location
    )


    # Revenue
    revenue = predict_revenue(
        row,
        model,
        model_features,
        store_format
    )


    # Investment
    investment = calculate_investment(
        row,
        location_tier,
        store_format,
        revenue
    )


    # Economics
    economics = calculate_economics(
        revenue,
        investment["total_investment"]
    )


    # -----------------------------------------------------
    # Combine results
    # -----------------------------------------------------

    result = {

        "location": location,

        "tier": location_tier,

        "format": store_format,

        "revenue": revenue,

        "store_area": investment["store_area"],

        "fitout_cost": investment["fitout_cost"],

        "inventory_cost": investment["inventory_cost"],

        "rent_deposit": investment["rent_deposit"],

        "working_capital": investment["working_capital"],

        "total_investment": investment["total_investment"],

        "annual_contribution":
            economics["annual_contribution"],

        "roi":
            economics["roi"],

        "payback":
            economics["payback"],

        # Market factors used by the Investment Planner ranking
        "customer_spending_index":
            row["customer_spending_index"],

        "network_gap_index":
            row["network_gap_index"],

        "accessibility_index":
            row["accessibility_index"],

        "competitor_presence_3km":
            row["competitor_presence_3km"],

        "cannibalisation_risk_index":
            row["cannibalisation_risk_index"]
    }


    return result


# =========================================================
# CALCULATE ALL LOCATIONS
# =========================================================

def calculate_all_locations(
    df,
    model,
    model_features,
    store_format
):

    results = []


    for _, row in df.iterrows():

        result = calculate_location(
            row,
            model,
            model_features,
            store_format
        )

        results.append(result)


    return pd.DataFrame(results)


# =========================================================
# BUDGET FILTER
# =========================================================

def filter_by_budget(
    results_df,
    budget
):

    return results_df[
        results_df["total_investment"] <= budget
    ].copy()


# =========================================================
# RANK LOCATIONS
# =========================================================

def rank_locations(
    results_df
):

    ranked = results_df.copy()

    def normalize(series):
        minimum = series.min()
        maximum = series.max()

        if maximum == minimum:
            return pd.Series(
                0.5,
                index=series.index
            )

        return (
            (series - minimum)
            / (maximum - minimum)
        )

    # Investment Score balances commercial upside with market quality.
    revenue_score = normalize(ranked["revenue"])
    roi_score = normalize(ranked["roi"])
    spending_score = normalize(ranked["customer_spending_index"])
    gap_score = normalize(ranked["network_gap_index"])
    accessibility_score = normalize(ranked["accessibility_index"])
    competition_score = 1 - normalize(
        ranked["competitor_presence_3km"]
    )
    cannibalisation_score = 1 - normalize(
        ranked["cannibalisation_risk_index"]
    )

    ranked["investment_score"] = (
        0.25 * revenue_score
        + 0.15 * roi_score
        + 0.25 * spending_score
        + 0.15 * gap_score
        + 0.05 * accessibility_score
        + 0.075 * competition_score
        + 0.075 * cannibalisation_score
    ) * 100

    ranked = ranked.sort_values(
        by=["investment_score", "roi", "payback"],
        ascending=[False, False, True]
    ).copy()

    ranked["rank"] = range(
        1,
        len(ranked) + 1
    )

    return ranked


# =========================================================
# GET BEST LOCATION WITHIN BUDGET
# =========================================================

def get_best_location(
    df,
    model,
    model_features,
    store_format,
    budget
):

    results = calculate_all_locations(
        df,
        model,
        model_features,
        store_format
    )


    feasible = filter_by_budget(
        results,
        budget
    )


    if feasible.empty:
        return None, results


    ranked = rank_locations(
        feasible
    )


    best_location = ranked.iloc[0].to_dict()


    return best_location, ranked