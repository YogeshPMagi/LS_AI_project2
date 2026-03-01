* Post-Layout Simulation for Level Shifter with Power and Delay Analysis
.lib "/home/yogesh/OpenLane/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice" tt
.include CLS.spice

* --- Device Under Test (DUT) ---
X1 VIN VDDH VOUT 0 VDDL CLS

* --- Voltage Sources ---
VDDH VDDH 0 3.3V
VDDL VDDL 0 1.2V

* --- Input Signal: 1.2V Pulse ---
VIN VIN 0 pulse(0 1.2 1n 1n 1n 4n 10n)

* --- Simulation Settings ---
.tran 0.1n 50n

.control
* 1. Ensure current through voltage sources is recorded
save all
save @vddh[i] @vddl[i]

run

* 2. Create Instantaneous Power Vectors (Calculated before measurement)
* We use -i(vxxx) because SPICE defines current flowing into the source as positive
let p_h = v(vddh) * -i(vddh)
let p_l = v(vddl) * -i(vddl)
let p_total = p_h + p_l

* 3. Measure Propagation Delay (50% points)
meas tran t_plh trig v(VIN) val=0.6 rise=1 targ v(VOUT) val=1.65 rise=1
meas tran t_phl trig v(VIN) val=0.6 fall=1 targ v(VOUT) val=1.65 fall=1

* 4. Measure Rise and Fall Times (10% to 90% of 3.3V)
meas tran t_rise trig v(VOUT) val=0.33 rise=1 targ v(VOUT) val=2.97 rise=1
meas tran t_fall trig v(VOUT) val=2.97 fall=1 targ v(VOUT) val=0.33 fall=1

* 5. Measure Average Power over 5 cycles (0 to 50ns)
meas tran avg_p_vddh avg p_h from=0n to=50n
meas tran avg_p_vddl avg p_l from=0n to=50n

* 6. Calculations and Outputs
let avg_delay = (t_plh + t_phl) / 2
let total_avg_power = avg_p_vddh + avg_p_vddl
let pdp = total_avg_power * avg_delay

print avg_delay
print total_avg_power
print pdp

* 7. Visualization
plot v(VIN) v(VOUT)
plot p_total title 'Total Instantaneous Power (W)'

.endc
.end