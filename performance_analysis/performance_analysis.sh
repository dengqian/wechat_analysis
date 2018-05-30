#!/bin/bash

# for file
# do
#     ofile=`echo "$file" | awk -F '.' '{print $1"-performance-info.txt"}'`
#     # echo "$ofile"
#     /usr/bin/python performance_analysis.py /home/data/3G/weixin_server_ip.txt \
#         /home/data/3G/long_conn_ip.txt "$file" > "$ofile"
# done
/usr/bin/python performance_analysis.py /home/data/3G/all_weixin_server_ip.txt \
    /home/data/3G/flow_type.txt /home/data/3G/long_conn_ip.txt "$@" 
