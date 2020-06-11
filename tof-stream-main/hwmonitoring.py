import time
import psutil
from threading import Thread, Lock

'''
d_vu - add singleton class for hardware monitoring - 20190918
'''
class HardwareMonitoring(object):    
    __instance = None

    bw_mbps = 0    
    bw_network_usage = 0

    cpu_p = 0

    interval_nic = 1
    interval_cpu = 1
    
    nic_min_mbps = float('inf')

    @staticmethod
    def getInstance():
        if HardwareMonitoring.__instance == None:
            HardwareMonitoring()
        
        return HardwareMonitoring.__instance

    def __init__(self):
        self.start()

        HardwareMonitoring.__instance = self        
    
    def start(self):
        self.thread = Thread(target=self.hwUsage_Network, args=())
        self.thread.start()

        self.thread2 = Thread(target=self.hwUsage_Cpu, args=())
        self.thread2.start()

        return self    

    def hwUsage_Network(self):        
        self.nic_min_mbps = float('inf')

        stats = psutil.net_if_stats()
        for nic in stats:
            key = str(nic)
            value = stats[key]
            
            if self.nic_min_mbps > value.speed and value.speed > 0:
                self.nic_min_mbps = value.speed
        
        #print('from hwmonitoring.py - min NIC mbps ', nic_min_mbps)
        old_value = 0        
        while True:
            new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

            if old_value:
                self.bw_mbps = self.convert_to_mbit(new_value - old_value)
                self.bw_network_usage = 100. * self.bw_mbps / self.nic_min_mbps
            
            old_value = new_value
            time.sleep(self.interval_nic)        
        return
    
    def hwUsage_Cpu(self):
        #querry system-wide cpu usage after 1 second
        while True:            
            self.cpu_p = psutil.cpu_percent(1)                        
            time.sleep(self.interval_cpu)
        
        return

    def convert_to_mbit(self, value):
        return value/1024./1024.*8

