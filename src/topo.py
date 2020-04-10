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
    # Ryu Controller
    #      s1
    #    /    \
    #  s11    s12
    #  /\      /\
    # h1 h2   h3 h4
    # ##########################   
    def basic(self):
        net = Mininet(build=False, host=CPULimitedHost, link=TCLink)

        info('*** Add Controller (ONOS) ***\n')
        c1 = net.addController(name='c1', controller=RemoteController, ip='127.0.0.1', protocol='tcp', port=6633) # default port 6633

        info('*** Add Switches ***\n')
        switches = ['s1', 's11', 's12']
        s1, s11, s12 = [net.addSwitch(s) for s in switches]

        info('*** Add Hosts ***\n')
        hosts = ['h1', 'h2', 'h3', 'h4']
        h1, h2, h3, h4 = [net.addHost(h) for h in hosts]

        info('*** Add Links ***\n')
        net.addLink(h1, s11, bw=10)
        net.addLink(h2, s11, bw=10)

        net.addLink(h3, s12, bw=10)
        net.addLink(h4, s12, bw=10)

        net.addLink(s11, s1, bw=10)
        net.addLink(s12, s1, bw=10)

        info('\n*** Build net ***\n')
        net.build()

        c1.start()
        for s in [s1, s11, s12]:
            s.start([c1])
        
        net.start()

        net.staticArp()

        CLI(net)

        net.stop()
    
    def large(self):
        pass


if __name__ == '__main__':
    customTopo = CustomTopology()
    customTopo.basic()