import time
import psutil

def main():
    old_value = 0    

    nic_min_mbps = float('inf')

    stats = psutil.net_if_stats()
    for x in stats:
        key = str(x)
        value = stats[key]

        if nic_min_mbps > value.speed:
            nic_min_mbps = value.speed

    print('min speed ', nic_min_mbps)

    while True:
        new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        if old_value:
            bw_mbps = convert_to_mbit(new_value - old_value)
            bw_kbps = convert_to_kbit(new_value - old_value)

            pc_mbps = 100.*bw_mbps / nic_min_mbps
            pc_kbps = 100.*bw_kbps / nic_min_mbps

            print("network usage mbps ", bw_mbps)
            print("network usage kbps ", bw_kbps)
            print("network percent ", pc_mbps)
            print("")
                
        old_value = new_value
        time.sleep(1)

def convert_to_gbit(value):
    return value/1024./1024./1024.*8

def convert_to_mbit(value):
    return value/1024./1024.*8

def convert_to_kbit(value):
    return value/1024.*8

def send_stat(value):
    print ("%0.3f" % convert_to_mbit(value))

main()