#!/bin/bash

#ls /home/data/3G/2014-08-06\ 08* | while read file
#do /usr/bin/python decode_ppp.py "/home/data/3G/${file}" /home/data/3G/$

for file 
do
    #echo "$file"
    ofile=`echo "$file" |awk -F "." '{print $1"-pured.pcap"}'`
    #echo $ofile
    /usr/bin/python decode_ppp.py "$file" "$ofile"
    rm "$file"
done
