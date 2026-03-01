import subprocess
import re

PDK_PATH = "/home/yogesh/OpenLane/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice"

# We pick a "Strong" config: High VDDL (1.2V), Strong Drive (16u), Weak Latch (0.4u)
# If THIS fails, the model path or the pin order is the problem.
debug_netlist = f"""
.lib "{PDK_PATH}" tt
.temp 27

.subckt CLS VIN VDDH VOUT GND VDDL
* Drain Gate Source Bulk
X0 A   VIN GND  GND  sky130_fd_pr__nfet_01v8 w=2.4 l=0.15
X1 A   VIN VDDL VDDL sky130_fd_pr__pfet_01v8 w=2.4 l=0.15

* Input Differential Pair
X4 G   A   GND  GND  sky130_fd_pr__nfet_01v8 w=16.0 l=0.15
X6 H   VIN GND  GND  sky130_fd_pr__nfet_01v8 w=16.0 l=0.15

* Cross-Coupled Latch
X2 G   H   VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w=0.4 l=0.8
X7 H   G   VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w=0.4 l=0.8

* Output Buffer
X3 VOUT H   VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w=4.0 l=0.5
X5 VOUT H   GND  GND  sky130_fd_pr__nfet_g5v0d10v5 w=2.0 l=0.5

* Parasitics from Magic
C_P_H    H    GND 4.0f
C_P_G    G    GND 3.0f
C_P_VOUT VOUT GND 1.5f
.ends

VVDDL VDDL GND 1.2V
VVDDH VDDH GND 5.0V
VIN   VIN  GND PULSE(0 1.2V 2n 100p 100p 10n 20n)

X1 VIN VDDH VOUT GND VDDL CLS

* Force the latch to start in a known state
.nodeset v(X1.G)=5.0 v(X1.H)=0.0

.tran 10p 30n

.control
  run
  echo "--- NODE VOLTAGE CHECK AT 5ns (VIN should be HIGH) ---"
  print v(VIN)
  print v(X1.A)
  print v(X1.G)
  print v(X1.H)
  print v(VOUT)
  
  meas tran tplh trig v(VIN) val=0.6 rise=1 targ v(VOUT) val=2.5 rise=1
  quit
.endc
.end
"""

with open("debug_final.sp", "w") as f:
    f.write(debug_netlist)

print("🚀 Running One-Shot Debug Simulation...")
proc = subprocess.run(["ngspice", "-b", "debug_final.sp"], capture_output=True, text=True)

# Print the output so we can see the 'print' statements from SPICE
print(proc.stdout)