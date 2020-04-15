from operator import attrgetter

import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

from datetime import datetime
import csv

from config import Config
from entropy import Entropy
import utils


class SimpleMonitor(simple_switch_13.SimpleSwitch13):
    # frequency of running _monitor function
    MONITOR_INTERVAL = 2
    # whether print debug info
    DEBUG_PRINT = False
    
    FILE_PRINT = True

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

        # store previous byte count for each flow
        self.previous_byte_count = {}
        # store previous package count for each flow
        self.previous_packet_count = {}

        self.previous_rx_packet_count = {}
        self.previous_rx_byte_count = {}
        self.previous_rx_err_count = {}

        self.previous_tx_packet_count = {}
        self.previous_tx_byte_count = {}
        self.previous_tx_err_count = {}

        self.timestamp = datetime.now().strftime("%d-%H-%M-%S")

        # models
        self.entropy_model = Entropy()

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(SimpleMonitor.MONITOR_INTERVAL)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    # TODO: feature engineering for SVM
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        # get monitored switch
        dpid = int(ev.msg.datapath.id)
        switch = Config.dpid2switch[dpid]

        if SimpleMonitor.DEBUG_PRINT:
            print '-------------------------------------------------------------------------------'
            print '-------- ----------------- Flow Stat for Switch: ' + switch + ' ----------------- --------'
            print '-------------------------------------------------------------------------------'
            self._flow_print(body)
        
        cache = []
        for stat in sorted([flow for flow in body if flow.priority == 1], key=lambda flow: (flow.match['in_port'], flow.match['eth_dst'])):
            in_port = stat.match['in_port']
            eth_src = stat.match['eth_src']
            eth_dst = stat.match['eth_dst']
            out_port = stat.instructions[0].actions[0].port
            duration_sec = stat.duration_sec
            
            # a flow is identified by this 5 tuple
            flow = (switch, eth_src, in_port, eth_dst, out_port)
            # calculate bit rate
            bit_rate = 0
            current_byte = stat.byte_count
            if flow in self.previous_byte_count:
                bit_rate = utils.bit_rate(current_byte - self.previous_byte_count[flow], SimpleMonitor.MONITOR_INTERVAL)
            self.previous_byte_count[flow] = current_byte
            # calculate package rate
            packet_rate = 0
            current_packet = stat.packet_count
            if flow in self.previous_packet_count:
                packet_rate = utils.packet_rate(current_packet - self.previous_packet_count[flow], SimpleMonitor.MONITOR_INTERVAL)
            self.previous_packet_count[flow] = current_packet

            if SimpleMonitor.DEBUG_PRINT:
                print 'bit rate: ' + str(bit_rate) + ' packet rate: ' + str(packet_rate)

            cache.append([eth_src, in_port, eth_dst, out_port, duration_sec, bit_rate, packet_rate])
        
        if SimpleMonitor.FILE_PRINT:
            self._flow_dump(switch, cache)
        
        flows = []
        for row in cache:
            flows.append({
                'eth_src': row[0],
                'eth_dst': row[2],
                'packets': row[5] * SimpleMonitor.MONITOR_INTERVAL
            })
        entropy = self.entropy_model.get_entropy(flows)
        print "**************" + str(entropy)
    
    def _flow_dump(self, switch, cache):
        fname = '../data/' + self.timestamp + '-flow-' + str(switch)
        with open(fname, 'a') as f:
            writer = csv.writer(f)
            for row in cache:
                writer.writerow(row)
                
    def _flow_print(self, body):
        self.logger.info('in-port        eth-src          eth-dst      '
                         'out-port packets  bytes')
        self.logger.info('-------- ----------------- ----------------- '
                         '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            self.logger.info('%8x %17s %17s %8x %8d %8d',
                             stat.match['in_port'], stat.match['eth_src'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)
        

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
        # get monitored switch
        dpid = int(ev.msg.datapath.id)
        switch = Config.dpid2switch[dpid]

        if SimpleMonitor.DEBUG_PRINT:
            print '-------------------------------------------------------------------------------'
            print '-------- ----------------- Port Stat for Switch: ' + switch + ' ----------------- --------'
            print '-------------------------------------------------------------------------------'
            self._port_print(body)
        
        cache = []
        for stat in sorted(body, key=attrgetter('port_no')):
            port = (switch, stat.port_no)
            # calculate receive bit rate
            rx_bit_rate = 0
            current_rx_byte = stat.rx_bytes
            if port in self.previous_rx_byte_count:
                rx_bit_rate = utils.bit_rate(current_rx_byte - self.previous_rx_byte_count[port], SimpleMonitor.MONITOR_INTERVAL)
            self.previous_rx_byte_count[port] = current_rx_byte
            # calculate transmit bit rate
            tx_bit_rate = 0
            current_tx_byte = stat.tx_bytes
            if port in self.previous_tx_byte_count:
                tx_bit_rate = utils.bit_rate(current_tx_byte - self.previous_tx_byte_count[port], SimpleMonitor.MONITOR_INTERVAL)
            self.previous_tx_byte_count[port] = current_tx_byte
            # calculate receive packet rate
            rx_packet_rate = 0
            current_rx_packet = stat.rx_packets
            if port in self.previous_rx_packet_count:
                rx_packet_rate = utils.packet_rate(current_rx_packet - self.previous_rx_packet_count[port], SimpleMonitor.MONITOR_INTERVAL)
            self.previous_rx_packet_count[port] = current_rx_packet
            # calculate transmit packet rate
            tx_packet_rate = 0
            current_tx_packet = stat.tx_packets
            if port in self.previous_tx_packet_count:
                tx_packet_rate = utils.packet_rate(current_tx_packet - self.previous_tx_packet_count[port], SimpleMonitor.MONITOR_INTERVAL)
            self.previous_tx_packet_count[port] = current_tx_packet
            # calculate receive err rate
            rx_err_rate = 0
            current_rx_err = stat.rx_errors
            if port in self.previous_rx_err_count:
                rx_err_rate = utils.err_rate(current_rx_err - self.previous_rx_err_count[port], SimpleMonitor.MONITOR_INTERVAL)
            self.previous_rx_err_count[port] = current_rx_err
            # calculate transmit err rate
            tx_err_rate = 0
            current_tx_err = stat.tx_errors
            if port in self.previous_tx_err_count:
                tx_err_rate = utils.err_rate(current_tx_err - self.previous_tx_err_count[port], SimpleMonitor.MONITOR_INTERVAL)
            self.previous_tx_err_count[port] = current_tx_err

            if SimpleMonitor.FILE_PRINT:
                cache.append([rx_bit_rate, rx_packet_rate, rx_err_rate, tx_bit_rate, tx_packet_rate, tx_err_rate])
        
        if SimpleMonitor.FILE_PRINT:
            self._port_dump(switch, cache)
    
    def _port_dump(self, switch, cache):
        fname = '../data/' + self.timestamp + '-port-' + str(switch)
        with open(fname, 'a') as f:
            writer = csv.writer(f)
            for row in cache:
                writer.writerow(row)
    
    def _port_print(self, body):
        self.logger.info('port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('-------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%8x %8d %8d %8d %8d %8d %8d',
                             stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)
