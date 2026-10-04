import streamlit as st

from market_explorer import show_market_explorer
from investment_planner import show_investment_planner
from location_comparator import show_location_comparator
from market_gap_map import show_market_gap_map


# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="Tanishq Location Expansion",
    page_icon="◆",
    layout="wide"
)


# =========================================================
# ORIGINAL PREMIUM BRAND UI
# =========================================================


st.markdown("""

<style>

@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Source+Sans+3:wght@400;500;600;700&display=swap');


:root {
    --burgundy: #641C29;
    --deep-burgundy: #541521;
    --plum: #563448;

    --antique-rose: #A66A78;
    --rustique-rose: #F3E3E6;
    --bronze: #9B6A45;
    --gold: #B68A55;

    --cream: #FBF8F3;
    --ivory: #FFFDF9;

    --border: #D9D0C7;

    --text: #403A37;
    --muted: #817770;
}


/* =========================================================
   PAGE
========================================================= */

.stApp {
    background: var(--cream) !important;
    background-color: var(--cream) !important;
    color: var(--text);
}

.block-container {
    max-width: 1400px;
    padding-top: 1.8rem;
    padding-bottom: 1.8rem;
}


/* =========================================================
   MAIN TITLE
========================================================= */

h1 {
    font-family: 'Libre Baskerville', serif !important;

    color: var(--burgundy) !important;

    text-align: center !important;

    font-size: 2.35rem !important;

    font-weight: 700 !important;

    letter-spacing: -0.8px;

    margin-top: 0 !important;
    margin-bottom: 0 !important;
}


/* =========================================================
   SECTION HEADINGS
========================================================= */

h2 {
    font-family: 'Libre Baskerville', serif !important;

    color: var(--plum) !important;

    text-align: center !important;

    font-size: 1.34rem !important;

    font-weight: 700 !important;

    letter-spacing: -0.2px;

    margin-top: 1.15rem !important;
    margin-bottom: 0.8rem !important;

    padding-bottom: 0 !important;
}

h2::after {
    display: none !important;
}


/* =========================================================
   MAIN TITLE DIVIDER
========================================================= */

hr {
    border: none !important;

    border-top: 1px solid var(--bronze) !important;

    opacity: 0.45;

    width: 42px;

    margin: 0.25rem auto 0.9rem auto !important;
}



/* =========================================================
   NAVIGATION TABS
========================================================= */

/* =========================================================
   NAVIGATION TABS — FOUR EQUAL CENTRED SECTIONS
========================================================= */

div[data-testid="stTabs"] {
    width: 100% !important;
}

div[data-testid="stTabs"] [role="tablist"] {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    width: 100% !important;
    gap: 0 !important;
    border-bottom: 1px solid var(--border) !important;
}

div[data-testid="stTabs"] [role="tab"] {
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
    justify-content: center !important;
    text-align: center !important;
    display: flex !important;
    align-items: center !important;
    padding: 0.55rem 0.5rem !important;
    color: var(--plum) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--burgundy) !important;
    font-weight: 600 !important;
}

div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: var(--bronze) !important;
    height: 2px !important;
}

/* =========================================================
   SELECT LABELS
========================================================= */

label {
    color: var(--plum) !important;

    font-family: 'Source Sans 3', sans-serif !important;

    font-size: 12px !important;

    font-weight: 600 !important;

    text-align: center !important;

    width: 100%;
}


/* =========================================================
   SELECT BOX
========================================================= */

div[data-baseweb="select"] > div {

    border: 1px solid var(--border) !important;

    border-radius: 5px !important;

    min-height: 42px !important;

    background: var(--ivory) !important;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.8) !important;
}



/* =========================================================
   CENTRED LOCATION / FORMAT CONTROLS
========================================================= */

div[data-testid="stSelectbox"] {
    max-width: 390px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

div[data-testid="stSelectbox"] label {
    color: var(--plum) !important;
    text-align: center !important;
    justify-content: center !important;
    width: 100% !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] {
    width: 100% !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: var(--ivory) !important;
    background-color: var(--ivory) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    min-height: 44px !important;
    box-shadow: 0 2px 7px rgba(70,45,30,0.04) !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
    border-color: var(--bronze) !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
    border-color: var(--bronze) !important;
    box-shadow: 0 0 0 1px var(--bronze) !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] * {
    background-color: transparent !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] input {
    color: var(--text) !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] svg {
    color: var(--plum) !important;
    fill: var(--plum) !important;
}

/* =========================================================
   PREMIUM METRIC CARDS
========================================================= */

div[data-testid="stMetric"] {

    position: relative;

    background: var(--ivory);

    border: 1px solid var(--border);

    border-top: 3px solid var(--bronze);

    border-radius: 9px;

    padding: 18px 14px 16px 14px;

    min-height: 100px;

    text-align: center;

    box-shadow:
        0 4px 12px rgba(90,60,45,0.055);

    overflow: hidden;
}


/* =========================================================
   REMOVE OLD CARD ACCENT
========================================================= */

div[data-testid="stMetric"]::before {
    display: none !important;
}


/* =========================================================
   CARD TITLE
========================================================= */

div[data-testid="stMetricLabel"] {

    width: 100% !important;

    display: flex !important;

    align-items: center !important;

    justify-content: center !important;

    text-align: center !important;

    color: var(--plum) !important;

    font-family: 'Source Sans 3', sans-serif !important;

    font-size: 12.5px !important;

    font-weight: 600 !important;

    letter-spacing: 0.15px;

    line-height: 1.2 !important;

    margin: 0 !important;

    padding: 0 !important;
}


/* Force Streamlit inner label container to centre */

div[data-testid="stMetricLabel"] > div {

    width: 100% !important;

    display: flex !important;

    justify-content: center !important;

    align-items: center !important;

    text-align: center !important;
}


/* Force label paragraph to centre */

div[data-testid="stMetricLabel"] p {

    width: 100% !important;

    margin: 0 !important;

    padding: 0 !important;

    text-align: center !important;

    color: var(--plum) !important;

    font-family: 'Source Sans 3', sans-serif !important;

    font-size: 13px !important;

    font-weight: 600 !important;
}


/* =========================================================
   CARD VALUE
========================================================= */

div[data-testid="stMetricValue"] {

    width: 100% !important;

    display: flex !important;

    justify-content: center !important;

    align-items: center !important;

    text-align: center !important;

    color: var(--burgundy) !important;

    font-family: 'Source Sans 3', sans-serif !important;

    font-size: 1.72rem !important;

    font-weight: 600 !important;

    letter-spacing: -0.3px;

    margin-top: 6px !important;
}


/* =========================================================
   REMOVE METRIC DELTAS
========================================================= */

div[data-testid="stMetricDelta"] {
    display: none !important;
}



/* =========================================================
   SECTION CAPTIONS
========================================================= */

div[data-testid="stCaptionContainer"],
div[data-testid="stCaptionContainer"] p,
.stCaption {
    color: var(--muted) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 12px !important;
    line-height: 1.4 !important;
    text-align: center !important;
    margin-top: -2px !important;
    margin-bottom: 8px !important;
}


/* =========================================================
   WHY THIS LOCATION
========================================================= */

div[data-testid="stAlert"] {

    background: var(--plum) !important;

    border: 1px solid rgba(182,138,85,0.28) !important;

    border-left: 4px solid var(--bronze) !important;

    border-radius: 9px !important;

    padding: 16px 28px !important;

    margin-top: 0.1rem !important;

    box-shadow:
        0 3px 10px rgba(70,45,30,0.045);
}


div[data-testid="stAlert"] p {

    color: #F6EFE5 !important;

    text-align: center !important;

    font-family: 'Source Sans 3', sans-serif !important;

    font-size: 14px !important;

    line-height: 1.55 !important;

    margin: 0 !important;
}


div[data-testid="stAlert"] svg {
    display: none !important;
}


/* =========================================================
   EXPANDER
========================================================= */

div[data-testid="stExpander"] {

    background: rgba(255,253,249,0.92) !important;

    border: 1px solid var(--border) !important;

    border-radius: 6px !important;

    margin-top: 0.65rem !important;

    box-shadow:
        0 1px 5px rgba(70,45,30,0.025);
}


div[data-testid="stExpander"] summary {

    justify-content: center !important;
}


div[data-testid="stExpander"] summary p {

    text-align: center !important;

    color: var(--plum) !important;

    font-family: 'Source Sans 3', sans-serif !important;

    font-size: 13px !important;

    font-weight: 600 !important;
}


div[data-testid="stExpander"] p {

    text-align: center !important;

    color: var(--text) !important;

    line-height: 1.55 !important;
}


/* =========================================================
   SPACING
========================================================= */

div[data-testid="stVerticalBlock"] {
    gap: 0.45rem;
}


/* =========================================================
   REMOVE HEADING LINK ICONS
========================================================= */

h1 a,
h2 a,
h3 a {
    display: none !important;

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.title("Tanishq Location Expansion")
st.markdown("---")


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Market Explorer",
    "Investment Planner",
    "Location Comparator",
    "Market Gap Map"
])


# =========================================================
# TAB 1
# =========================================================

with tab1:
    show_market_explorer()


# =========================================================
# TAB 2
# =========================================================

with tab2:
    show_investment_planner()


# =========================================================
# TAB 3
# =========================================================

with tab3:
    show_location_comparator()


# =========================================================
# TAB 4
# =========================================================

with tab4:
    show_market_gap_map()
