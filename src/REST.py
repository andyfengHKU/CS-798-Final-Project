import json
import requests
import sys
import time
from datetime import datetime
import csv
import numpy as np

from config import Config
from entropy import Entropy
from pca import PCA
import utils


class SimpleMonitor():

    # frequency of running _monitor function
    MONITOR_INTERVAL = 5
    # whether print debug info
    DEBUG_PRINT = False

    FILE_PRINT = True

    def __init__(self, *args, **kwargs):
        self.datapaths = {}

        # store previous byte count for each flow
        self.previous_byte_count = {}
        # store previous package count for each flow
        self.previous_packet_count = {}
        self.previous_duration_sec = {}

        self.previous_rx_packet_count = {}
        self.previous_rx_byte_count = {}
        self.previous_rx_err_count = {}

        self.previous_tx_packet_count = {}
        self.previous_tx_byte_count = {}
        self.previous_tx_err_count = {}

        self.timestamp = datetime.now().strftime("%d-%H-%M-%S")

        # models
        self.entropy_model = Entropy()
        self.pca_model = PCA()

    def _get_dpids(self):
        url = 'http://localhost:8080/stats/switches'  #switches.
        handler = requests.get(url)
        self.datapaths = map(str,handler.json())
        #print self.datapaths

    def _monitor(self):
        while True:
            self._get_dpids()
            for dp in self.datapaths:
                self._request_stats(dp)
                self._port_stats_reply_handler(dp)
            time.sleep(SimpleMonitor.MONITOR_INTERVAL)


    def _request_stats(self, datapath):

        url = 'http://localhost:8080/stats/flow/' + datapath
        body = requests.get(url).json()[datapath]
        switch = Config.dpid2switch[int(datapath)]

        if SimpleMonitor.DEBUG_PRINT:
            print '-------------------------------------------------------------------------------'
            print '-------- ----------------- Flow Stat for Switch: ' + switch + ' ----------------- --------'
            print '-------------------------------------------------------------------------------'
            self._flow_print(body)

        cache = []

        for stat in sorted([flow for flow in body if flow['priority'] == 1],
                           key=lambda flow: (flow['match']['in_port'], flow['match']['dl_dst'])):

            in_port = stat['match']['in_port']
            eth_src = stat['match']['dl_src']
            eth_dst = stat['match']['dl_dst']
            out_port = stat['actions'][0].split(':')[1]

            # a flow is identified by this 5 tuple
            flow = (switch, eth_src, in_port, eth_dst, out_port)
            # calculate bit rate
            bit_rate = 0
            current_byte = stat['byte_count']
            if flow in self.previous_byte_count:
                bit_rate = utils.bit_rate(current_byte - self.previous_byte_count[flow], SimpleMonitor.MONITOR_INTERVAL)
            self.previous_byte_count[flow] = current_byte
            if bit_rate < 0: continue
            # calculate package rate
            packet_rate = 0
            current_packet = stat['packet_count']
            if flow in self.previous_packet_count:
                packet_rate = utils.packet_rate(current_packet - self.previous_packet_count[flow],
                                                SimpleMonitor.MONITOR_INTERVAL)
            self.previous_packet_count[flow] = current_packet
            if packet_rate < 0: continue

            duration = 0
            current_duration_sec = stat['duration_sec']
            if flow in self.previous_duration_sec:
                duration = current_duration_sec - self.previous_duration_sec[flow]
            else:
                duration = current_duration_sec
            self.previous_duration_sec[flow] = current_duration_sec
            if duration < 0: continue

            if SimpleMonitor.DEBUG_PRINT:
                print 'bit rate: ' + str(bit_rate) + ' packet rate: ' + str(packet_rate)

            cache.append([eth_src, in_port, eth_dst, out_port, duration, bit_rate, packet_rate])

        feature = self._compute_feature(cache)
        if SimpleMonitor.FILE_PRINT:
            self._feature_dump(switch, feature)
            # self._flow_dump(switch, cache)

        flows = []
        for row in cache:
            flows.append({
                'eth_src': row[0],
                'eth_dst': row[2],
                'packets': row[6] * SimpleMonitor.MONITOR_INTERVAL
            })
        entropy = self.entropy_model.compute_entropy(flows)
        print "=====================Entropy: " + str(entropy)

        # self._detect_attack(entropy,datapath,'entropy')

        # residual = self.pca_model.compute_residual(flows)
        # print "=====================Residual: " + str(residual)

        #self._detect_attack(entropy, dpid, 'entropy')

    '''
    Features:
    APf: average packets rate per flow
    MPf: maximum packet rate per flow
    ABf: average bits per packet per flow
    MBf: maximum bits per packet per flow
    ADf: average duration per flow
    MDf: maximum duration per flow
    PPf: percentage of Pair flows
    GSf: growth of single flows
    GDP: growth of different ports
    '''


    def _compute_feature(self, cache):
        # stat
        packets_rate = []
        bits_rate = []
        durations = []
        num_flows = 0
        num_pair_flows = 0
        pair_flows = {}
        ports = {}

        for item in cache:
            duration = item[4]
            bit_rate = item[5] * 1000.0
            packet_rate = item[6]
            # skip empty flow
            if bit_rate == 0 or packet_rate == 0: continue

            packets_rate.append(packet_rate)
            bits_rate.append(bit_rate / packet_rate)
            durations.append(duration)

            num_flows += 1
            # count for PPf & GSf
            src = item[0]
            dst = item[2]
            pair_flow = tuple(sorted([src, dst]))
            if pair_flow not in pair_flows:
                pair_flows[pair_flow] = 1
            else:
                pair_flows[pair_flow] += 1
            # count for GDP
            in_port = item[1]
            out_port = item[2]
            if in_port not in ports:
                ports[in_port] = 0
            else:
                ports[in_port] += 1

            if out_port not in ports:
                ports[out_port] = 0
            else:
                ports[out_port] += 1

        if len(packets_rate) == 0: return

        APf = np.median(packets_rate)
        MPf = np.max(packets_rate)

        ABf = np.median(bits_rate)
        MBf = np.max(bits_rate)

        ADf = np.median(durations)
        MDf = np.max(durations)

        for _, v in pair_flows.items():
            if v == 2: num_pair_flows += 1

        PPf = 2.0 * num_pair_flows / num_flows

        GSf = (num_flows - 2.0 * num_pair_flows) / SimpleMonitor.MONITOR_INTERVAL

        GDP = len(ports) * 1.0 / SimpleMonitor.MONITOR_INTERVAL

        features = [self._format(APf), self._format(MPf), self._format(ABf), \
                    self._format(MBf), self._format(ADf), self._format(MDf), \
                    self._format(PPf), self._format(GSf), self._format(GDP)]

        return features


    def _format(self, num):
        return "{:.2f}".format(num)


    def _feature_dump(self, switch, feature):
        if feature is None: return
        fname = '../data/' + self.timestamp + '-features-' + str(switch)
        with open(fname, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(feature)


    def _flow_dump(self, switch, cache):
        if len(cache) == 0: return
        saperater = [-1] * len(cache[0])
        fname = '../data/' + self.timestamp + '-flow-' + str(switch)
        with open(fname, 'a') as f:
            writer = csv.writer(f)
            for row in cache:
                writer.writerow(row)
            writer.writerow(saperater)



    def _port_stats_reply_handler(self, datapath):

        url = 'http://localhost:8080/stats/port/' + datapath
        body = requests.get(url).json()[datapath]
        switch = Config.dpid2switch[int(datapath)]

        cache = []
        for stat in sorted(body, key = lambda port: port['port_no']):
            port = (switch, stat['port_no'])
            # calculate receive bit rate
            rx_bit_rate = 0
            current_rx_byte = stat['rx_bytes']
            if port in self.previous_rx_byte_count:
                rx_bit_rate = utils.bit_rate(current_rx_byte - self.previous_rx_byte_count[port],
                                             SimpleMonitor.MONITOR_INTERVAL)
            self.previous_rx_byte_count[port] = current_rx_byte
            # calculate transmit bit rate
            tx_bit_rate = 0
            current_tx_byte = stat['tx_bytes']
            if port in self.previous_tx_byte_count:
                tx_bit_rate = utils.bit_rate(current_tx_byte - self.previous_tx_byte_count[port],
                                             SimpleMonitor.MONITOR_INTERVAL)
            self.previous_tx_byte_count[port] = current_tx_byte
            # calculate receive packet rate
            rx_packet_rate = 0
            current_rx_packet = stat['rx_packets']
            if port in self.previous_rx_packet_count:
                rx_packet_rate = utils.packet_rate(current_rx_packet - self.previous_rx_packet_count[port],
                                                   SimpleMonitor.MONITOR_INTERVAL)
            self.previous_rx_packet_count[port] = current_rx_packet
            # calculate transmit packet rate
            tx_packet_rate = 0
            current_tx_packet = stat['tx_packets']
            if port in self.previous_tx_packet_count:
                tx_packet_rate = utils.packet_rate(current_tx_packet - self.previous_tx_packet_count[port],
                                                   SimpleMonitor.MONITOR_INTERVAL)
            self.previous_tx_packet_count[port] = current_tx_packet
            # calculate receive err rate
            rx_err_rate = 0
            current_rx_err = stat['rx_errors']
            if port in self.previous_rx_err_count:
                rx_err_rate = utils.err_rate(current_rx_err - self.previous_rx_err_count[port],
                                             SimpleMonitor.MONITOR_INTERVAL)
            self.previous_rx_err_count[port] = current_rx_err
            # calculate transmit err rate
            tx_err_rate = 0
            current_tx_err = stat['tx_errors']
            if port in self.previous_tx_err_count:
                tx_err_rate = utils.err_rate(current_tx_err - self.previous_tx_err_count[port],
                                             SimpleMonitor.MONITOR_INTERVAL)
            self.previous_tx_err_count[port] = current_tx_err

            if SimpleMonitor.FILE_PRINT:
                cache.append([rx_bit_rate, rx_packet_rate, rx_err_rate, tx_bit_rate, tx_packet_rate, tx_err_rate])

        # if SimpleMonitor.FILE_PRINT:
        #     self._port_dump(switch, cache)


    def _port_dump(self, switch, cache):
        fname = '../data/' + self.timestamp + '-port-' + str(switch)
        with open(fname, 'a') as f:
            writer = csv.writer(f)
            for row in cache:
                writer.writerow(row)

    def _detect_attack(self, value, _dpid, method):
        if method == 'entropy':

            if value > 0.7:
                self._drop_attacker_traffic(_dpid, '00:00:00:00:00:04') #add src_IP of the attacker.

            print "=====================Entropy: " + str(value)

        elif method == 'pca':
            print "=====================Residual: " + str(value)

        elif method == 'svm':
            pass

        # return flag, victim_IP, attackers_IP

    def _drop_attacker_traffic(self, datapath, src):
        url = 'http://localhost:8080/stats/flowentry/add'

        rule = {'dpid': int(datapath),
                "priority": 44444,
                "table_id": 0,
                'match':{'dl_src':src},
                'instructions':[]}
        handler = requests.post(url, json=rule)

def main():

    MONITOR_INTERVAL = 5
    monitor = SimpleMonitor()
    monitor._monitor()

if __name__ == '__main__':
    main()


