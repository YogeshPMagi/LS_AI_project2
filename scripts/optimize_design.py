import joblib
import numpy as np
import pandas as pd
import os
import warnings
import sys

# 1. SILENCE WARNINGS
warnings.filterwarnings("ignore", category=UserWarning)

# 2. PATHS & LOADING
MODEL_DIR = "../models/"
try:
    gatekeeper = joblib.load(os.path.join(MODEL_DIR, "gatekeeper.joblib"))
    perf_brain = joblib.load(os.path.join(MODEL_DIR, "perf_brain.joblib"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.joblib"))
except FileNotFoundError:
    print("❌ ERROR: Model files not found in ../models/. Please train the AI first!")
    sys.exit()

FEATURES = ['VDDL', 'VDDH', 'W_IN', 'W_DRIVE', 'W_LATCH', 'W_OUT', 'L_VAL']

def run_optimizer(vlow, vhigh, target_delay_ps):
    print(f"\n🔍 AI is searching for the lowest power design...")
    
    best_power = float('inf')
    best_config = None
    fastest_stable = float('inf')
    legal_count = 0

    # SEARCH SPACE
    w_in_range = [0.6, 1.2, 2.4]
    w_drive_range = [4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]
    w_latch_range = [0.6, 0.8, 1.0]
    w_out_range = [1.0, 2.0, 4.0]

    for wi in w_in_range:
        for wd in w_drive_range:
            for wl in w_latch_range:
                for wo in w_out_range:
                    input_df = pd.DataFrame([[vlow, vhigh, wi, wd, wl, wo, 0.9]], columns=FEATURES)
                    input_scaled = scaler.transform(input_df)
                    
                    is_legal = gatekeeper.predict(input_scaled)[0]
                    
                    if is_legal == 1:
                        legal_count += 1
                        perf = perf_brain.predict(input_scaled)
                        delay, power = perf[0][0], perf[0][1]
                        
                        if delay < fastest_stable:
                            fastest_stable = delay
                        
                        if delay <= target_delay_ps:
                            if power < best_power:
                                best_power = power
                                best_config = {
                                    'W_IN': wi, 'W_DRIVE': wd, 'W_LATCH': wl, 
                                    'W_OUT': wo, 'Delay_ps': delay, 'Power_uW': power
                                }

    if best_config:
        print(f"\n✅ OPTIMAL CONFIGURATION FOUND:")
        print(f"{'='*40}")
        for k, v in best_config.items():
            unit = "ps" if "Delay" in k else "uW" if "Power" in k else "um"
            print(f" {k:10}: {v:.2f} {unit}")
        print(f"{'='*40}")
    else:
        print(f"\n❌ NO DESIGN MET TARGET.")
        if fastest_stable != float('inf'):
            print(f"💡 Fastest stable design: {fastest_stable:.2f} ps.")
        else:
            print("⚠️ All designs failed contention. Try higher W_DRIVE.")

# --- INTERACTIVE TERMINAL INTERFACE ---
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"       ⚡ SKY130 LEVEL SHIFTER AI OPTIMIZER ⚡")
    print(f"{'='*60}")

    while True:
        try:
            print("\nEnter Specifications (or type 'exit' to quit):")
            v_in = input("🔹 Input Voltage (VDDL) [e.g. 1.2]: ")
            if v_in.lower() == 'exit': break
            
            v_out = input("🔹 Output Voltage (VDDH) [3.3 or 5.0]: ")
            target = input("🔹 Target Delay (ps) [e.g. 1000]: ")

            run_optimizer(
                vlow=float(v_in), 
                vhigh=float(v_out), 
                target_delay_ps=float(target)
            )
        except ValueError:
            print("❌ Invalid input. Please enter numbers only.")
        except KeyboardInterrupt:
            break

    print("\n👋 Optimizer closed. Happy Designing!")