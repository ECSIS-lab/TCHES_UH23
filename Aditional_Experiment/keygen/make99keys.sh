#!/bin/bash

keypath='../RSA2048key/'

count=1
while [ $count -lt 100 ] ;
do
    ./RSA2048keygen 2> ${keypath}key${count}.csv

    (( count++ ))
done