---

# **LS-AI: Predictive Post-Layout Optimizer (SkyWater 130nm)**

## **🌟 Executive Summary**

In standard VLSI flows, parasitic-induced failures are discovered post-PEX, causing costly late-stage redesigns. **LS-AI** shifts performance discovery to the schematic phase. By training an AI "Digital Twin" on physics-infused synthetic data, it predicts **Post-Layout Delay and Power** directly from schematic sizing. This framework replaces brute-force SPICE sweeps, accelerating PPA (Power, Performance, Area) optimization by **2500x** and bypassing the six-figure OpEx of commercial EDA characterization tools.

---

## **🔥 System Architecture & Industrial Impact**

### **1\. "Layout-Less" PEX Awareness**

Standard ML models optimize ideal schematics. LS-AI optimizes for **Silicon Reality**.

* **Procedural Junctions:** Dynamically calculates diffusion capacitances (AD, PD, AS, PS) for every sizing candidate.  
* **Synthetic Interconnects:** Injects C\_wire and FO4 equivalent C\_load into the training netlists.  
* **Impact:** Eliminates the "Layout-Sim-Fail-Redraw" loop by predicting routing degradation *before* layout generation.

### **2\. Project Architecture**

![](https://github.com/YogeshPMagi/LS_AI_project2/blob/main/Images/project_arc.png)<br>

### **3\. Bifurcated Inference Pipeline (The XGBoost Engine)**

DCVSL level shifters suffer from non-linear contention. A standard regressor will hallucinate metrics for unstable circuits. LS-AI solves this with a two-stage pipeline:

* **Stage 1 \- The Gatekeeper (XGB-Classifier):** Predicts functional convergence. It strictly filters out candidates that fail due to PDK geometry limits (L\_min) or improper W\_n/W\_p drive-to-latch ratios.  
* **Stage 2 \- The Brain (Multi-Output XGB-Regressor):** Quantifies t\_pd(ps) and P\_avg(μW) **only** for stable designs.  
* **Why XGBoost?** Chosen over Neural Networks for its superior inference speed and higher accuracy (\>97%) on structured, tabular PDK data.

### **4.High-Dimensional Input Control**

The architecture of this AI engine is designed for **full design-space flexibility**. It is not limited to just "Voltage in/Voltage out" targets. Because the model is trained on a complete physical dataset, a user can input—and the AI can optimize—any of the following parameters simultaneously:

* **Geometry Control:** Manually override or let the AI suggest widths for **W\_IN, W\_DRIVE, W\_LATCH,** and **W\_OUT**.  
* **Physical Parasitics:** Input specific **AD/PD** (Area/Perimeter of Drain) values to simulate custom transistor layouts.  
* **Power Budgeting:** Set a hard limit on **Power (uW)** and let the AI find the fastest delay that stays under that cap.  
* **Load Adaptability:** Adjust the **Load Capacitance** (current baseline 15fF) to see how the design scales from driving a tiny flip-flop to a heavy global clock line.

### **5\. Radical Compute Economics**

Evaluates 1,000 design space points in **\~0.4 seconds**. It achieves on a standard laptop what traditionally requires a high-compute server farm running Monte Carlo simulations.


### **6.Final Result and Efficiency of Project**


![](https://github.com/YogeshPMagi/LS_AI_project2/blob/main/Images/Screenshot%202026-03-01%20231643.png)

This project delivers a **High-Dimensional Synthesis Engine** that transforms manual "trial-and-error" SPICE sweeps into **50ms AI inference**, resulting in a **10x increase in design efficiency**. By training on a **Parasitic-Aware** dataset, the tool incorporates silicon-level realities such as **Junction Capacitance (AD/PD)**,  **internal wire loads**, and  **fan-out loads**. This ensures the AI suggests robust, "Tape-out ready" configurations optimized for the **Sky130 PDK** rather than just theoretical schematics.

The final system successfully predicts complex metrics like the **Power-Delay Product (PDP)**—matching "Golden SPICE" results. The modular architecture allows engineers to input much more than just voltages; it acts as a multivariable synthesis engine where **transistor widths (W\_iN, W\_OUT), parasitics, and power budgets** are balanced simultaneously to find the global optimum.

---

## **🔮 Future Implementation:** 

* **PVT Corner Integration:** Expanding the model to guarantee yield across Process Corners (SS, TT, FF) and Temperature extremes (-4C to 125C).  
* **RL Optimization Agents:** Replacing grid search with Reinforcement Learning to navigate non-linear analog trade-off curves.  
* **Auto-GDSII Streaming:** Hooking inference outputs directly into **OpenLane** for automated physical layout generation---
