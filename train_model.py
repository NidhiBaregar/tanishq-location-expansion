import os
import json
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_FILE = "candidate_locations.csv"

df = pd.read_csv(DATA_FILE)

print("\nDataset loaded successfully")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")


# ============================================================
# 2. DEFINE TARGET
# ============================================================

TARGET = "estimated_annual_sales_potential_cr"

if TARGET not in df.columns:
    raise ValueError(
        f"Target column '{TARGET}' not found in dataset."
    )


# ============================================================
# 3. DEFINE FEATURES
# ============================================================

FEATURES = [
    "population_3km",
    "household_income_proxy",
    "footfall_estimate_index",
    "competitor_presence_3km",
    "rental_cost_rs_sqft_month",
    "accessibility_index",
    "existing_tanishq_stores_3km",
    "existing_mia_stores_3km",
    "existing_zoya_stores_3km",
    "customer_spending_index",
    "network_gap_index",
    "cannibalisation_risk_index"
]


# Check that all features exist
missing_features = [
    col for col in FEATURES
    if col not in df.columns
]

if missing_features:
    raise ValueError(
        f"Missing feature columns: {missing_features}"
    )


# ============================================================
# 4. PREPARE X AND y
# ============================================================

X = df[FEATURES].copy()
y = df[TARGET].copy()

# Convert everything to numeric
X = X.apply(pd.to_numeric, errors="coerce")
y = pd.to_numeric(y, errors="coerce")

# Remove rows with missing values
valid_rows = X.notna().all(axis=1) & y.notna()

X = X.loc[valid_rows]
y = y.loc[valid_rows]

print(f"\nRows used for modelling: {len(X)}")


# ============================================================
# 5. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print(f"Training rows: {len(X_train)}")
print(f"Testing rows:  {len(X_test)}")


# ============================================================
# 6. TRAIN XGBOOST
# ============================================================

model = XGBRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42
)

model.fit(
    X_train,
    y_train
)


# ============================================================
# 7. TEST MODEL
# ============================================================

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(
    y_test,
    y_pred
) ** 0.5

r2 = r2_score(y_test, y_pred)


print("\n" + "=" * 50)
print("MODEL PERFORMANCE")
print("=" * 50)

print(f"MAE  : ₹{mae:.2f} Cr")
print(f"RMSE : ₹{rmse:.2f} Cr")
print(f"R²   : {r2:.3f}")

print("=" * 50)


# ============================================================
# 8. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "feature": FEATURES,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print("\nFEATURE IMPORTANCE")
print("=" * 50)

for _, row in importance.iterrows():
    print(
        f"{row['feature']:<35} "
        f"{row['importance']:.4f}"
    )


# ============================================================
# 9. SAVE MODEL
# ============================================================

MODEL_DIR = "models"

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

model_path = os.path.join(
    MODEL_DIR,
    "tanishq_sales_model.pkl"
)

joblib.dump(
    model,
    model_path
)


# ============================================================
# 10. SAVE FEATURE LIST
# ============================================================

feature_path = os.path.join(
    MODEL_DIR,
    "model_features.json"
)

with open(
    feature_path,
    "w"
) as f:

    json.dump(
        FEATURES,
        f,
        indent=4
    )


# ============================================================
# 11. SAVE TEST RESULTS
# ============================================================

test_results = X_test.copy()

test_results["actual_sales_cr"] = y_test.values
test_results["predicted_sales_cr"] = y_pred

test_results.to_csv(
    os.path.join(
        MODEL_DIR,
        "model_test_results.csv"
    ),
    index=False
)


print("\nModel saved successfully:")
print(model_path)

print("\nFeature list saved:")
print(feature_path)

print("\nTest predictions saved:")
print("models/model_test_results.csv")