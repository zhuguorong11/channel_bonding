#coding:utf-8
# -*- coding:utf-8 -*-
import subprocess
import re
import time
import socket
import threading
essid = 'ath10k-test-ubuntu2'
password = '123456789a'
host = ('192.168.3.1','12306')
def auto_client():
    bandWidths = []
    #judge hether has this essid
    while True:
        flag = False
        p = subprocess.Popen('iwconfig', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out = p.stdout.read().decode('gbk')
        group = re.search(r'ath10k-test-ubuntu2', out)
        if group:
            print 'has this essid'
            # get bandwidth
            sub_p = subprocess.Popen('iw dev', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            sub_out = sub_p.stdout.read().decode('gbk')
            sub_group = re.search(r'channel (\d+) .+ width: (\d+) MHz', sub_out)
            if sub_group:
                curChannel = sub_group.group(1)
                curBandWidth = sub_group.group(2)
                bandWidths.append(curBandWidth)
                # print curChannel
                print 'current bandwidth: ',curBandWidth
            flag = True
        #has connect this essid
        if flag:
            time.sleep(1)
            continue
        #not connect,then we should scan list
        else:
            print 'not conncet this essid,scan this essid now'
            p_scan_list = subprocess.Popen('nmcli device wifi list', stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
            p_scan_list_out = p_scan_list.stdout.read().decode('utf8')
            group = re.search(r'ath10k-test-ubuntu2', p_scan_list_out)
            #this essid has in list
            if group:
                print 'find this essid,conncet it'
                connect = subprocess.Popen('nmcli device wifi connect '+ essid +' password '+ password, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                connect_out = connect.stdout.read().decode('gbk')
                print connect_out
            #this essid has no in list,we should wait for a while
            else:
                print 'not find this essid,wait for a moment'
                time.sleep(1)

auto_client()


# def auto_iperf():
#     p = subprocess.Popen('iperf3 -s', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#     out = p.stdout.read().decode('gbk')
#     print out
#
# myThread1 = threading.Thread(target=auto_client)
# myThread2 = threading.Thread(target=auto_iperf)
# myThread2.start()
# myThread1.start()
# myThread2.join()
# myThread1.join()