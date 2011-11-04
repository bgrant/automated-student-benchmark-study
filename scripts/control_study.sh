#! /usr/bin/env bash

if [ $# -ne 0 ]
then
    echo "usage: `basename $0` [-h]"
    echo """
An example of how to programatically generate 5 studies and distribute them to
the workstations.  Modify this to do what you want.

THIS WILL OVERWRITE EXISTING WORKSTATION DATA.  BACK UP DATA FIRST.

optional arguments:
  -h, --help            show this help message and exit
"""
    exit $E_BADARGS
fi

for n in {1,2,3,4,5,6}
do
    echo "Generating study for station_$n..."
    ./generate_study.py -dstation_$n t e f

    echo "Distributing study to station_$n..."
    ./distribute_study.py station_$n $n
done
