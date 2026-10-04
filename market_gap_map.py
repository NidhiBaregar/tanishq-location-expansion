import streamlit as st
import pandas as pd
import pydeck as pdk
from pathlib import Path


DATA_PATH = Path("candidate_locations.csv")
STORE_PATH = Path("store_locations.csv")


# Brand-aligned map palette
BURGUNDY = [100, 28, 41]
ANTIQUE_ROSE = [154, 92, 107]
BRONZE = [155, 106, 69]
PLUM = [86, 52, 72]
MUTED = [117, 107, 100]
CREAM = [245, 238, 227]


def _normalise(series):
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(0.5, index=series.index)

    return (series - minimum) / (maximum - minimum)


def show_market_gap_map():

    candidates = pd.read_csv(DATA_PATH)
    stores = pd.read_csv(STORE_PATH)

    # Only genuine stores are shown on the map.
    # market_reference rows are deliberately excluded.
    stores = stores[
        stores["record_type"].eq("store")
    ].copy()

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    st.markdown(
        """
        <style>
        /* Center Tab 4 navigation and content */
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center !important;
        }

        .stTabs [data-baseweb="tab"] {
            text-align: center !important;
        }

        .stTabs [data-baseweb="tab-highlight"] {
            margin-left: auto !important;
            margin-right: auto !important;
        }

        /* Center Tab 4 section headings */
        .market-gap-heading {
            text-align: center;
            font-family: 'Libre Baskerville', serif;
            color: #641C29;
            font-size: 1.42rem;
            font-weight: 700;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }

        /* Clean, balanced map controls */
        .map-control-label {
            text-align: center;
            color: #563448;
            font-family: 'Source Sans 3', sans-serif;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 6px;
        }

        div[data-testid="stSelectbox"] > div {
            max-width: 360px;
            margin: 0 auto;
        }

        div[data-testid="stCheckbox"] {
            display: flex;
            justify-content: center;
            padding-top: 8px;
        }

        div[data-testid="stCheckbox"] label {
            color: #563448 !important;
            font-size: 12px !important;
        }

        /* Center the legend text */
        .market-gap-legend {
            text-align: center;
        }
        </style>

        <div class="market-gap-heading">Market Gap Map</div>

        <div style="
            text-align:center;
            color:#756B64;
            font-family:'Source Sans 3', sans-serif;
            font-size:12px;
            margin-top:-6px;
            margin-bottom:12px;
        ">
            Identify high-potential markets where Tanishq Group presence
            is limited relative to local demand.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # CONTROLS
    # ---------------------------------------------------------

    control_left, control_right = st.columns(2, gap="large")

    with control_left:
        st.markdown(
            '<div class="map-control-label">Opportunity Markets</div>',
            unsafe_allow_html=True,
        )
        opportunity_markets = st.selectbox(
            "Opportunity Markets",
            [10, 15, 20],
            index=1,
            key="gap_map_opportunity_count",
            label_visibility="collapsed",
        )

    with control_right:
        st.markdown(
            '<div class="map-control-label">Map Layers</div>',
            unsafe_allow_html=True,
        )
        show_competitors = st.checkbox(
            "Show competitor network",
            value=True,
            key="gap_map_show_competitors",
        )

    # ---------------------------------------------------------
    # MARKET OPPORTUNITY INDEX
    # ---------------------------------------------------------

    candidates["market_opportunity_score"] = (
        0.40 * _normalise(
            candidates["estimated_annual_sales_potential_cr"]
        )
        + 0.30 * _normalise(
            candidates["network_gap_index"]
        )
        + 0.15 * _normalise(
            candidates["customer_spending_index"]
        )
        + 0.10 * _normalise(
            candidates["accessibility_index"]
        )
        + 0.05 * (
            1 - _normalise(
                candidates["competitor_presence_3km"]
            )
        )
    ) * 100

    opportunity = candidates.sort_values(
        "market_opportunity_score",
        ascending=False
    ).head(opportunity_markets).copy()

    opportunity["size"] = 100 + (
        opportunity["market_opportunity_score"] * 4
    )

    # Unified tooltip fields so the same map tooltip works for
    # both opportunity markets and actual stores.
    opportunity["map_title"] = opportunity["location"]
    opportunity["map_line_1"] = (
        "Market opportunity: "
        + opportunity["market_opportunity_score"].round(1).astype(str)
    )
    opportunity["map_line_2"] = (
        "Revenue potential: ₹"
        + opportunity["estimated_annual_sales_potential_cr"].round(1).astype(str)
        + " Cr"
    )
    opportunity["map_line_3"] = (
        "Network gap: "
        + opportunity["network_gap_index"].round(0).astype(str)
    )
    opportunity["map_line_4"] = (
        "Competition: "
        + opportunity["competitor_presence_3km"].round(0).astype(str)
    )

    # ---------------------------------------------------------
    # MAP DATA
    # ---------------------------------------------------------

    own_stores = stores[
        stores["network_type"].isin(
            ["Tanishq", "Tanishq Group"]
        )
    ].copy()

    competitors = stores[
        stores["network_type"].eq("Competitor")
    ].copy()

    for store_df in (own_stores, competitors):
        store_df["map_title"] = store_df["brand"]
        store_df["map_line_1"] = store_df["store_name"].fillna("")
        store_df["map_line_2"] = store_df["address_area"].fillna("")
        store_df["map_line_3"] = ""
        store_df["map_line_4"] = ""

    layers = []

    # Candidate opportunity markets
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=opportunity,
            get_position="[longitude, latitude]",
            get_radius="size",
            get_fill_color=ANTIQUE_ROSE,
            get_line_color=BURGUNDY,
            line_width_min_pixels=1,
            stroked=True,
            filled=True,
            pickable=True,
            opacity=0.82,
        )
    )

    # Existing Tanishq Group stores
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=own_stores,
            get_position="[longitude, latitude]",
            get_radius=135,
            get_fill_color=BRONZE,
            get_line_color=CREAM,
            line_width_min_pixels=2,
            stroked=True,
            filled=True,
            pickable=True,
            opacity=0.95,
        )
    )

    # Competitor stores
    if show_competitors:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=competitors,
                get_position="[longitude, latitude]",
                get_radius=90,
                get_fill_color=MUTED,
                get_line_color=CREAM,
                line_width_min_pixels=1,
                stroked=True,
                filled=True,
                pickable=True,
                opacity=0.55,
            )
        )

    tooltip = {
        "html": """
        <div style="
            font-family: Arial, sans-serif;
            padding: 8px;
            min-width: 210px;
        ">
            <div style="
                font-weight: 700;
                font-size: 15px;
                margin-bottom: 7px;
                color: #641C29;
            ">
                {map_title}
            </div>
            <div>{map_line_1}</div>
            <div>{map_line_2}</div>
            <div>{map_line_3}</div>
            <div>{map_line_4}</div>
        </div>
        """,
        "style": {
            "backgroundColor": "#FFFDF8",
            "color": "#3F3935",
            "border": "1px solid #D8CCBD",
        },
    }

    # Separate views are not necessary; one professional business map.
    view_state = pdk.ViewState(
        latitude=19.12,
        longitude=72.90,
        zoom=10.3,
        pitch=0,
        bearing=0,
    )

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light",
    )

    st.pydeck_chart(
        deck,
        use_container_width=True,
        height=570,
    )

    # ---------------------------------------------------------
    # LEGEND
    # ---------------------------------------------------------

    legend_cols = st.columns(3)

    with legend_cols[0]:
        st.markdown(
            '<span style="color:#641C29;font-size:18px;">●</span> '
            '<span style="color:#563448;">Tanishq Group stores</span>',
            unsafe_allow_html=True,
        )

    with legend_cols[1]:
        st.markdown(
            '<span style="color:#9A5C6B;font-size:18px;">●</span> '
            '<span style="color:#563448;">Priority opportunity markets</span>',
            unsafe_allow_html=True,
        )

    with legend_cols[2]:
        st.markdown(
            '<span style="color:#756B64;font-size:18px;">●</span> '
            '<span style="color:#563448;">Competitor stores</span>',
            unsafe_allow_html=True,
        )

    # ---------------------------------------------------------
    # OPPORTUNITY SUMMARY
    # ---------------------------------------------------------

    st.markdown('<div class="market-gap-heading">Priority Opportunity Markets</div>', unsafe_allow_html=True)

    summary = opportunity[
        [
            "location",
            "market_opportunity_score",
            "estimated_annual_sales_potential_cr",
            "network_gap_index",
            "competitor_presence_3km",
        ]
    ].copy()

    summary.columns = [
        "Location",
        "Opportunity Score",
        "Revenue Potential (₹ Cr)",
        "Network Gap",
        "Competitors (3 km)",
    ]

    st.dataframe(
        summary.style
        .format(
            {
                "Opportunity Score": "{:.1f}",
                "Revenue Potential (₹ Cr)": "{:.1f}",
                "Network Gap": "{:.0f}",
                "Competitors (3 km)": "{:.0f}",
            }
        )
        .set_properties(**{"text-align": "center"}),
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("How Is the Market Gap Map Calculated?"):
        st.write(
            "The map highlights candidate markets using a Market Opportunity "
            "Score created specifically for geographic screening. It combines "
            "revenue potential, network gap, customer spending, accessibility "
            "and competitor intensity."
        )
        st.write(
            "Existing store markers use only records classified as actual "
            "stores; market-reference rows are excluded from the map."
        )
        st.write(
            "The score is a screening indicator for identifying white-space "
            "markets. It is not a replacement for the Investment Planner's "
            "budget-based recommendation."
        )
