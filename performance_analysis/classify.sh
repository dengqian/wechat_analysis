#!/bin/bash

awk '{print $18}' xiaoxi.txt > finish_time_xiaoxi.txt 
awk '{print $18}' mmsns.txt > finish_time_mmsns.txt 
awk '{print $18}' weixinnum.txt > finish_time_weixinnum.txt 
awk '{print $18}' short.txt > finish_time_short.txt 

# awk '{print $26}' xiaoxi.txt > data_bytes_xiaoxi.txt
# awk '{print $26}' mmsns.txt > data_bytes_mmsns.txt
# awk '{print $26}' weixinnum.txt > data_bytes_weixinnum.txt
# awk '{print $26}' short.txt > data_bytes_short.txt
awk '{print $9+$13}' xiaoxi.txt > data_bytes_xiaoxi.txt
awk '{print $9+$13}' mmsns.txt > data_bytes_mmsns.txt
awk '{print $9+$13}' weixinnum.txt > data_bytes_weixinnum.txt
awk '{print $9+$13}' short.txt > data_bytes_short.txt

awk '{print $7}' xiaoxi.txt >    pkt_cnt_xiaoxi.txt
awk '{print $7}' mmsns.txt >     pkt_cnt_mmsns.txt  
awk '{print $7}' weixinnum.txt > pkt_cnt_weixinnum.txt  
awk '{print $7}' short.txt >     pkt_cnt_short.txt
