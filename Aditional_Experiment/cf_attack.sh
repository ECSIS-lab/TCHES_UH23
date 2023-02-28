#!/bin/bash
count=0
while [ $count -lt 100 ] ;
do
    python3 cf_attack.py ${count} 16 5 p
    sleep 0.01
    python3 cf_attack.py ${count} 16 5 q
    sleep 0.01
    (( count++ ))
done