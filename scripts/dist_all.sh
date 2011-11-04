#! /usr/bin/env bash

for n in {1,2,3,4,5,6}
do
    echo "Distributing study to station_$n..."
    ./distribute_study.py station_$n $n
done
