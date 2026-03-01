import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import os
from sklearn.preprocessing import StandardScaler

# --- SETTINGS ---
DATA_PATH = "../data/ls_ai_realistic_1000.csv"
MODEL_DIR = "../models/"
os.makedirs(MODEL_DIR, exist_ok=True)

# 1. DATA AUDIT: Watch the AI absorb the physics
print("📥 Phase 1: Absorbing CSV Data...")
df = pd.read_csv(DATA_PATH)
print(f"✅ Total Rows Absorbed: {len(df)}")

# Show a little bit of what it is learning
print("\n--- Absorption Sample ---")
print(df[['VDDL', 'VDDH', 'W_DRIVE', 'Status']].head(3))

# 2. SEPARATE LOGIC (Success vs. Performance)
features = ['VDDL', 'VDDH', 'W_IN', 'W_DRIVE', 'W_LATCH', 'W_OUT', 'L_VAL']
X = df[features]
y_status = (df['Status'] == 'SUCCESS').astype(int)

df_ok = df[df['Status'] == 'SUCCESS']
X_ok = df_ok[features]
y_perf = df_ok[['Delay_ps', 'Power_uW']]

# 3. SCALING
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_ok_scaled = scaler.transform(X_ok)

# 4. TRAINING: THE GATEKEEPER
print("\n🛡️  Phase 2: Training the Gatekeeper (PDK & Logic Limits)")
gatekeeper = xgb.XGBClassifier(n_estimators=100, max_depth=6, random_state=42)
gatekeeper.fit(X_scaled, y_status)

# 5. TRAINING: THE PERFORMANCE BRAIN
print("⚡ Phase 3: Training Performance Brain (Delay & Power)")
from sklearn.multioutput import MultiOutputRegressor
perf_brain = MultiOutputRegressor(xgb.XGBRegressor(n_estimators=200, max_depth=8, random_state=42))
perf_brain.fit(X_ok_scaled, y_perf)

# 6. EXPORT
joblib.dump(gatekeeper, os.path.join(MODEL_DIR, "gatekeeper.joblib"))
joblib.dump(perf_brain, os.path.join(MODEL_DIR, "perf_brain.joblib"))
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))

print("\n✨ TRAINING COMPLETE! Models saved in /models/ folder.")