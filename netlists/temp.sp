
.lib "/home/yogesh/OpenLane/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" ff
.temp 100

* 1. Input Inverter
X0 A VIN GND GND sky130_fd_pr__nfet_01v8 w=0.6 l=0.2
X1 A VIN VDDL VDDL sky130_fd_pr__pfet_01v8 w=0.6 l=0.2

* 2. Pull-Down Network (CORRECTED)
* Drain Gate Source Bulk
X4 G A GND GND sky130_fd_pr__nfet_01v8 w=4.0 l=0.15
X6 H VIN GND GND sky130_fd_pr__nfet_01v8 w=4.0 l=0.15

* 3. Cross-Coupled Latch (CORRECTED)
* Drain Gate Source Bulk
X2 G H VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w=1 l=0.8
X7 H G VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w=1 l=0.8

* 4. Output Buffer
X3 VOUT H VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w=5.0 l=0.5
X5 VOUT H GND GND sky130_fd_pr__nfet_g5v0d10v5 w=2 l=0.5

VVDDL VDDL 0 1.2V
VVDDH VDDH 0 3.3V
VIN VIN 0 PULSE(0 1.2 1n 1n 1n 5n 10n)

.tran 0.1n 50n

.control
  run
  * Trigger at 50% of VDDL, Target at 50% of VDDH
  meas tran dly trig v(VIN) val=0.6 rise=1 targ v(VOUT) val=1.65 rise=1
  meas tran pwr avg "@vvddh[i]" from 1n to 10n
  quit
.endc
.end
