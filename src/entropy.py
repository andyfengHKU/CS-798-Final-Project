import math
# untested class
class Entropy:

    def __init__(self):
        pass
    
    def compute_entropy(self, flows):
        total_traffic_S = 0.0
        total_od_pairs_N = 0.0
        od_pairs = {}
        for flow in flows:
            # print flow
            src = flow['eth_src']
            dst = flow['eth_dst']
            packets = float(flow['packets'])
            od_key = tuple(sorted((src, dst)))
            if od_key not in od_pairs:
                od_pairs[od_key] = packets
                total_od_pairs_N += 1.0
            else:
                od_pairs[od_key] += packets
            total_traffic_S += packets
        
        entropy = 0.0
        if total_traffic_S == 0: return entropy
        for _, ni in od_pairs.items():
            if ni == 0: continue
            entropy += - (ni / total_traffic_S) * math.log(ni / total_traffic_S, 2)
            
        return entropy
