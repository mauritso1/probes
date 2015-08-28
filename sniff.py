from scapy.all import *
import airoiv.scapy_ex

def print_info(packet):
    if packet.haslayer(Dot11ProbeReq) and packet.info is not '':
        try:
            print 'Mac: ' + packet.addr1 + ' / ' + packet.addr2 + ' / ' + packet.addr3 + ' | Signal Strength: ' + str(packet.dBm_AntSignal) + ' | SSID: ' + packet.info + ' | Channel: ' + str(packet.Channel)
        except:
            print 'no addr1/dBm_AntSignal'
    return

packets = sniff(prn=lambda x: print_info(x))

