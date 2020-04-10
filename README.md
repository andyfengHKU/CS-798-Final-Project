# CS-798-Final-Project
Source code for CS 798 Final Project "A comprehensive study of DDoS Attacks Detection Scheme for SDN Environment"

## Current Setup
Use "sdn-vm.ova" in VirtualBox (mininet and onos already installed)  
Working with python2 (this maybe a problem when we use ML packages)  
!! Do not run installation !!

## Steps
1. Open "sdn-vm.ova" VM
2. Check your java version `java -version`  
   if your java version is not 11, `sudo update-alternatives --config java` choose 0 (java 11)
3. Start ONOS `/opt/onos/bin/onos-service`
4. Connect to ONOS service `ssh -p 8101 karaf@localhost` (password: karaf)  
   Currently I'm running the following apps (we may need others in future)  
   * org.onosproject.optical-model
   * org.onosproject.drivers
   * org.onosproject.hostprovider
   * org.onosproject.lldpprovider
   * org.onosproject.openflow-base
   * org.onosproject.openflow
   * org.onosproject.proxyarp
   * org.onosproject.fwd
5. 

