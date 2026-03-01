import subprocess
import re
import csv
import random
from concurrent.futures import ProcessPoolExecutor, as_completed

# --- CONFIGURATION ---
PDK_PATH = "/home/yogesh/OpenLane/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice"
SAVE_PATH = "ls_ai_realistic_1000.csv"
TOTAL_SAMPLES = 1000
MAX_WORKERS = 8 # Adjust based on your CPU threads

def run_single_sim(index):
    # Industry-Standard Stratified Sampling
    v_nodes = [0.8, 1.0, 1.2, 1.5, 1.8]
    vl = random.choice(v_nodes) if random.random() > 0.5 else round(random.uniform(0.7, 1.8), 2)
    vh = random.choice([3.3, 5.0])
    
    # Transistor Sizing
    wi = round(random.uniform(0.6, 2.4), 2)
    wd = round(random.uniform(4.0, 16.0), 2)
    wl = round(random.uniform(0.4, 1.2), 2)
    wo = round(random.uniform(1.0, 4.0), 2)
    
    # PDK Limit Check (2% fail rate for AI learning)
    l_val = 0.9 if random.random() > 0.02 else 0.8
    if l_val < 0.9:
        return [vl, vh, wi, wd, wl, wo, l_val, 0, 0, "FAIL", "PDK_LIMIT"]

    # NETLIST (Piped to RAM - Includes Junction + Wire + Load Parasitics)
    netlist = f"""
.lib "{PDK_PATH}" tt
.subckt CLS VIN VDDH VOUT GND VDDL
* Stage 1: Input Inverter (with Junction Parasitics)
X0 A VIN GND GND sky130_fd_pr__nfet_01v8 ad={wi*0.24} pd={wi+2.0} as={wi*0.24} ps={wi+2.0} w={wi} l=0.15
X1 A VIN VDDL VDDL sky130_fd_pr__pfet_01v8 ad={wi*0.24} pd={wi+2.0} as={wi*0.24} ps={wi+2.0} w={wi} l=0.15

* Stage 2: DCVSL Latch Core
X2 G H VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 ad={wl*1.6} pd={wl+4.8} as={wl*1.6} ps={wl+4.8} w={wl} l={l_val}
X7 VDDH G H VDDH sky130_fd_pr__pfet_g5v0d10v5 ad={wl*1.6} pd={wl+4.8} as={wl*1.6} ps={wl+4.8} w={wl} l={l_val}
X4 G A GND GND sky130_fd_pr__nfet_01v8 ad={wd*1.2} pd={wd+4.6} as={wd*1.2} ps={wd+4.6} w={wd} l=0.15
X6 GND VIN H GND sky130_fd_pr__nfet_01v8 ad={wd*1.2} pd={wd+4.6} as={wd*1.2} ps={wd+4.6} w={wd} l=0.15

* Stage 3: Output Stage
X3 VOUT H VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 ad={wo*3.0} pd={wo+11} as={wo*3.0} ps={wo+11} w={wo} l={l_val}
X5 VOUT H GND GND sky130_fd_pr__nfet_g5v0d10v5 ad={wo*1.2} pd={wo+5} as={wo*1.2} ps={wo+5} w={wo} l={l_val}

* --- INTERCONNECT & LOAD PARASITICS ---
C_INT_WIRE A GND 2fF  $ Fakes the metal routing track inside
C_LOAD VOUT GND 15fF $ Fakes the Fan-out load of the next gate
.ends

X1 VIN VDDH VOUT GND VDDL CLS
VVDDH VDDH GND {vh}V
VVDDL VDDL GND {vl}V
VIN VIN GND pulse(0 {vl} 1n 0.1n 0.1n 10n 20n)
.tran 0.1n 80n
.control
  run
  let p_total = (v(VDDH) * -VVDDH#branch) + (v(VDDL) * -VVDDL#branch)
  meas tran t_plh trig v(VIN) val={vl/2} rise=1 targ v(VOUT) val={vh/2} rise=1
  meas tran t_phl trig v(VIN) val={vl/2} fall=1 targ v(VOUT) val={vh/2} fall=1
  meas tran avg_pwr avg p_total from=5n to=45n
  print t_plh t_phl avg_pwr
  quit
.endc
.end
"""
    proc = subprocess.run(["ngspice", "-b"], input=netlist, capture_output=True, text=True)

    tplh_m = re.search(r"t_plh\s*=\s*([0-9.eE+-]+)", proc.stdout)
    tphl_m = re.search(r"t_phl\s*=\s*([0-9.eE+-]+)", proc.stdout)
    pwr_m  = re.search(r"avg_pwr\s*=\s*([0-9.eE+-]+)", proc.stdout)

    if tplh_m and tphl_m and pwr_m and "failed" not in tplh_m.group(1).lower():
        delay = ((float(tplh_m.group(1)) + float(tphl_m.group(1))) / 2) * 1e12
        p_uw = abs(float(pwr_m.group(1))) * 1e6
        # Filtering unrealistic artifacts
        if 5.0 < delay < 50000:
            return [vl, vh, wi, wd, wl, wo, l_val, round(delay, 2), round(p_uw, 2), "SUCCESS", "NONE"]
    
    return [vl, vh, wi, wd, wl, wo, l_val, 0, 0, "FAIL", "CONTENTION"]

if __name__ == "__main__":
    print(f"\n🚀 NITRO-REALITY ENGAGED | 1000 SAMPLES | PARASITIC AWARE")
    
    results = []
    successes = 0
    
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_sim = {executor.submit(run_single_sim, i): i for i in range(TOTAL_SAMPLES)}
        for i, future in enumerate(as_completed(future_to_sim)):
            res = future.result()
            results.append(res)
            if res[9] == "SUCCESS": successes += 1
            
            if (i + 1) % 50 == 0 or (i + 1) == TOTAL_SAMPLES:
                print(f"📊 Progress: {i+1}/1000 | Success Rate: { (successes/(i+1))*100:.1f}%")

    print(f"\n💾 Saving to {SAVE_PATH}...")
    with open(SAVE_PATH, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["VDDL", "VDDH", "W_IN", "W_DRIVE", "W_LATCH", "W_OUT", "L_VAL", "Delay_ps", "Power_uW", "Status", "Failure_Reason"])
        writer.writerows(results)
    print("✨ DONE!")