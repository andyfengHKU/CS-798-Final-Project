# return b/s 
def bit_rate(byte, interval):
    return byte * 8 / interval

def packet_rate(packet, interval):
    return packet / interval