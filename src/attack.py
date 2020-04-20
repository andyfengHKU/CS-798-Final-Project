import random
import time
import numpy as np

TIMEOUT = 5

class BasicAttacker:
    
    def __init__(self, victim, attacker, hosts):
        self.victim = victim # should be h1
        self.attacker = attacker # should be h4
        self.hosts = hosts
    
    # we can do multi thread if needed
    # but it cannot be terminated in mininet
    def normal_traffic(self):
        while True:
            random_host = self.hosts[random.randint(0, len(self.hosts)-1)]
            random_timeout = str(TIMEOUT)
            random_interval = str(random.uniform(0,0.1))
            ping_cmd = 'ping -w ' + random_timeout + ' -i ' +  random_interval + ' ' + self.victim.IP()
            random_host.cmd(ping_cmd)

    def ddos_traffic(self):

        time.sleep(5)
        #There will be regular traffic for normal_time and then the attack will take place.
        #the other host that are not malicious should be able to keep the communication.

        print "ddos"

        for host in self.hosts:
            spoof_ip = host.IP()
            ddos_cmd = 'hping3 --flood ' + self.victim.IP() + ' -a ' + spoof_ip + ' &'
            self.attacker.cmd(ddos_cmd)
            print ddos_cmd

        time.sleep(50)
        print("killing all.....")
        for host in self.hosts:
            spoof_ip = host.IP()
            ddos_cmd = 'kill $(jobs -p)'
            self.attacker.cmd(ddos_cmd)
            print ddos_cmd


        

class LargeAttacker:
    
    def __init__(self, victim, attacker, hosts, out_domain_host):
        self.victim = victim 
        self.attacker = attacker 
        self.hosts = hosts

        self.out_domain_host = out_domain_host

        self.num_sample = 3
    
    def normal_traffic(self):
        print "normal"
        while True:
            random_timeout = str(TIMEOUT)
            for i in range(self.num_sample):
                random_host = self.hosts[random.randint(0, len(self.hosts)-1)]
                random_interval = str(random.uniform(0,0.05))
                ping_cmd = 'ping -w ' + random_timeout + ' -i ' +  random_interval + ' ' + self.victim.IP() + ' &'
                random_host.cmd(ping_cmd)
            time.sleep(TIMEOUT)
    
    def ddos_traffic(self):
        print "ddos"
        for host in self.hosts:
            spoof_ip = host.IP()
            ddos_cmd = 'hping3 --flood ' + self.victim.IP() + ' -a ' + spoof_ip + ' &'
            self.attacker.cmd(ddos_cmd)
            print ddos_cmd
    
    # new type of ddos attack that attacks random victim
    # should only test in large topo
    def random_ddos_traffic(self):
        pass