from mininet.net import Mininet
from mininet.node import CPULimitedHost, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class CustomTopology:

    def __init__(self):
        setLogLevel('info')

    # ##########################    
    # basic topo for testing
    # ONOS Controller
    #   
    #  s1  --  s2
    #  /\      /\
    # h1 h2   h3 h4
    # ##########################   
    def basic(self):
        net = Mininet(build=False, host=CPULimitedHost, link=TCLink)

        info('*** Add Controller (ONOS) ***\n')
        c1 = net.addController(name='c1', controller=RemoteController, ip='127.0.0.1', protocol='tcp', port=6633) # default port 6633

        info('*** Add Switches ***\n')
        switches = ['s1', 's2']
        s1, s2 = [net.addSwitch(s) for s in switches]

        info('*** Add Hosts ***\n')
        hosts = ['h1', 'h2', 'h3', 'h4']
        h1, h2, h3, h4 = [net.addHost(h) for h in hosts]

        info('*** Add Links ***\n')
        for s in [s1]:
            for h in [h1, h2]:
                net.addLink(s, h, bw=10) # we can modify delay, max_queue_size as well
        for s in [s2]:
            for h in [h3, h4]:
                net.addLink(s, h, bw=10)
        net.addLink(s1, s2)

        info('\n*** Build net ***\n')
        net.build()

        for c in net.controllers:
            c.start()
        
        net.start()

        net.staticArp()

        CLI(net)

        net.stop()

if __name__ == '__main__':
    customTopo = CustomTopology()
    customTopo.basic()