# CS-798-Final-Project
Source code for CS 798 Final Project "A comprehensive study of DDoS Attacks Detection Scheme for SDN Environment"

## Installation
1. Download and install a fresh Ubuntu 18 in VM
2. Git clone this repo
3. Install mininet, Ryu and all dependencies by   
   `sudo ./install.sh`

## Run

1. Run the controller with  
   `./run_monitor.sh`  
   if you are using large topology also run another switch with  
   `./run_switch.sh`  
2. Run the RESTFUL API monitor with  
   `./run_mitigation.sh`  
   we support the following flags  
   - --mitigation
      - None: no mitigation will be run.
      - entropy: Entropy indicator will be used.
      - pca: PCA indicator will be used
      - svm : Machine Learning will be used. 
3. Run the topology with  
   `./run_topo.sh`  
   we support the following flags  
   - --topo
      - basic: basic topology
      - large: large topology
   - --traffic
      - empty: no traffic will be run
      - normal: normal ping traffic auto-run
      - ddos: ddos hping3 flood traffic auto-run
      - mix: first normal then ddos (loop)

#### Note

1. Monitor should be run at first
2. See the script `src/attack.py`for changin the attacker time of operation. 
3. For collecting data run the monitor without any mitigation strategy `--mitigation='None'` and run step 3 before step 2.
4. !!! mitigation.py line 136 is hard code for topology. Need to change when using large topo !!!


