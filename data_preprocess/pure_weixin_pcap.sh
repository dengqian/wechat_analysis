#!/bin/bash

for file
do
    ipfile=`echo "$file" | awk -F "." '{print $1"-weixin.txt"}'`
    outfile=`echo "$file" | awk -F "." '{print $1"-weixin.pcap"}'`
    /usr/bin/python pure_weixin_pcap.py /home/data/3G/long_conn_ip.txt "$ipfile" "$file" "$outfile"
    #echo $ipfile
done
