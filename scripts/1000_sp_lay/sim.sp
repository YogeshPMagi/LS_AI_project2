
.lib "/home/yogesh/OpenLane/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.temp 27
.subckt CLS VIN VDDH VOUT GND VDDL
X0 A VIN GND GND sky130_fd_pr__nfet_01v8 ad=0.24 pd=2.0 as=0.24 ps=2.0 w=0.68 l=0.15
X1 A VIN VDDL VDDL sky130_fd_pr__pfet_01v8 ad=0.24 pd=2.0 as=0.24 ps=2.0 w=0.68 l=0.15
X2 G H VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 ad=1.6 pd=4.8 as=1.6 ps=4.8 w=0.98 l=0.9
X7 VDDH G H VDDH sky130_fd_pr__pfet_g5v0d10v5 ad=1.6 pd=4.8 as=1.6 ps=4.8 w=0.98 l=0.9
X4 G A GND GND sky130_fd_pr__nfet_01v8 ad=1.2 pd=8.6 as=1.2 ps=4.6 w=13.39 l=0.15
X6 GND VIN H GND sky130_fd_pr__nfet_01v8 ad=1.2 pd=4.6 as=1.2 ps=8.6 w=13.39 l=0.15
X3 VOUT H VDDH VDDH sky130_fd_pr__pfet_g5v0d10v5 ad=3 pd=11 as=3 ps=11 w=1.18 l=0.9
X5 VOUT H GND GND sky130_fd_pr__nfet_g5v0d10v5 ad=1.2 pd=5 as=1.2 ps=5 w=1.18 l=0.9
.ends
X1 VIN VDDH VOUT GND VDDL CLS
VVDDH VDDH GND 5.0V
VVDDL VDDL GND 1.8V
VIN VIN GND pulse(0 1.8 1n 1n 1n 4n 10n)
.tran 0.1n 50n
.control
  run
  let p_total = (v(VDDH) * -VVDDH#branch) + (v(VDDL) * -VVDDL#branch)
  meas tran t_plh trig v(VIN) val=0.9 rise=1 targ v(VOUT) val=2.5 rise=1
  meas tran t_phl trig v(VIN) val=0.9 fall=1 targ v(VOUT) val=2.5 fall=1
  meas tran avg_pwr avg p_total from=0n to=50n
  print t_plh t_phl avg_pwr
  quit
.endc
.end
