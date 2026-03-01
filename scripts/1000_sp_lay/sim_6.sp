
.lib "/home/yogesh/OpenLane/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.subckt CLS VIN VDDH VOUT GND VDDL
X0 A VIN GND GND sky130_fd_pr__nfet_01v8 w=1.19 l=0.15
X1 A VIN VDDL VDDL sky130_fd_pr__pfet_01v8 w=1.19 l=0.15
X2 G H VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w=0.78 l=0.9
X7 VDDH G H VDDH sky130_fd_pr__pfet_g5v0d10v5 w=0.78 l=0.9
X4 G A GND GND sky130_fd_pr__nfet_01v8 w=5.12 l=0.15
X6 GND VIN H GND sky130_fd_pr__nfet_01v8 w=5.12 l=0.15
X3 VOUT H VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 w=3.84 l=0.9
X5 VOUT H GND GND sky130_fd_pr__nfet_g5v0d10v5 w=3.84 l=0.9
.ends
X1 VIN VDDH VOUT GND VDDL CLS
VVDDH VDDH GND 3.3V
VVDDL VDDL GND 1.2V
VIN VIN GND pulse(0 1.2 1n 0.1n 0.1n 10n 20n)
.tran 0.1n 80n
.control
  run
  let p_total = (v(VDDH) * -VVDDH#branch) + (v(VDDL) * -VVDDL#branch)
  meas tran t_plh trig v(VIN) val=0.6 rise=1 targ v(VOUT) val=1.65 rise=1
  meas tran t_phl trig v(VIN) val=0.6 fall=1 targ v(VOUT) val=1.65 fall=1
  meas tran avg_pwr avg p_total from=5n to=45n
  print t_plh t_phl avg_pwr
  quit
.endc
.end
