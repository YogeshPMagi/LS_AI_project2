import subprocess
import os
import re
import csv
import random
import itertools

# --- PATH SETUP ---
current_dir = os.getcwd()
data_dir = os.path.join(current_dir, "data")
save_path = os.path.join(data_dir, "ls_random_10_audit.csv")
os.makedirs(data_dir, exist_ok=True)

PDK_PATH = "/home/yogesh/OpenLane/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice"

# --- RANGES ---
v_low_range   = [1.0, 1.2, 1.8]     
v_high_range  = [3.3, 5.0]        
w_in_range    = [0.6, 1.2, 2.4]      
w_drive_range = [4.0, 8.0, 12.0]  
w_latch_range = [0.4, 0.8]        
w_out_range   = [1.0, 2.0, 4.0]

all_combos = list(itertools.product(v_low_range, v_high_range, w_in_range, 
                                     w_drive_range, w_latch_range, w_out_range))

test_samples = random.sample(all_combos, 10)

# Master Template with corrected Port Mapping and Power Integration
master_template = """
.lib "{PDK_LIB}" tt
.temp 27
.subckt CLS VIN VDDH VOUT GND VDDL
* --- Input Inverter ---
X0 A VIN GND GND sky130_fd_pr__nfet_01v8 w={W_IN} l=0.15
X1 A VIN VDDL VDDL sky130_fd_pr__pfet_01v8 w={W_IN} l=0.15

* --- Pull Down Pair (Drain Gate Source Bulk) ---
X4 G A   GND GND sky130_fd_pr__nfet_01v8 w={W_DRIVE} l=0.15
X6 H VIN GND GND sky130_fd_pr__nfet_01v8 w={W_DRIVE} l=0.15

* --- Latch (Drain Gate Source Bulk) ---
X2 G H VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w={W_LATCH} l=0.8
X7 H G VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w={W_LATCH} l=0.8

* --- Output Stage ---
X3 VOUT H VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w={W_OUT} l=0.5
X5 VOUT H GND  GND  sky130_fd_pr__nfet_g5v0d10v5 w={W_OUT_N} l=0.5

* Parasitics
C_P_H    H    GND 4.0f
C_P_G    G    GND 3.0f
C_P_VOUT VOUT GND 1.5f
.ends

VVDDL VDDL GND {V_LOW}V
VVDDH VDDH GND {V_HIGH}V
VIN VIN GND PULSE(0 {V_LOW}V 2n 100p 100p 10n 20n)
X1 VIN VDDH VOUT GND VDDL CLS
C_LOAD VOUT GND 10f

.tran 10p 40n
.control
  run
  * Measure Delay
  meas tran tplh trig v(VIN) val={TH_LOW} rise=1 targ v(VOUT) val={TH_HIGH} rise=1
  meas tran tphl trig v(VIN) val={TH_LOW} fall=1 targ v(VOUT) val={TH_HIGH} fall=1
  
  * Measure Power: Avg Power and Total Energy from VDDH
  let pwr = v(VDDH) * -i(VVDDH)
  meas tran avg_pwr AVG pwr from=2n to=22n
  meas tran energy INTEG pwr from=2n to=22n
  
  quit
.endc
.end
"""

print(f"🎲 Running 10 Random Simulations with Power Measurement...")

with open(save_path, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["VDDL", "VDDH", "W_IN", "W_DRIVE", "W_LATCH", "W_OUT", "Delay_ps", "Avg_Power_uW", "Energy_fJ"])

    for i, (vl, vh, wi, wd, wl, wo) in enumerate(test_samples):
        th_low, th_high = vl/2, vh/2
        wo_n = wo / 2
        
        netlist = master_template.format(
            PDK_LIB=PDK_PATH, V_LOW=vl, V_HIGH=vh, 
            W_IN=wi, W_DRIVE=wd, W_LATCH=wl, W_OUT=wo, W_OUT_N=wo_n,
            TH_LOW=th_low, TH_HIGH=th_high
        )
        
        with open("temp_sim.sp", "w") as tmp: tmp.write(netlist)
        proc = subprocess.run(["ngspice", "-b", "temp_sim.sp"], capture_output=True, text=True)
        
        tplh = re.search(r"tplh\s*=\s*([0-9.eE+-]+)", proc.stdout)
        tphl = re.search(r"tphl\s*=\s*([0-9.eE+-]+)", proc.stdout)
        pwr  = re.search(r"avg_pwr\s*=\s*([0-9.eE+-]+)", proc.stdout)
        nrg  = re.search(r"energy\s*=\s*([0-9.eE+-]+)", proc.stdout)

        if tplh and tphl and pwr:
            avg_ps = ((float(tplh.group(1)) + float(tphl.group(1))) / 2) * 1e12
            pwr_uw = abs(float(pwr.group(1))) * 1e6
            energy_fj = abs(float(nrg.group(1))) * 1e15
            
            writer.writerow([vl, vh, wi, wd, wl, wo, avg_ps, pwr_uw, energy_fj])
            print(f"Test {i+1}: ✅ V={vl}V -> Delay: {avg_ps:.1f}ps | Power: {pwr_uw:.2f}uW")
        else:
            print(f"Test {i+1}: ❌ Failed (Contention or Mapping Error)")

print(f"\n✨ Results saved to: {save_path}")