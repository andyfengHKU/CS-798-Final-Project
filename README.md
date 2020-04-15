# CS-798-Final-Project
Source code for CS 798 Final Project "A comprehensive study of DDoS Attacks Detection Scheme for SDN Environment"

## Installation
1. Download and install a fresh Ubuntu 18 in VM
2. Git clone this repo
3. Install mininet, Ryu and all dependencies by   
   `sudo ./install.sh`

## Run

#### For basic topology  
1. First run the monitor with
   `./run_monitor.sh`
2. Then create the topology with  
   `./run_topo.sh`

#### For large topology  
1. First run monitor and simple switch with  
   `./run_monitor.sh`  
   `./run_switch.sh`  
2. Then create the topology with  
   `./run_topo.sh --large` 

#### Note
1. topo should be run after monitor/switch
2. Attacker logic is under construction, it's not a good idea to run it now

