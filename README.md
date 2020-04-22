# CS-798-Final-Project
Source code for CS 798 Final Project "A comprehensive study of DDoS Attacks Detection Scheme for SDN Environment"

## Installation
1. Download and install a fresh Ubuntu 18 in VM
2. Git clone this repo
3. Install mininet, Ryu and all dependencies by   
   `sudo ./install.sh`

## Run

1. Run the monitor with  
   `./run_monitor.sh`  
   if you are using large topology also run another switch with  
   `./run_switch.sh`  
2. Run the topology with  
   `./run_topo.sh`  
   we support the following flags  
   - --topo
      - basic: basic topology
      - large: large topology
   - --traffic
      - empty: no traffic will be run
      - normal: normal ping traffic auto-run
      - ddos: ddos hping3 flood traffic auto-run
3. Run the Restful API with  
   `python REST.py` (I forget whether its python3 or not)

#### Note
1. Monitor should be run at first

