#-*- coding:utf-8 –*-
import subprocess as sp
import time as ti
import re
import threading


def start_ap(band_width, chan_ind):
    print 'Band_width:      ',band_width
    print 'Channel_index:   ',chan_ind
    while True:
        if not IfEnable():
            break
    # IfEnable()

    comd = r'sudo /home/chenzhe/hostapd-2.6/hostapd/hostapd  /home/chenzhe/hostapd-2.6/hostapd/hostapd'+str(band_width)+'M'+str(chan_ind)+'.conf'
    p1 = sp.Popen(comd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    # print 'AP Enabled'
    while True:
        for line in iter(p1.stdout.readline, ''):
            print line
            group = re.search(r'AP-STA-CONNECTED (.+)', line)
            if group:
                # ti.sleep(1)
                p2 = sp.Popen('iperf3 -u -t 8 -c 192.168.3.3 -b 0', stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
                # print p2.stdout.read().decode('gbk')
                for sub_line in iter(p2.stdout.readline,''):
                    groups = re.search(r'(\d+.*\d+) Mbits/sec', sub_line)
                    if groups:
                        strs = groups.group(1).split('  ')
                        num = float(strs[-1].strip())
                        subThroughput.append(num)
                        # print num
                if len(subThroughput) != 0:
                    average = float(subThroughput[-1])
                    if str(band_width) == '80':
                        print 'band_width:', band_width, '    channel_id:', chan_ind, '     Throughput: ', average
                        all_dic[str(str(band_width) + '_' + str(chan_ind))] = min(average, all_dic[str(str(band_width) + '_' + str(chan_ind))])

                    else:
                        print 'band_width:',band_width,'    channel_id:',chan_ind,'     Throughput: ',average
                        all_dic[str(str(band_width)+'_'+str(chan_ind))] = max(average,all_dic[str(str(band_width)+'_'+str(chan_ind))])
                print 'Band:'+str(band_width)+'M Channel:'+str(chan_ind)
                break
        IfEnable()
        print 'AP was killed!'
        print '***************************************'
        print
        print '***************************************'
        break

def IfEnable():
    p1 = sp.Popen('ps -e |grep hostapd', stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    out1 = p1.stdout.read().decode('gbk')
    group1 = re.search(r'hostapd',out1)
    flag = 0
    if group1:
        # pid1 = group1.group(1)
        sp.Popen('pkill -9 hostapd', stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        flag = 1
    sp.Popen('sudo nmcli radio wifi off', stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    sp.Popen('sudo rfkill unblock wlan', stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    print flag
    return flag




all_dic = {'20_48': 0, '20_44': 0, '20_40': 0, '20_36': 0, '80_36': 1000000000, '40_36': 0, '40_44': 0}
list20 = [36,36]#40,40,44,44,48,48]
list40 = [36,36]#,44,44]
list80 = [36,36]
start_time = ti.time()
for band_width in [20,40,80]:
    subThroughput = []  # save throughput
    if band_width == 20:
        list = list20
    elif band_width == 40:
        list = list40
    else:
        list = list80
    for chan_id in list:
        start_ap(band_width,chan_id)
        with open('/home/chenzhe/data/data4/loca_'+str(band_width)+'.txt','a+') as f:
            for num in subThroughput:
                f.write(str(num))
                f.write(' ')
    # ti.sleep(10)
print all_dic
# list_sorted = sorted(all_dic.items(),key=lambda x : x[1])
# band_channel_out = list_sorted[-1]
# strs = band_channel_out[0].split('_')
# Throughput = band_channel_out[1]
if all_dic['80_36'] != 1000000000:
    list_sorted = sorted(all_dic.items(), key=lambda x: x[1])
    band_channel_out = list_sorted[-1]
    strs = band_channel_out[0].split('_')
    Throughput = band_channel_out[1]
    Throughput_80M = all_dic['80_36']
    gain = 100 * round((Throughput - Throughput_80M)/Throughput_80M,4)
else:
    del all_dic['80_36']
    list_sorted = sorted(all_dic.items(), key=lambda x: x[1])
    band_channel_out = list_sorted[-1]
    strs = band_channel_out[0].split('_')
    Throughput = band_channel_out[1]
    Throughput_40M = max(all_dic['40_36'],all_dic['40_44'])
    # gain = 100 * round((Throughput - Throughput_40M) / Throughput_40M, 4)
    gain = '无穷'
with open('/home/chenzhe/data/data4/gain.txt','a+') as f:
    f.write(str(gain))
    f.write(' ')
end_time = ti.time()
print '***************************************************************************'
print
print 'Result（结果）:'
print 'Chosen Bandwidth（选择带宽）:      ',strs[0],'MHz'
print 'Chosen Channel（选择信道）:        ',strs[1]
print 'Average Throughtput（平均吞吐量）:   ',Throughput,'Mbps','    the gain is（增益）:',gain,'%'
print 'Run Time:              ',end_time - start_time,'s'
print
print '***************************************************************************'

#use this bandwidth and channel

print '================================================start ap================================'
final_select_bandwidtch = strs[0]
final_select_channel = strs[1]
while True:
    if not IfEnable():
        break
comd = r'sudo /home/chenzhe/hostapd-2.6/hostapd/hostapd  /home/chenzhe/hostapd-2.6/hostapd/hostapd' + str(final_select_bandwidtch) + 'M' + str(final_select_channel) + '.conf'
p1 = sp.Popen(comd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
for line in iter(p1.stdout.readline, ''):
    print line

# for band_width in final_select_bandwidtch:
#     for channel in final_select_channel:
#         while True:
#             if not IfEnable():
#                 break
#         comd = r'sudo /home/chenzhe/hostapd-2.6/hostapd/hostapd  /home/chenzhe/hostapd-2.6/hostapd/hostapd' + str(band_width) + 'M' + str(channel) + '.conf'
#         p1 = sp.Popen(comd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
#         out = p1.stdout.read().decode('gbk')
#         print out