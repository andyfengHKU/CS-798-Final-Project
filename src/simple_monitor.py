from operator import attrgetter

import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
import ryu.app.ofctl.api as ofctl_api
from ryu.lib import hub

from datetime import datetime
import csv
import numpy as np

from config import Config
from entropy import Entropy
from pca import PCA
import utils

#import matplotlib.pyplot as plt

class SimpleMonitor(simple_switch_13.SimpleSwitch13):
    # frequency of running _monitor function

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}

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


