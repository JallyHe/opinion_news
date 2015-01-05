#!/bin/bash
# User: linhaobuaa
# Date: 2015-01-05 20:00:00
# Version: 0.1.0
# 子事件演化聚类跑一天

for i in {1..24}
do
   # echo "Welcome $i times"
   python run.py >> run.log
done
