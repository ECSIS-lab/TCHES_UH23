#!/bin/bash


count=0
while [ $count -lt 100 ] ;
do
    python3 expblindkeygen.py 16 ${count} 

    (( count++ ))
done