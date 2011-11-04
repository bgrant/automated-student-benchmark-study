#! /usr/bin/env bash

for n in {1,2,3,4,5,6}
do
    echo "station_$n..."
    ./simple_grading.sh  /media/asb_share/stations/station_$n
    echo ""
done
