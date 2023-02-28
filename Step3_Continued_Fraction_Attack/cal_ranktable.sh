#!/bin/sh

a=0
choice=5
bitsize=16
for a in `seq 0 99`
do
  python3 cal_ranktable.py ${bitsize} ${choice} ${a}
done
