
#!/bin/bash

for file
do
    #echo "$file"
    ofile=`echo "$file" | awk -F "." '{print $1"-weixinip.txt"}'`
    ofile1=`echo "$file" | awk -F "." '{print $1"-weixin.txt"}'`
    ./parse_weixin_ip.py "$file" > "$ofile"
    cat "$ofile" | sort | uniq > "$ofile1"
    #weixinfile=`echo "$file" | awk -F "." '{print $1"-weixin.pcap"}'`
    #echo $weixinfile
    #/usr/bin/python pure_weixin_pcap.py "$ofile1" "$file" "$weixinfile"
    rm "$ofile"
done
